from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from rembg import remove
from PIL import Image, ImageOps
import io
from django.http import JsonResponse
from .models import UploadedImage

def home(request):
    images = UploadedImage.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'images': images})

def upload_image(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['image']
        UploadedImage.objects.create(image=uploaded_file)
        return redirect('home')
    return render(request, 'upload.html')

def process_image(request, pk):
    image = get_object_or_404(UploadedImage, pk=pk)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if image.processing_type:
            return JsonResponse({'error': 'Image already processed'}, status=400)
            
        action = request.POST.get('action')
        
        try:
            with Image.open(image.image.path) as img:
                if action == 'remove_bg':
                    processed = remove(img)
                    processing_type = 'bg_removed'
                elif action == 'remove_fg':
                    alpha = remove(img).getchannel('A')
                    inverted_alpha = ImageOps.invert(alpha)
                    img.putalpha(inverted_alpha)
                    processed = img
                    processing_type = 'fg_removed'
                else:
                    return JsonResponse({'error': 'Invalid action'}, status=400)

                img_io = io.BytesIO()
                processed.save(img_io, format='PNG')
                img_io.seek(0)
                
                image.image.save(
                    f'processed_{image.image.name}',
                    ContentFile(img_io.read()),
                    save=False
                )
                image.processing_type = processing_type
                image.save()

            return JsonResponse({'image_url': image.image.url})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'process.html', {'image': image})

def delete_image(request, pk):
    image = get_object_or_404(UploadedImage, pk=pk)
    image.delete()
    return redirect('home')
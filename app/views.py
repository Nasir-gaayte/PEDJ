from django.shortcuts import render, redirect, get_object_or_404
from .models import UploadedImage
from django.core.files.base import ContentFile
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import io
from django.http import JsonResponse

def home(request):
    images = UploadedImage.objects.all().order_by('-uploaded_at')
    return render(request, 'home.html', {'images': images})


def upload_image(request):
    if request.method == 'POST':
        image = request.FILES['image']
        uploaded_image = UploadedImage.objects.create(original_image=image)
        return redirect('edit_image', image_id=uploaded_image.id)
    return render(request, 'upload_image.html')


def edit_image(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        action = request.POST.get('action')

        if action in ['remove_bg', 'remove_fg']:
            try:
                # Process the original image
                with open(image.original_image.path, 'rb') as img_file:
                    input_image = img_file.read()
                    result = remove(input_image)
                    img_with_no_bg = Image.open(io.BytesIO(result))

                    if action == 'remove_bg':
                        # Save the background-removed image
                        img_io = io.BytesIO()
                        img_with_no_bg.save(img_io, 'PNG')
                        img_io.seek(0)
                        image.processed_image.save(
                            f"processed_{image.original_image.name}",
                            ContentFile(img_io.read()),
                            save=True
                        )
                    elif action == 'remove_fg':
                        # Invert the alpha channel to remove foreground
                        alpha = img_with_no_bg.getchannel('A')
                        inverted_alpha = Image.eval(alpha, lambda x: 255 - x)

                        # Apply inverted alpha to original image
                        original_img = Image.open(image.original_image.path).convert('RGBA')
                        original_img.putalpha(inverted_alpha)

                        # Save the foreground-removed image
                        img_io = io.BytesIO()
                        original_img.save(img_io, 'PNG')
                        img_io.seek(0)
                        image.processed_image.save(
                            f"processed_{image.original_image.name}",
                            ContentFile(img_io.read()),
                            save=True
                        )

                return JsonResponse({'image_url': image.processed_image.url})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    context = {'image': image}
    return render(request, 'edit_image.html', context)

# Delete image view
def delete_image(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)

    # Delete the image from the model and filesystem
    image.image.delete()  # This removes the file from the storage
    image.delete()  # This removes the record from the database

    return redirect('home')  # Redirect back to the homepage

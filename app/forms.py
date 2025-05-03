# forms.py
from django import forms
from .models import UploadedImage

class ImageUploadForm(forms.ModelForm):
    PROCESSING_CHOICES = [
        ('bg_removed', 'Remove Background'),
        ('fg_removed', 'Remove Foreground'),
    ]

    processing_type = forms.ChoiceField(
        choices=PROCESSING_CHOICES,
        widget=forms.RadioSelect,
        initial='bg_removed'
    )

    class Meta:
        model = UploadedImage
        fields = ['image', 'processing_type']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'})
        }
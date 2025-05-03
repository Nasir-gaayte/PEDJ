from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class UploadedImage(models.Model):
    PROCESSING_CHOICES = [
        ('bg_removed', 'Background Removed'),
        ('fg_removed', 'Foreground Removed'),
    ]
    
    image = models.ImageField(upload_to='uploads/')
    processing_type = models.CharField(
        max_length=20, 
        choices=PROCESSING_CHOICES, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - {self.processing_type or 'Original'}"

@receiver(pre_save, sender=UploadedImage)
def delete_old_file(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = UploadedImage.objects.get(pk=instance.pk)
            if old_instance.image != instance.image:
                if os.path.isfile(old_instance.image.path):
                    os.remove(old_instance.image.path)
        except UploadedImage.DoesNotExist:
            return
from django.db import models
from django.db.models.signals import pre_save, post_delete
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
        return f"Image {self.id} - {self.processing_type or 'media/Original'}"

    def delete(self, *args, **kwargs):
        """Delete the associated file when the model instance is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

@receiver(pre_save, sender=UploadedImage)
def delete_old_file(sender, instance, **kwargs):
    """Delete old file when updating the image"""
    if instance.pk:
        try:
            old_instance = UploadedImage.objects.get(pk=instance.pk)
            if old_instance.image != instance.image:
                if os.path.isfile(old_instance.image.path):
                    os.remove(old_instance.image.path)
        except UploadedImage.DoesNotExist:
            return

@receiver(post_delete, sender=UploadedImage)
def delete_file_on_delete(sender, instance, **kwargs):
    """Delete file when the record is deleted from database"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
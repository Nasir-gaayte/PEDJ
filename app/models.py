from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class UploadedImage(models.Model):
    original_image = models.ImageField(upload_to='originals/', null=True, blank=True)
    processed_image = models.ImageField(upload_to='processed/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return self.original_image.name

@receiver(pre_save, sender=UploadedImage)
def delete_old_processed_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = UploadedImage.objects.get(pk=instance.pk)
        except UploadedImage.DoesNotExist:
            return
        
        old_processed = old_instance.processed_image
        new_processed = instance.processed_image
        if old_processed and old_processed != new_processed:
            if os.path.isfile(old_processed.path):
                os.remove(old_processed.path)
                
                
class ImageTemplate(models.Model):
    name = models.CharField(max_length=255)
    template_image = models.ImageField(upload_to='templates/')
    created_at = models.DateTimeField(auto_now_add=True)

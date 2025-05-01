from django.contrib import admin
from app.models import UploadedImage, ImageTemplate
# Register your models here.
admin.site.register(UploadedImage)
admin.site.register(ImageTemplate)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('upload/', views.upload_image, name='upload_image'),
   path('process/<int:pk>/', views.process_image, name='process_image'),
    path('delete/<int:pk>/', views.delete_image, name='delete_image'),
]

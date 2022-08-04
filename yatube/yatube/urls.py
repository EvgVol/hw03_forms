from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls'), name='users'),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls'), name='group'),
    path('about/', include('about.urls'), name='about'),
]

from cProfile import label
from wsgiref.validate import validator
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Post, Group


User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма создание поста."""

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            "text": "Текст",
            "group": "Группа"
        }
        widgets = {
            'text': forms.Textarea(),
        }

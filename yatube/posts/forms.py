from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Форма создание поста."""

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            "text": "Текст",
            "group": "Группа"
        }
        help_texts = {
            'text': 'Текст сообщения',
            'group': 'Группа, к которой принадлежит это сообщение',
        }

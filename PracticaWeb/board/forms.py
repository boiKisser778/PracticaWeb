from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'email', 'subject', 'message', 'image']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
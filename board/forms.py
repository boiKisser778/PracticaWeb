from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'message', 'image']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
        
class PostReply(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', 'image']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
        
  

from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        pass
    
    pass

class SearchForm(forms.Form):
    query = forms.CharField()
    pass
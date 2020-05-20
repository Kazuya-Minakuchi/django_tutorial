from django import forms

from .models import Post, Comment, Category

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'category')

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text')

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name', 'text')

import csv
import io
import datetime
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
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

class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル',
        help_text='※拡張子csvのファイルをアップロードしてください。',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csv_file = io.TextIOWrapper(file, encoding='utf-8')
        reader = csv.reader(csv_file)
        # 各行から作った保存前のモデルインスタンスを保管するリスト
        self._instances_create = []
        self._instances_update = []
        try:
            for row in reader:
                if row[0] == "":
                    post = Post(
                        author=User.objects.get(username=row[1]),
                        title=row[2],
                        text=row[3],
                        created_date=datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S %z'),
                        published_date=datetime.datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S %z'),
                        category=Category.objects.get(name=row[6])
                        )
                    self._instances_create.append(post)
                else:
                    post = Post(
                        pk=row[0],
                        author=User.objects.get(username=row[1]),
                        title=row[2],
                        text=row[3],
                        created_date=datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S %z'),
                        published_date=datetime.datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S %z'),
                        category=Category.objects.get(name=row[6])
                        )
                    self._instances_update.append(post)
        except UnicodeDecodeError:
                raise forms.ValidationError('ファイルのエンコーディングや、正しいCSVファイルか確認ください。')
        return file
    
    def save(self):
        Post.objects.bulk_create(self._instances_create, ignore_conflicts=True)
        Post.objects.bulk_update(self._instances_update, fields=['title', 'text', 'created_date', 'published_date', 'category'])

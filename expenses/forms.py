import io
import csv
import datetime
from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import AuthenticationForm
from .models import Record, Category, Payment

class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class RecordForm(forms.ModelForm):

    class Meta:
        model = Record
        fields = ('expense_date', 'amount', 'category', 'payment', 'note')

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name',)

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ('name',)

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
                    post = Record(
                        created_date = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S %z'),
                        expense_date = datetime.datetime.strptime(row[2], '%Y-%m-%d'),
                        amount = row[3],
                        category = Category.objects.get(name=row[4]),
                        payment = Payment.objects.get(name=row[5]),
                        note = row[6]
                        )
                    self._instances_create.append(post)
                else:
                    post = Record(
                        pk=row[0],
                        created_date = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S %z'),
                        expense_date = datetime.datetime.strptime(row[2], '%Y-%m-%d'),
                        amount = row[3],
                        category = Category.objects.get(name=row[4]),
                        payment = Payment.objects.get(name=row[5]),
                        note = row[6]
                        )
                    self._instances_update.append(post)
        except UnicodeDecodeError:
                raise forms.ValidationError('ファイルのエンコーディングや、正しいCSVファイルか確認ください。')
        return file

    def save(self):
        Record.objects.bulk_create(self._instances_create, ignore_conflicts=True)
        Record.objects.bulk_update(self._instances_update, fields=['created_date', 'expense_date', 'amount', 'category', 'payment', 'note'])

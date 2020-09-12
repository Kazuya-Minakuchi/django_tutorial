import csv
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import models
from django.db.models import Max, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import ListView
from .models import Record, Category, Payment
from .forms import LoginForm, RecordForm, CategoryForm, PaymentForm, CSVUploadForm

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'expenses/login.html'

class Logout(LogoutView):
    """ログアウトページ"""
    template_name = "expenses/record_list.html"

# レコード一覧
class RecordList(ListView):
    template_name = "expenses/record_list.html"
    context_object_name = 'records'
    paginate_by = 10
    def get_queryset(self):
        q_word = self.request.GET.get('query')
        if q_word:
            object_list = Record.objects.filter(Q(note__icontains=q_word))
        else:
            object_list = Record.objects.all()
        return object_list.order_by('-expense_date', '-created_date')

# カテゴリ一覧
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'expenses/category_list.html', {'categories': categories})

# 支払い方法一覧
@login_required
def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'expenses/payment_list.html', {'payments': payments})

# レコード追加
@login_required
def record_new(request):
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.author = request.user
            record.save()
            return redirect('expenses:record_list')
    else:
        form = RecordForm()
    return render(request, 'expenses/record_edit.html', {'form': form})

# レコード編集
@login_required
def record_edit(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == "POST":
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.author = request.user
            record.save()
            return redirect('expenses:record_list')
    else:
        form = RecordForm(instance=record)
    return render(request, 'expenses/record_edit.html', {'form': form})

# レコードコピー
@login_required
def record_copy(request, pk):
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.author = request.user
            record.save()
            return redirect('expenses:record_list')
    else:
        copied_record = get_object_or_404(Record, pk=pk)
        copied_data = {
            'amount': copied_record.amount,
            'category': copied_record.category,
            'payment': copied_record.payment,
            'note': copied_record.note,
        }
        form = RecordForm(None, initial=copied_data)
    return render(request, 'expenses/record_edit.html', {'form': form})

# カテゴリ追加
@login_required
def category_new(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('expenses:category_list')
    else:
        form = CategoryForm()
    return render(request, 'expenses/category_edit.html', {'form': form})

# カテゴリ編集
@login_required
def category_edit(request, pk):
    post = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('expenses:category_list')
    else:
        form = CategoryForm(instance=post)
    return render(request, 'expenses/category_edit.html', {'form': form})

# 支払い方法追加
@login_required
def payment_new(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('expenses:payment_list')
    else:
        form = PaymentForm()
    return render(request, 'expenses/payment_edit.html', {'form': form})

# 支払い方法編集
@login_required
def payment_edit(request, pk):
    post = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('expenses:payment_list')
    else:
        form = PaymentForm(instance=post)
    return render(request, 'expenses/payment_edit.html', {'form': form})

# レコード削除
def record_remove(request, pk):
    record = get_object_or_404(Record, pk=pk)
    record.delete()
    return redirect('expenses:record_list')

# カテゴリ削除
def category_remove(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('expenses:category_list')

# 支払い方法削除
def payment_remove(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.delete()
    return redirect('expenses:payment_list')

# リストの重複を消してソートする関数
def sorted_unique_list(lst):
    return sorted(list(set(lst)))

# レコード集計用、フィルタ&合計関数
def filter_sum(amounts, month, key=None, key_pk=None):
    amount_filtered_month = filter(lambda x: x['expense_date'].strftime('%Y-%m') == month, amounts)
    if key == None:
        return sum(map(lambda x: x['total_price'], amount_filtered_month))
    else:
        amount_filtered = filter(lambda x: (x[key] == key_pk), amount_filtered_month)
        return sum(map(lambda x: x['total_price'], amount_filtered))

# 月+αでの金額集計用関数
def amount_aggregate(months, amounts, key, contents):
    return_dicts = []
    for month in months:
        dict_month = {'month': month, 'contents': []}
        for content in contents:
            dict_month['contents'].append({'con_pk': content.pk,
             'con_name': content.name,
             'amount': filter_sum(amounts, month, key, content.pk)})
        return_dicts.append(dict_month)
    return return_dicts

# レコード集計画面
def record_aggregate(request):
    records = Record.objects.all()
    categories = Category.objects.all()
    payments = Payment.objects.all()
    
    # 「日、カテゴリ、支払い方法」で金額をまとめる
    amounts = (
        records
        .values('expense_date', 'category', 'payment')
        .annotate(total_price=Sum('amount'))
    )
    
    # 集計用の月一覧
    months = sorted_unique_list([amount['expense_date'].strftime('%Y-%m') for amount in amounts])
    # 月で金額を集計
    amounts_per_m = [{'month': month, 'amount': filter_sum(amounts, month)} for month in months]
    # 月・カテゴリで金額を集計
    amounts_per_m_c = amount_aggregate(months, amounts, 'category', categories)
    # 月・支払い方法で金額を集計
    amounts_per_m_p = amount_aggregate(months, amounts, 'payment', payments)

    context = {
        'amounts': amounts,
        'categories': categories,
        'payments': payments,
        'amounts_per_m': amounts_per_m,
        'amounts_per_m_c': amounts_per_m_c,
        'amounts_per_m_p': amounts_per_m_p,
    }
    return render(request, 'expenses/record_aggregate.html', context)

# カテゴリCSVインポート
class RecordImport(generic.FormView):
    template_name = 'expenses/record_import.html'
    success_url = reverse_lazy('expenses:record_list')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save()
        return redirect('expenses:record_list')

# カテゴリCSVエクスポート
def record_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="records.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せる
    writer = csv.writer(response)
    records = Record.objects.all()
    for record in records:
        writer.writerow(
            [record.pk,
             record.created_date.strftime('%Y-%m-%d %H:%M:%S %z'),
             record.expense_date.strftime('%Y-%m-%d'),
             record.amount,
             record.category,
             record.payment,
             record.note
             ]
        )
    return response


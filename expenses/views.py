import csv
import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from .models import Record, Category, Payment
from .forms import RecordForm, CategoryForm, PaymentForm, CSVUploadForm

# レコード一覧
def record_list(request):
    records = Record.objects.order_by('-expense_date', '-created_date')
    page_obj = paginate_queryset(request, records, 10)
    context = {
        'records': page_obj.object_list,
        'page_obj': page_obj,
        'start_page': page_obj.number - 4,
        'end_page': page_obj.number + 4,
    }
    return render(request, 'expenses/record_list.html', context)

def paginate_queryset(request, queryset, count):
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

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
            'expense_date': copied_record.expense_date,
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


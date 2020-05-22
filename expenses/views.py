import csv
import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from .models import Record, Category, Payment
from .forms import RecordForm, CategoryForm, PaymentForm, CSVUploadForm

def record_list(request):
    records = Record.objects.order_by('-expense_date')
    return render(request, 'expenses/record_list.html', {'records': records})

@login_required
def record_edit(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == "POST":
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.author = request.user
            record.save()
            return redirect('record_list')
    else:
        form = RecordForm(instance=record)
    return render(request, 'expenses/record_edit.html', {'form': form})

@login_required
def record_new(request):
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.author = request.user
            record.save()
            return redirect('record_list')
    else:
        form = RecordForm()
    return render(request, 'expenses/record_edit.html', {'form': form})

@login_required
def category_list(request):
    categories = Category.objects.all
    return render(request, 'expenses/category_list.html', {'categories': categories})

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

@login_required
def payment_list(request):
    payments = Payment.objects.all
    return render(request, 'expenses/payment_list.html', {'payments': payments})

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

class RecordImport(generic.FormView):
    template_name = 'expenses/import.html'
    success_url = reverse_lazy('expenses:record_list')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save()
        return redirect('expenses:record_list')

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

def record_remove(request, pk):
    record = get_object_or_404(Record, pk=pk)
    record.delete()
    return redirect('expenses:record_list')

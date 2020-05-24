from . import views
from .models import Record, Category, Payment
from django.db import models
from django.db.models import Max, Sum

from django.test import TestCase

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
def record_aggregate():
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
    # return context
    return amounts_per_m

ret = record_aggregate()
print(ret)

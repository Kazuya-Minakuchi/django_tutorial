from . import views
from .models import Record, Category, Payment
from django.db import models
from django.db.models import Max, Sum

from django.test import TestCase

# リストの重複を消してソートする関数
def sorted_unique_list(lst):
    return sorted(list(set(lst)))

# レコード集計用の辞書作成関数
def create_dict(months, key, contents):
    content_dict_list = [{key: content, 'amount': 0} for content in contents]
    ret_dict = [{'month': month, 'content': content_dict_list} for month in months]
    return ret_dict

# レコード集計用、フィルタ&合計関数
def filter_sum(dict, amounts, key, key_pk):
    amount_filtered_month = filter(lambda x: x['expense_date'].strftime('%Y-%m') == dict['month'], amounts)
    amount_filtered = filter(lambda x: (x[key] == key_pk), amount_filtered_month)
    return sum(map(lambda x: x['total_price'], amount_filtered))

# 金額集計用関数
def amount_aggregate(months, amounts, key, contents):
    return_dicts = create_dict(months, key, contents)
    for return_dict in return_dicts:
        for content in return_dict['content']:
            content['amount'] = filter_sum(return_dict, amounts, key, content[key].pk)
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
    # 月・カテゴリで金額を集計
    amounts_per_m_c = amount_aggregate(months, amounts, 'category', categories)
    # # 月・支払い方法で金額を集計
    amounts_per_m_p = amount_aggregate(months, amounts, 'payment', payments)

    context = {
        'amounts': amounts,
        'amounts_per_m_c': amounts_per_m_c,
        'amounts_per_m_p': amounts_per_m_p,
    }
    return context
    return amounts_per_m_c

ret = record_aggregate()
print(ret)

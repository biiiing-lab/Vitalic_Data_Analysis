from calendar import monthrange
from collections import defaultdict
from django.db.models import Sum, Case, When, F, IntegerField
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear, ExtractWeekDay
from django.http import JsonResponse

from .models import passbook

CATEGORY_MAPPING = {
    0: '입금',
    1: '이체',
    2: '편의점',
    3: '마트',
    4: '웹쇼핑',
    5: '엔테터인먼트(영화, 게임)',
    6: '카페',
    7: '패스트푸드',
    8: '식당',
    9: '기타'
}


def get_summary_data(transactions):
    deposit_total = transactions.filter(inout_type=0).aggregate(total=Sum('tran_amt'))['total'] or 0
    withdraw_total = transactions.filter(inout_type=1).aggregate(total=Sum('tran_amt'))['total'] or 0

    category_sums = transactions.filter(inout_type=1).values('out_type').annotate(total=Sum('tran_amt'))
    category_sums = sorted(category_sums, key=lambda x: x['total'], reverse=True)[:3]

    top_categories = [
        {
            'out_type': CATEGORY_MAPPING.get(item['out_type'], '알 수 없음'),
            'amount': item['total']
        }
        for item in category_sums
    ]

    return {
        "deposit_total": deposit_total,
        "withdraw_total": withdraw_total,
        "top_categories": top_categories
    }


def fixed_group():
    return (passbook.objects
            .annotate(
        day=ExtractDay('tran_date_time'),
        week_day=ExtractWeekDay('tran_date_time'),
        month=ExtractMonth('tran_date_time'),
        year=ExtractYear('tran_date_time'),
        withdrawal_amount=Case(
            When(inout_type=1, then=F('tran_amt')),
            default=0,
            output_field=IntegerField(),
        )
    )
            .values('day', 'month', 'year', 'week_day', 'withdrawal_amount', 'inout_type', 'in_des')
            .order_by('year', 'month', 'day'))


def fixed_analysis_patterns():
    transactions_by_day = fixed_group()
    monthly_pattern = defaultdict(list)

    for transaction in transactions_by_day:
        day = transaction['day']
        withdraw_amount = transaction['withdrawal_amount'] if transaction['inout_type'] == 1 else 0
        withdrawal_source = transaction['in_des']

        if withdraw_amount > 0:
            monthly_pattern[(day, withdrawal_source)].append(withdraw_amount)

    monthly_result = []

    for (day, withdrawal_source), amounts in monthly_pattern.items():
        if len(amounts) >= 15:  # Adjusted to 15 occurrences
            monthly_result.append({
                'date': f'{day}일',
                'amount': amounts[0],
                'source': withdrawal_source
            })

    return {
        "monthly": monthly_result if monthly_result else None
    }


def calendar_amount(year, month):
    # Prepare a dictionary to hold daily totals
    daily_totals = {}

    # 1부터 해당 월의 마지막 날까지의 일자 가져오기
    last_day = monthrange(year, month)[1]  # 해당 월의 마지막 날
    for day in range(1, last_day + 1):  # 각 날짜에 대해 반복
        # 필터링: 해당 날짜의 거래 내역
        daily_transactions = passbook.objects.filter(
            tran_date_time__year=year,
            tran_date_time__month=month,
            tran_date_time__day=day
        )

        # 입금과 출금 합계 계산
        deposit_total = daily_transactions.filter(inout_type=0).aggregate(total=Sum('tran_amt'))['total'] or 0
        withdraw_total = daily_transactions.filter(inout_type=1).aggregate(total=Sum('tran_amt'))['total'] or 0

        # 결과를 딕셔너리에 추가
        daily_totals[day] = {
            'deposits': deposit_total,
            'withdrawals': withdraw_total
        }

    return daily_totals
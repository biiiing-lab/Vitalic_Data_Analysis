from calendar import monthrange
from datetime import datetime, timedelta
from django.db.models import Sum, Case, When, F, IntegerField
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.utils import timezone
from rest_framework.response import Response
from .models import passbook
from collections import defaultdict
from .serializers import ResponseSerializer # 직렬화기 클래스

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

# 많이 쓴 곳 카테고리 탑 3개
def get_summary_data(transactions):

    # 입 출금 필터링
    # aggregate 기본 연산 함수 집계
    deposit_total = transactions.filter(inout_type=0).aggregate(total=Sum('tran_amt'))['total'] or 0
    withdraw_total = transactions.filter(inout_type=1).aggregate(total=Sum('tran_amt'))['total'] or 0

    # transaction Django 모델 쿼리셋 사용
    #.values 쿼리셋을 out_type 필드를 기준으로 그룹화 -> 딕셔너리 형태이며 out_type 키 포함
    # annotate(total = Sum('tran_amt')) 각 그룹에 대해 tran_amt 필드의 합계를 계산하여 total 새 필드 추가
    category_sums = transactions.filter(inout_type=1).values('out_type').annotate(total=Sum('tran_amt'))

    # 탑 3 카테고리 (기타 제외)
    top_categories = []
    used_categories = set()

    # 카테고리 정렬
    # key = lambda x : x['total'] -> key 값은 x의 total key 값을 기준으로 정리
    # reverse = True 내림차순으로
    category_sums = sorted(category_sums, key=lambda x: x['total'], reverse=True)

    for item in category_sums:
        category_name = CATEGORY_MAPPING.get(item['out_type'], '알 수 없음')
        if category_name != '기타' and len(top_categories) < 3:
            top_categories.append({
                'out_type': category_name,
                'amount': item['total']
            })
            used_categories.add(category_name)

    return {
        "deposit_total": deposit_total,
        "withdraw_total": withdraw_total,
        "top_categories": top_categories
    }

# 전체 분석
def transaction_mwd() :

    # 현재 시간
    today = timezone.now()

    #오늘 기준으로 1주일 전, 1달 전 값 구하기
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)

    # 데일리
    daily_transactions = passbook.objects.filter(tran_date_time__date = today.date())
    daily_summary_data = get_summary_data(daily_transactions)

    # 위클리
    weekly_transactions = passbook.objects.filter(tran_date_time__gte = one_week_ago)
    weekly_summary_data = get_summary_data(weekly_transactions)

    # 먼슬리
    monthly_transactions = passbook.objects.filter(tran_date_time__gte = one_month_ago)
    monthly_summary_data = get_summary_data(monthly_transactions)

    response_data = {
        'monthly_summary': monthly_summary_data,
        'weekly_summary': weekly_summary_data,
        'daily_summary': daily_summary_data,
    }

    # response_data를 직렬화 하여 serializer 변수에 담음
    serializer = ResponseSerializer(response_data)

    # Response 객체를 생성하여 반환
    return Response(serializer.data)

# 위클리, 데일리 삭제 / 기타 카테고리 제외 / 모든 카테고리 합산 전달
def monthly_statistics(year, month):

    # 연과 달을 가지고 오기
    transactions = passbook.objects.filter(tran_date_time__year = year, tran_date_time__month = month)

    # 사용 top 3 카테고리 가져오기
    monthly_top3_summary = get_summary_data(transactions)

    # 사용 top 3를 제외한 나머지 카테고리 필터링
    # 사용 top 3 카테고리 이름만 추출
    top3_categories = {cat['out_type'] for cat in monthly_top3_summary['top_categories']}

    # 사용 top 3를 제외한 나머지 카테고리 필터링
    category_sums = transactions.filter(inout_type=1).values('out_type').annotate(total=Sum('tran_amt'))

    other_categories = []

    for item in sorted(category_sums, key=lambda x: x['total'], reverse=True):
        category_name = CATEGORY_MAPPING.get(item['out_type'], '알 수 없음')
        if category_name != '기타' and category_name not in top3_categories:
            other_categories.append({
                'out_type': category_name,
                'amount': item['total']
            })

    # 기타 항목의 총합 계산
    other_total = transactions.filter(inout_type=1, out_type=9).aggregate(total=Sum('tran_amt'))['total'] or 0

    # 기타 항목 추가
    other_categories.append({
        'out_type': CATEGORY_MAPPING.get(9, '기타'),  # 기본적으로 '기타'로 설정
        'amount': other_total
    })

    return {
        "monthly_top3_summary": monthly_top3_summary,
        "other_categories": other_categories
    }


def fixed_group():
    # 현재 날짜로부터 4개월 전 날짜 계산, 대략적인 계산
    today = datetime.today()
    four_months_ago = today - timedelta(days=4*30)

    return (passbook.objects
            .filter(tran_date_time__gte=four_months_ago)
            .annotate(
                # 날짜 추출
                day=ExtractDay('tran_date_time'),
                month=ExtractMonth('tran_date_time'),
                year=ExtractYear('tran_date_time'),

                # case, when으로 경우 분류
                # inout_type이 1일 경우 withdrawal에 넣지만 아닐 경우 0을 반환
                withdrawal_amount=Case(
                    When(inout_type=1, then=F('tran_amt')),
                    default=0,
                    output_field=IntegerField(),
                )
            )
            .values('day', 'month', 'year', 'withdrawal_amount', 'inout_type', 'in_des') # 값
            .order_by('year', 'month', 'day')) # 정렬 방식


def fixed_analysis_patterns():
    transactions_by_day = fixed_group()
    monthly_pattern = defaultdict(list)

    # 그룹화된 데이터를 처리하여 출금 내역을 월별 패턴으로 그룹화
    for transaction in transactions_by_day:
        day = transaction['day']
        withdraw_amount = transaction['withdrawal_amount'] if transaction['inout_type'] == 1 else 0
        withdrawal_source = transaction['in_des']

        if withdraw_amount > 0:
            # 출금일, 출금처, 출금액으로 그룹화
            monthly_pattern[(day, withdrawal_source, withdraw_amount)].append(transaction)

    monthly_result = []

    # 각 그룹을 순회하면서 3번 이상 발생한 항목만 고정 지출로 간주
    for (day, withdrawal_source, amount), transactions in monthly_pattern.items():
        # 3회 이상 발생한 경우만 처리
        if len(transactions) >= 3:
            monthly_result.append({
                'date': f'{day}일',
                'amount': amount,
                'source': withdrawal_source
            })

    return {
        "monthly": monthly_result if monthly_result else None
    }


# 요청 연, 월, 일을 받았을 경우 그 날짜에 해당하는 입출금 합산 값, 입출금처를 보내줌
def calendar_amount(year, month, day):

    # 해당 날짜의 거래 내역 가져오기
    daily_transactions = passbook.objects.filter(
            tran_date_time__year=year,
            tran_date_time__month=month,
            tran_date_time__day=day
    )

    # 필터링1 : 해당 날짜 거래내역 가져오기
    deposit_transactions = daily_transactions.filter(inout_type=0)
    withdraw_transactions = daily_transactions.filter(inout_type=1)

    # 필터링2 : 입금과 출금 합계 계산
    deposit_total = daily_transactions.filter(inout_type=0).aggregate(total=Sum('tran_amt'))['total'] or 0
    withdraw_total = daily_transactions.filter(inout_type=1).aggregate(total=Sum('tran_amt'))['total'] or 0

    # 데이터 처리 : 거래 내역의 날짜 포맷 변경
    deposit_details = [
        {
            **transaction,
            'tran_date_time': transaction['tran_date_time'].strftime("%Y-%m-%d %H:%M")
        } for transaction in deposit_transactions.values('tran_amt', 'in_des', 'tran_date_time')
    ]

    withdraw_details = [
        {
            **transaction,
            'tran_date_time': transaction['tran_date_time'].strftime("%Y-%m-%d %H:%M")
        } for transaction in withdraw_transactions.values('tran_amt', 'in_des', 'tran_date_time')
    ]

    # 결과 딕셔너리 생성
    daily_totals = {
        'deposits_total': deposit_total,
        'withdrawals_total': withdraw_total,
        'deposit_details': deposit_details,
        'withdraw_details': withdraw_details
    }

    return daily_totals


# 해당 날짜의 모든 값을 다 보내야함
def calendar_all_amount(year, month):
    # 월의 마지막 날짜 계산
    last_day = (datetime(year, month, 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # 월의 모든 날짜에 대한 입출금 합산 결과를 저장할 리스트
    monthly_totals = []

    # 각 날짜에 대해 입출금 합산 계산
    for day in range(1, last_day.day + 1):
        daily_transactions = passbook.objects.filter(
            tran_date_time__year=year,
            tran_date_time__month=month,
            tran_date_time__day=day
        )

        deposit_total = daily_transactions.filter(inout_type=0).aggregate(total=Sum('tran_amt'))['total'] or 0
        withdraw_total = daily_transactions.filter(inout_type=1).aggregate(total=Sum('tran_amt'))['total'] or 0

        # 날짜별 결과 딕셔너리 생성
        daily_totals = {
            'day': day,
            'deposit': deposit_total,
            'withdraw': withdraw_total
        }

        monthly_totals.append(daily_totals)

    return monthly_totals
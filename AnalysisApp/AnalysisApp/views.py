from django.http import JsonResponse
from rest_framework.decorators import api_view
from .services import fixed_analysis_patterns, calendar_amount, monthly_statistics, transaction_mwd

# 월, 주, 일 기준 분석
@api_view(['POST'])
def transaction_summary(request):
    return transaction_mwd()

# 월별 많이 사용한 곳 입출금 합산
@api_view(['POST'])
def monthly_summary(request):
    year = request.data.get('year')
    month = request.data.get('month')
    return JsonResponse(monthly_statistics(year, month), safe=False)

# 고정 지출 분석
@api_view(['POST'])
def fixed_expenses(request):
    return JsonResponse(fixed_analysis_patterns(), safe=False)

# 선택 캘린더별 사용 내역
@api_view(['POST'])
def calendar_return(request):
    year = request.data.get('year')
    month = request.data.get('month')
    day = request.data.get('day')

    daily_totals = calendar_amount(year, month, day)

    return JsonResponse(daily_totals)
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from .email import send_email
from .services import fixed_analysis_patterns, calendar_amount, monthly_statistics, transaction_mwd, calendar_all_amount


# 월, 주, 일 기준 분석
@api_view(['POST'])
def transaction_summary(request):
    return transaction_mwd()

# 월별 많이 사용한 곳 입출금 합산
@api_view(['POST'])
def monthly_summary(request):
    monthly_statistic = monthly_statistics(request.data.get('year'),
                                           request.data.get('month'))
    return JsonResponse(monthly_statistic, safe=False)

# 고정 지출 분석
@api_view(['POST'])
def fixed_expenses(request):
    return JsonResponse(fixed_analysis_patterns(), safe=False)

# 선택 캘린더별 사용 내역
@api_view(['POST'])
def calendar_return(request):
    daily_calendar_totals = calendar_amount(request.data.get('year'),
                                   request.data.get('month'),
                                   request.data.get('day'))
    return JsonResponse(daily_calendar_totals)

# 전체 캘린더
@api_view(['POST'])
def monthly_return(request):
    monthly_calendar_totals = calendar_all_amount(request.data.get('year'),
                                       request.data.get('month'))
    return JsonResponse(monthly_calendar_totals, safe=False)

# 시각화 요청 PDF
@api_view(['POST'])
def visualization_pdf(request) :
    email = request.data.get('email')
    start_date = timezone.now() - timedelta(days=180) # 6개월 데이터 조회 및 시각화
    end_date = timezone.now()
    result = send_email(start_date, end_date, email)

    if(result) :
        return JsonResponse("이메일 차트 발송 완료", safe=False)
    else:
        return JsonResponse("이메일 차트 발송 실패", safe=False)
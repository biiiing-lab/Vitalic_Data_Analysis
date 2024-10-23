from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import passbook
from .serializers import ResponseSerializer
from .services import get_summary_data, fixed_analysis_patterns, calendar_amount  # Import your service functions

# 월, 주, 일 기준 분석
@api_view(['POST'])
def transaction_summary(request):
    today = timezone.now()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)

    daily_transactions = passbook.objects.filter(tran_date_time__date=today.date())
    daily_summary_data = get_summary_data(daily_transactions)

    weekly_transactions = passbook.objects.filter(tran_date_time__gte=one_week_ago)
    weekly_summary_data = get_summary_data(weekly_transactions)

    monthly_transactions = passbook.objects.filter(tran_date_time__gte=one_month_ago)
    monthly_summary_data = get_summary_data(monthly_transactions)

    response_data = {
        'monthly_summary': monthly_summary_data,
        'weekly_summary': weekly_summary_data,
        'daily_summary': daily_summary_data,
    }

    serializer = ResponseSerializer(response_data)
    return Response(serializer.data)

# 고정 지출 분석
@api_view(['POST'])
def fixed_expenses(request):
    return JsonResponse(fixed_analysis_patterns(), safe=False)


@api_view(['POST'])
def calendar_return(request):
    # Step 2: Extract year and month from the request
    year = request.data.get('year')
    month = request.data.get('month')

    print(f"Requested Year: {year}, Month: {month}")  # 로그 추가

    # Validate year and month
    if not year or not month:
        return JsonResponse({'error': 'Year and month are required.'}, status=400)

    # Call the service to get daily totals
    daily_totals = calendar_amount(year, month)

    # Return the formatted response
    return JsonResponse({'year': year, 'month': month, 'daily_totals': daily_totals})
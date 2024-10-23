from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import passbook
from .serializers import ResponseSerializer
from .services import get_summary_data, fixed_analysis_patterns  # Import your service functions

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

@api_view(['POST'])
def fixed_expenses(request):
    return JsonResponse(fixed_analysis_patterns(), safe=False)

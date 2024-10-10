from rest_framework import serializers

class SummarySerializer(serializers.Serializer):
    deposit_total = serializers.IntegerField()
    withdraw_total = serializers.IntegerField()
    top_categoryies = serializers.ListField()

class ResponseSerializer(serializers.Serializer):
    monthly_summary = SummarySerializer()
    weekly_summary = SummarySerializer()
    daily_summary = SummarySerializer()
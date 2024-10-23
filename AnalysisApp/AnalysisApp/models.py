from django.db import models

class passbook (models.Model) :
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    balance_amt = models.IntegerField()
    inout_type = models.IntegerField()  # 0: 입금, 1: 출금
    in_des = models.CharField(max_length=100)
    out_des = models.CharField(max_length=100)
    tran_date_time = models.DateTimeField()
    tran_type = models.IntegerField()
    tran_amt = models.IntegerField()
    after_balance_amt = models.IntegerField()
    out_type = models.IntegerField()  # todo 수정

    class Meta :
        db_table = 'passbook'
        app_label = 'AnalysisApp'

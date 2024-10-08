from django.db import models

class passbook (models.Model) :
    bank_name = models.CharField()
    account_number = models.CharField()
    balance_amt = models.IntegerField()
    inout_type = models.IntegerField()  # 0: 입금, 1: 출금
    in_des = models.CharField()
    out_des = models.CharField()
    tran_date_time = models.DateTimeField()
    tran_type = models.IntegerField()
    tran_amt = models.IntegerField()
    after_balance_amt = models.IntegerField()
    category = models.IntegerField()  # todo 수정

    class Meta :
        db_table = 'passbook'
        managed = False # 실제 테이블 관리 X

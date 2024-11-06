# 💊 Vitalic : 개인 금융 자산 관리 웹사이트

## 🌟  Vitalic이 무엇인가요?
(전체 작동 영상 추가)
 바이탈릭(Milky Way)는 2030 세대를 대상으로 **금융 자산 관리 능력을 향상**시킬 수 있고, 소비패턴과 지출목표를 등록하여 원활한 사용을 하고 있는지 이메일 알림 서비스를 제공합니다. 

 또한 자신이 사용한 입출금 패턴을 분석하여 소비 습관을 확인할 수 있으며, 사이트 일일 지출 및 캘린더를 통한 사용 요약을 확인 가능합니다. 많은 데이터가 쌓인 이후, 사용자는 요청 날짜를 기준으로 6개월 동안의 패턴 분석 차트 PDF를 이메일로 받아볼 수 있습니다.

<br>

## 🔗전체 프로젝트 리포지토리
- [Vitalic Front-End Repository](https://github.com/ziiroJ/Vitalic_Front)   
- [Vitalic Back-End Repository](https://github.com/LeeTaeGyeong00/Vitalic_Back)

<br>

##  🙋‍♀️ Vitalic_Data_Analysis 주요 기술
🔨 **환경**
- Django Framwork
- Python 3.12.6

<br>

 📈**시각화 관련 사용 모듈** 📈
- pandas
- seaborn, matplotlib
- PdfPages, Image

<br>

👓 **데이터 정제 및 필터링 관련 사용 모듈**
- models : Sum, Case, When, F, IntegerField, filter
- datetime, timezone

<br>

🧺 **데이터베이스**
- MySQL

<br>

##  🙋‍♀️ Vitalic_Data_Analysis 기능
> 데이터 필터링을 통하여 사용자에게 유의미한 데이터를 반환합니다. <br>

> 누적된 사용자의 입출금 데이터를 통하여 패턴을 파악합니다. <br>

> 사용자에게 직접적으로 입출금 사용 흐름을 알려줍니다. 


### RestFul API

#### 오늘을 기준으로 월, 주, 일 사용 분석과 가장 많이 사용한 카테고리 TOP3
- 기간별 필터링
- filter aggregate Sum을 활용하여 집계 연산
- 내림차순 정렬
<u> Response</u>
```
{
    "monthly_summary": {
        "deposit_total": monthly_deposit_total,
        "withdraw_total": monthly_withdraw_total,
        "top_categories": [
            {
                "out_type": "monthly_top1",
                "amount": amount
            },
            {
                "out_type": "monthly_top2",
                "amount": amount
            },
            {
                "out_type": "monthly_top3",
                "amount": amount
            }
        ]
    },
    "weekly_summary": {
        "deposit_total": weekly_deposit_total,
        "withdraw_total": weekly_deposit_total,
        "top_categories": [
            {
                "out_type": "weekly_top1",
                "amount": amount
            },
            {
                "out_type": "weekly_top3",
                "amount": amount
            },
            {
                "out_type": "weekly_top3",
                "amount": amount
            }
        ]
    },
    "daily_summary": {
        "deposit_total": daily_deposit_total,
        "withdraw_total": daily_deposit_total,
        "top_categories": [
            {
                "out_type": "daily_top1",
                "amount": amount
            },
            {
                "out_type": "daily_top2",
                "amount": amount
            },
            {
                "out_type": "daily_top3",
                "amount": amount
            }
        ]
    }
}
```

#### 해당 연, 월에 많이 사용한 카테고리 TOP3 및 순차 정렬
- TOP3 필터링 및 나머지 카테고리 필터링 처리
<u>Request</u>
```
{
    "year" : year, # ex 2024
    "month" : month # ex 11
}
```

<u>Response</u>
```
{
    "monthly_top3_summary": {
        "deposit_total": deposit_total,
        "withdraw_total": withdraw_total,
        "top_categories": [
            {
                "out_type": "top1",
                "amount": amount
            },
            {
                "out_type": "top2",
                "amount": amount
            },
            {
                "out_type": "top3",
                "amount": amount
            }
        ]
    },
    "other_categories": [
        {
            "out_type": "top4",
            "amount": amount
        },
.
.
.
        {
            "out_type": "topN",
            "amount": amount
        },
    ]
}

```

#### 고정 지출 분석
- 현재 날짜로부터 4개월를 기준으로 지출 계산 `timedelta(days = 4 * 30)`
- 출금 내역 월별 그룹화
- 출금일, 출금처, 출금액 그룹화
- 각 그룹 순회하며 3번 이상 동일하게 발생 시 고정 지출로 간주 후 반환
```
{
    "monthly": [
        {
            "date": f"${date}일", # ex 10일 
            "amount": amount,
            "source": source # 출금처
        },
.
.
.
    ]
}
```

#### 캘린더 특정 월 전체와 선택 날짜값 필터링 후 입출금 내역, 합산 반환
##### 특정 월 전체 반환
- 월의 마지막 날짜 계산
- 입출금 합산 계산
<u>Request</u>
```
{
    "year" : year, # 2024
    "month" : month # 11
}
```

<u>Response</u>
```
[
    {
        "day": 1,
        "deposit": deposit,
        "withdraw": withdraw
    },
.
.
.
    {
        "day": last_day, # 28, 30, 31 중 1
        "deposit": deposit,
        "withdraw": withdraw
```

##### 특정 날짜 반환
- 날짜 포맷 변경 `strftime("%Y-%m-%d %H:%M")`
<u>Request</u>
```
{
    "year" : year, # 2024
    "month" : month, # 11
    "day" : day # 6
}
```

<u>Response</u>
```
{
    "deposits_total": deposits_total,
    "withdrawals_total": withdrawals_total,
    "deposit_details": [
        {
            "tran_amt": tran_amt, # 입금 금액
            "in_des": in_des, # 입금처
            "tran_date_time": # todo 데이터 형식값 추가
        }
.
.
    ],
    "withdraw_details": [
        {
            "tran_amt": tran_amt, # 출금 금액
            "in_des": in_des, # 출금처
            "tran_date_time": # todo 데이터 형식값 
        },
      .
      .
      .
    ]
}
```

<br>

### 오늘을 기준으로 6개월간의 분석 차트 : 각각 사진 추가
#### 입출금 횟수 및 입출금 금액 합계, 잔액 변화 (선 및 막대 그래프)
##### 분석 과정
1. 요청 날짜로부터 6개월 간의 데이터 필터링 **range**
2. 월 단위로 그룹화 **TruncMonth**를하여 <i>period</i> 그룹 생성
3. 거래 건 수 **Count**
4. 입출금 합계 **Sum** 계산, DB 기준 **filter** 처리
5. 입금 금액에서 출금 금액을 제외한 **F** 계산
6. **order_by**로 <i>period</i> 정렬

##### 차트 설명
- **matplotlib.pyplot** 사용
- 막대 그래프 : 입출금 횟수
- 선 그래프 : 입금 / 출금 / 잔액 변동 
- 결과물 추가
- 사진 추가 예정

<br>

#### 매월 초, 말의 잔액 변화 (히스토그램)
##### 분석 과정
1. 요청 날짜로부터 6개월 기간 중 매 월 1일 필터링
2. 마지막 날(28, 30, 31) **Q** 필터링
3. 각 월 **TrancMonth**로 <i>period</i> 그룹화
4. 그룹화 한 <i>period</i> 순차 정렬
5. **Pandas** 를 활용하여 데이터 프레임 생성
6. **to_period**, **to_timestamp** 활용하여 월 말 데이터가 있는 날짜로 변환
7. **tz_localize** 기간 형식 동일화
8. 결측치 **fillna**로 0 처리
9. 두 개(초, 말) 데이터 프레임 병합
10. 눈금 단위 설정


##### 차트 설명
- **matplotlib.pyplot** 사용으로 x, y 프레임 설정
- **seaborn** 의 **hisplot** 으로 시각화
- 사진 추가 예정

<br>

#### 카테고리별 사용 빈도와 평균 사용 시간 (산포도)
##### 분석 과정
1. 요청 날짜로부터 6개월간의 데이터 **range** 필터링
2. 카테고리별 사용 빈도 **Count** 집계
3. 사용 시간대 **filter** 추출 후 **Pandas** 데이터 프레임 생성
4. 데이터 프레임 내 카테고리별(**groupby**) 평균 시간 추출
5. 각 카테고리 이름 매핑
6. 카테고리 사용 빈도와 평균 사용 시간대 **Pandas merge** 병합
7. 가장 활동시간인 09시부터 24시까지 출력

##### 차트 설명
- **matplotlib.pyplot** 사용으로 x, y 프레임 설정 및 시간 설정
- **seaborn** 의 **scatterplot** 으로 시각화
- 사진 추가 예정

<br>

#### 요일 및 시간대별 사용 패턴 (버블차트)
##### 분석 과정
1. 요청 날짜로부터 6개월간의 데이터 **range** 필터링
2. **Pandas** 를 통하여 데이터 프레임을 시간, 카테고리, 금액 list 형태로 변환
3. 요일과 시간대 각각 열 추가
4. **Pandas의 groupby size()** 를 통하여 사용 빈도 집계
5. 요일 이름을 0-6에서 월-일로 변경

##### 차트 설명
- **matplotlib.pyplot** 사용
- **scatter**로 버블 생성 및 크기 조절
- **colorbar** 를 통하여 사용 빈도를 나타냄
- **xticks** 로 시간 범위 설정
- 사진 추가 예정

<br>

### 메일 서비스
#### 4개의 분석 차트를 한 페이지의 PDF 변환
- 사진 추가 예정
#### SMTP Google Email PDF 발송
- 사진 추가 예정

<br>
    
   
 


# 시각화 차트 생성 파일

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncMonth
from matplotlib import ticker

from .models import passbook
from .services import CATEGORY_MAPPING

# 한글 폰트 경로 설정 (Windows에서 맑은 고딕 폰트 경로)
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 경로 예시
fontprop = fm.FontProperties(fname=font_path)

# 전체 폰트 설정
plt.rc("font", family=fontprop.get_name())

# 기본 통계 : 입금, 출금 횟수, 입출금 뺀 나머지 잔액 및 입출금 금액 시각화
def plot_basic_visualization(start_date, end_date):

    queryset = (
        passbook.objects.filter(tran_date_time__range=[start_date, end_date])
        .annotate(period=TruncMonth("tran_date_time"))
        .values("period")
        .annotate(
            transaction_count=Count("id"),
            deposit_total=Sum("tran_amt", filter=Q(inout_type=0)),  # 입금 합계
            withdrawal_total=Sum("tran_amt", filter=Q(inout_type=1)),  # 출금 합계
            remain_total=F('deposit_total') - F('withdrawal_total')
        )
        .order_by("period")
    )

    df = pd.DataFrame(list(queryset))

    # 기간 형식 설정
    df["period"] = df["period"].dt.strftime("%Y-%m")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 첫 번째 y축: 입출금 횟수 (막대 그래프)
    ax1.bar(df["period"], df["transaction_count"], color="skyblue", label="입출금 횟수")
    ax1.set_xlabel("기간")
    ax1.set_ylabel("입출금 횟수", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    # 두 번째 y축: 입금, 출금, 입금 - 출금 나머지 금액 그래프
    ax2 = ax1.twinx()
    ax2.plot(df["period"], df["withdrawal_total"], color="green", marker="o", label="출금 금액 합계")
    ax2.plot(df["period"], df["deposit_total"], color="red", marker="o", linestyle="--", label="입금 금액 합계")
    ax2.plot(df["period"], df["remain_total"], color="orange", marker="o", linestyle=":", label="남은 금액")  # 잔여 금액 추가
    ax2.set_ylabel("금액 (입금 & 출금)", color="green")
    ax2.tick_params(axis="y", labelcolor="green")

    # y축 눈금을 10만 원 단위로 설정
    ax2.yaxis.set_major_locator(mticker.MultipleLocator(300000))  # 10만 원 간격 설정
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x / 10000)}만 원"))  # 10,000으로 나누고 "만 원" 추가

    # 그래프 제목 및 범례 추가
    fig.suptitle("기간별 입출금 횟수 및 금액 합계")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.xticks(rotation=45)
    plt.tight_layout()

    pdf_path = "C:/Users/jangy/Downloads/Vitailic/plot_basic_visualization.pdf"
    plt.savefig(pdf_path)
    plt.close()

    return pdf_path  # PDF 경로 반환

# 월 초, 월 말 비교 그래프
def plot_balance_change_beginning_and_end_each_month_visualization(start_date, end_date):
    # 월 초 잔액: 매월 1일의 after_balance_amt
    beginning_queryset = (
        passbook.objects.filter(tran_date_time__range=[start_date, end_date], tran_date_time__day=1)
        .annotate(period=TruncMonth("tran_date_time"))
        .values("period")
        .annotate(
            beginning_balance=Sum("after_balance_amt")
        )
        .order_by("period")
    )

    # 월 말 잔액: 매월 마지막 날짜의 after_balance_amt
    ending_queryset = (
        passbook.objects.filter(tran_date_time__range=[start_date, end_date])
        .annotate(period=TruncMonth("tran_date_time"))
        .values("period")
        .annotate(
            ending_balance=Sum("after_balance_amt", filter=Q(tran_date_time__day=28) | Q(tran_date_time__day=30) | Q(tran_date_time__day=31))
        )
        .distinct()  # 각 월의 마지막 날만 추출
        .order_by("period")
    )

    # 데이터프레임 생성
    beginning_df = pd.DataFrame(list(beginning_queryset))
    ending_df = pd.DataFrame(list(ending_queryset))

    # 월 말 데이터가 있는 날짜로 변환
    ending_df['period'] = ending_df['period'].dt.to_period('M').dt.to_timestamp('M')  # 월 마지막 날로 변환

    # 기간 형식을 동일하게 맞추기
    beginning_df['period'] = beginning_df['period'].dt.tz_localize(None)  # UTC를 제거하여 단순 datetime으로 변환
    ending_df['period'] = ending_df['period'].dt.tz_localize(None)  # UTC를 제거하여 단순 datetime으로 변환

    # NaN 값을 0으로 대체
    beginning_df['beginning_balance'] = beginning_df['beginning_balance'].fillna(0)
    ending_df['ending_balance'] = ending_df['ending_balance'].fillna(0)

    # 'balance_type' 컬럼 추가
    beginning_df['balance_type'] = '월 초 잔액'
    ending_df['balance_type'] = '월 말 잔액'

    # 필요한 컬럼 선택 및 재구성
    beginning_df = beginning_df[['period', 'beginning_balance', 'balance_type']]
    ending_df = ending_df[['period', 'ending_balance', 'balance_type']].rename(columns={'ending_balance': 'beginning_balance'})  # 컬럼 이름 변경하여 동일하게

    # 두 데이터프레임 합치기
    combined_df = pd.concat([beginning_df, ending_df], ignore_index=True)

    # 시각화
    plt.figure(figsize=(12, 6))

    # 막대 그래프 그리기
    sns.histplot(data=combined_df, x='period', weights='beginning_balance', hue='balance_type', multiple='stack', kde=False, palette=['skyblue', 'lightcoral'])

    # x축 및 y축 레이블 설정
    plt.xlabel('기간', fontsize=12)
    plt.ylabel('잔액', fontsize=12)
    plt.title('매월 초와 말의 잔액 변화', fontsize=14)
    plt.xticks(rotation=45)

    # y축 눈금을 백 만원 단위로 설정
    ax = plt.gca()  # 현재 Axes 객체 가져오기
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100000000))  # 천만 원 단위로 눈금 설정
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x / 1000000):,} 만 원'))  # 백만원 단위로 포맷

    plt.tight_layout()

    pdf_path = "C:/Users/jangy/Downloads/Vitailic/plot_balance_change_beginning_and_end_each_month_visualization.pdf"
    plt.savefig(pdf_path)
    plt.close()

    return pdf_path  # PDF 경로 반환


# 카테고리별 사용 빈도, 평균 사용 시간대 산포도
def plot_category_time_using_avg(start_date, end_date):
    # 6개월 동안의 데이터 필터링
    transactions = passbook.objects.filter(tran_date_time__range=[start_date, end_date], tran_date_time__day=1)

    # 카테고리별 사용 빈도 집계
    category_counts = transactions.values('out_type').annotate(count=Count('id'))
    category_counts_df = pd.DataFrame(list(category_counts))  # list()로 감싸서 DataFrame 생성

    # 사용 시간대 분석을 위해 tran_date_time에서 시간 정보를 추출
    transaction_times = transactions.values('out_type', 'tran_date_time')
    transaction_times_df = pd.DataFrame(list(transaction_times))  # list()로 감싸서 DataFrame 생성
    transaction_times_df['hour'] = transaction_times_df['tran_date_time'].apply(lambda x: x.hour)

    # 카테고리별 평균 시간 계산
    avg_usage_time = transaction_times_df.groupby('out_type')['hour'].mean().reset_index(name='avg_hour')

    # 카테고리 이름 매핑
    category_counts_df['category_name'] = category_counts_df['out_type'].map(CATEGORY_MAPPING)
    avg_usage_time['category_name'] = avg_usage_time['out_type'].map(CATEGORY_MAPPING)

    # 카테고리별 사용 빈도와 평균 사용 시간대 병합
    final_df = pd.merge(category_counts_df, avg_usage_time, on='out_type')
    final_df = final_df.rename(columns={'category_name_x': 'category_name'})  # category_name 열을 하나로 통합

    # 산포도 그래프 생성
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=final_df, x='avg_hour', y='count', hue='category_name', s=100)
    plt.xlabel('사용 평균 시간대')
    plt.ylabel('거래 횟수')
    plt.title('6개월 동안 카테고리별 사용 빈도와 평균 사용 시간대')

    # x축 시간대를 '09시'부터 '24시'까지로 설정
    hours = [f"{int(h):02d}시" for h in range(9, 25)]
    plt.xticks(ticks=range(9, 25), labels=hours)

    plt.legend(title='Category')
    plt.grid(True)

    pdf_path = "C:/Users/jangy/Downloads/Vitailic/plot_category_time_using_avg.pdf"
    plt.savefig(pdf_path)
    plt.close()

    return pdf_path  # PDF 경로 반환

# 요일, 시간대별 패턴
def plot_week_and_time_pattern(start_date, end_date):
    # 지정된 기간 동안의 데이터 필터링
    transactions = passbook.objects.filter(tran_date_time__range=[start_date, end_date])

    # DataFrame으로 변환
    transactions_df = pd.DataFrame(list(transactions.values('tran_date_time', 'inout_type', 'tran_amt')))

    # 요일과 시간대 열 추가
    transactions_df['day_of_week'] = transactions_df['tran_date_time'].dt.dayofweek  # 0=월, 6=일
    transactions_df['hour'] = transactions_df['tran_date_time'].dt.hour

    # 요일별, 시간대별 사용 빈도 집계
    freq_df = transactions_df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')

    # 요일 이름을 한글로 변경
    day_labels = ['월', '화', '수', '목', '금', '토', '일']
    freq_df['day_of_week'] = freq_df['day_of_week'].apply(lambda x: day_labels[x])

    # 버블 차트 생성
    plt.figure(figsize=(12, 6))
    bubble = plt.scatter(
        x=freq_df['hour'],
        y=freq_df['day_of_week'],
        s=freq_df['count'] * 10,  # count에 따라 버블 크기 조절
        alpha=0.6,
        c=freq_df['count'],
        cmap="viridis",
        edgecolor='black',  # 버블 테두리 추가
        linewidth=1.5  # 테두리 두께 설정
    )
    plt.colorbar(bubble, label="사용 빈도")
    plt.xlabel("시간대 (24시간 기준)")
    plt.ylabel("요일")
    plt.title("요일 및 시간대별 사용 패턴 (버블 차트)")

    # 09시부터 24시까지 x축 설정
    plt.xticks(range(7, 25), [f"{h}시" for h in range(7, 25)])  # 09시부터 24시까지 표시

    plt.grid(True, linestyle='--', alpha=0.5)
    # 결과 그래프를 PDF 파일로 저장
    # PDF 파일로 저장
    pdf_path = "C:/Users/jangy/Downloads/Vitailic/plot_week_and_time_pattern.pdf"
    plt.savefig(pdf_path)
    plt.close()

    return pdf_path  # PDF 경로 반환

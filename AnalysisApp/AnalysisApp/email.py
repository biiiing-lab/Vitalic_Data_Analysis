# 생성된 pdf 파일을 이메일로 전송
# 차트 이메일 서비스
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from PyPDF2 import PdfMerger

from AnalysisApp.AnalysisApp.visualization import plot_basic_visualization, \
    plot_balance_change_beginning_and_end_each_month_visualization, plot_category_time_using_avg, \
    plot_week_and_time_pattern


def merge_pdfs(pdf_list, output_filename):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()

def send_email(start_date, end_date, email):
    # 차트 생성
    pdf_paths = []
    pdf_paths.append(plot_basic_visualization(start_date, end_date))
    pdf_paths.append(plot_balance_change_beginning_and_end_each_month_visualization(start_date, end_date))
    pdf_paths.append(plot_category_time_using_avg(start_date, end_date))
    pdf_paths.append(plot_week_and_time_pattern(start_date, end_date))

    # PDF 병합
    merged_pdf_path = "C:/Users/jangy/Downloads/Vitailic/merged_plots.pdf"
    merge_pdfs(pdf_paths, merged_pdf_path)

    from_email = os.getenv("VITALIC_EMAIL")
    password = os.getenv("VITALIC_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = email
    msg['Subject'] = "시각화 결과 PDF"

    msg.attach(MIMEApplication("첨부된 PDF 파일을 확인해 주세요.", 'plain'))

    with open(merged_pdf_path, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=os.path.basename(merged_pdf_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(merged_pdf_path)}"'
        msg.attach(part)

    # SMTP 서버 설정
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # TLS(전송 계층 보안) 시작
            server.login(from_email, password)  # 이메일 및 앱 비밀번호로 로그인
            server.send_message(msg)  # 이메일 전송
            print("이메일 전송 완료")
    except Exception as e:
        print(f"이메일 전송 실패: {e}")
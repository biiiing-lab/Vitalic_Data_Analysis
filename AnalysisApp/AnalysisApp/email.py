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

# pdf 병합
def merge_pdfs(pdf_list, output_filename):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()

def send_email(start_date, end_date, email):

    # 차트 가져오기
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

    msg = MIMEMultipart() # 이메일 메세지를 여러 부분을 구성할 수 있는 객체, 본문과 첨부 파일 추가
    msg['From'] = from_email # 발신자
    msg['To'] = email # 수신자
    msg['Subject'] = "시각화 결과 PDF" # 이메일 제목

    # 이메일 본문에 텍스트 추가, 평문 형식으로 되어있음
    msg.attach(MIMEApplication("첨부된 PDF 파일을 확인해 주세요.", 'plain'))

    #  PDF 파일 첨부
    with open(merged_pdf_path, "rb") as attachment: # path  경로의 파일을 읽기 모드로 열고, 변수에 저장
        part = MIMEApplication(attachment.read(), Name=os.path.basename(merged_pdf_path)) # 파일 이름 지정, 첨부파일로 인식
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(merged_pdf_path)}"' # 헤더에 첨부 파일로서의 정보 추가, 이메일 클라이언트에서 파일을 attachment 형식으로 인식
        msg.attach(part) # 첨부파일을 msg 객체에 추가하여 이메일 포함

    # SMTP 서버 설정
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # TLS(전송 계층 보안) 시작
            server.login(from_email, password)  # 이메일 및 앱 비밀번호로 로그인
            server.send_message(msg)  # 이메일 전송
            print("이메일 전송 완료")
    except Exception as e:
        print(f"이메일 전송 실패: {e}")
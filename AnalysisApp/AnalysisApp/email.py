
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    msg['Subject'] = f"{email}님의 분석 결과 PDF" # 이메일 제목

    msg.attach(MIMEText("첨부된 PDF 파일을 확인해 주세요", 'utf-8'))

    #  PDF 파일 첨부
    with open(merged_pdf_path, "rb") as attachment: # path  경로의 파일을 읽기 모드로 열고, 변수에 저장
        part = MIMEApplication(attachment.read(), Name=os.path.basename(merged_pdf_path)) # 파일 이름 지정, 첨부파일로 인식
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(merged_pdf_path)}"' # 헤더에 첨부 파일로서의 정보 추가, 이메일 클라이언트에서 파일을 attachment 형식으로 인식
        msg.attach(part) # 첨부파일을 msg 객체에 추가하여 이메일 포함

    # SMTP 서버 설정
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, local_hostname='localhost') as server: # hostname ascii 표현 수정
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            print("이메일 전송 완료")
            return True
    except Exception as e:
        print(f"이메일 전송 실패: {e}")
        return False
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from AnalysisApp.AnalysisApp.visualization import (
    plot_basic_visualization,
    plot_balance_change_beginning_and_end_each_month_visualization,
    plot_category_time_using_avg,
    plot_week_and_time_pattern
)

def conbined_make_pdf(image_paths, output_pdf_path):
    # 이미지 파일을 불러와서 PIL Image 객체로 변환
    images = [Image.open(img_path) for img_path in image_paths]

    # PDF 파일을 생성
    with PdfPages(output_pdf_path) as pdf:
        # A4 가로 비율에 맞춰 크기 설정, dpi를 높여 화질 개선
        fig, axs = plt.subplots(2, 2, figsize=(11.7, 8.3), dpi=300)  # A4 가로 비율 (11.7 x 8.3 inches)

        # 각 이미지에 대해 subplot에 배치
        for i, ax in enumerate(axs.flat):
            if i < len(images):  # 이미지가 있는 경우에만 추가
                ax.imshow(images[i])
            ax.axis('off')  # 축 숨기기

        # 여백을 최소화하고 페이지 저장
        plt.tight_layout(pad=0.5)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    print(f"PDF 파일이 성공적으로 생성되었습니다: {output_pdf_path}")



def send_email(start_date, end_date, email):
    # Get image paths instead of PDF paths
    image_paths = [
        plot_basic_visualization(start_date, end_date),
        plot_balance_change_beginning_and_end_each_month_visualization(start_date, end_date),
        plot_category_time_using_avg(start_date, end_date),
        plot_week_and_time_pattern(start_date, end_date)
    ]

    # Create the combined PDF
    combined_pdf_path = "C:/Users/jangy/Downloads/Vitailic/all_result.pdf"
    conbined_make_pdf(image_paths, combined_pdf_path)

    from_email = os.getenv("VITALIC_EMAIL")
    password = os.getenv("VITALIC_PASSWORD")

    msg = MIMEMultipart() # 이메일 메세지를 여러 부분을 구성할 수 있는 객체, 본문과 첨부 파일 추가
    msg['From'] = from_email # 발신자
    msg['To'] = email # 수신자
    msg['Subject'] = f"{email}님의 분석 결과 PDF" # 이메일 제목

    msg.attach(MIMEText("첨부된 PDF 파일을 확인해 주세요"))

    #  PDF 파일 첨부
    with open(combined_pdf_path, "rb") as attachment: # path  경로의 파일을 읽기 모드로 열고, 변수에 저장
        part = MIMEApplication(attachment.read(), Name=os.path.basename(combined_pdf_path)) # 파일 이름 지정, 첨부파일로 인식
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(combined_pdf_path)}"' # 헤더에 첨부 파일로서의 정보 추가, 이메일 클라이언트에서 파일을 attachment 형식으로 인식
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
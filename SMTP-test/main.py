import smtplib
from email.message import EmailMessage

# STMP 서버의 url과 port 번호
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

# 1. SMTP 서버 연결
smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

EMAIL_ADDR = 'm23235180@gmail.com'
EMAIL_PASSWORD = 'bpzwmnstpwrxmevk'

# 2. SMTP 서버에 로그인
smtp.login(EMAIL_ADDR, EMAIL_PASSWORD)

# 3. MIME 형태의 이메일 메세지 작성
message = EmailMessage()
message.set_content('이메일 본문')
message["Subject"] = "이메일 제목"
message["From"] = EMAIL_ADDR  #보내는 사람의 이메일 계정
message["To"] = 'dreampilot920@naver.com'

# 4. 서버로 메일 보내기
smtp.send_message(message)

# 5. 메일을 보내면 서버와의 연결 끊기
smtp.quit()
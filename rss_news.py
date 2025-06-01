import feedparser
import smtplib
import ssl
from email.message import EmailMessage
import re
import os  # ✅ 환경변수 사용을 위한 모듈

# ✅ 키워드 및 RSS 목록
keywords = ["네이버", "AI", "플랫폼", "포털", "제휴", "인공지능", "방통위", "과기부", "과방위"]
rss_sources = {
    "조선일보": "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml",
    "중앙일보": "https://www.joongang.co.kr/rss",
    "한겨레": "https://www.hani.co.kr/rss/",
}

# ✅ HTML 제거 및 요약 정리
def clean_text(text):
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.replace('\n', ' ').strip()[:150]

# ✅ 기사 HTML 포맷
def format_article(entry, source_name):
    title = entry.title
    link = entry.link
    summary = clean_text(entry.get('summary', ''))
    published = entry.get('published', '발행일 정보 없음')

    return (
        f"<b>[{source_name}]</b> <a href='{link}'>{title}</a><br>"
        f"🕒 {published}<br>"
        f"📄 {summary}<br><br>"
    )

# ✅ 기사 수집
def collect_articles():
    articles = []
    for name, url in rss_sources.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:50]:
            content = (entry.title + entry.get('summary', '')).lower()
            if any(keyword.lower() in content for keyword in keywords):
                articles.append(format_article(entry, name))
    return articles

# ✅ 이메일 전송 함수
def send_email(subject, body_html, sender_email, receiver_email, app_password):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("HTML 메일을 지원하지 않는 환경에서는 보일 수 없습니다.")
    msg.add_alternative(body_html, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

# ✅ 메인 로직
if __name__ == "__main__":
    articles = collect_articles()

    if articles:
        email_body = "<h2>📰 오늘의 주요 뉴스</h2><hr>" + ''.join(articles)
    else:
        email_body = "<h3>오늘은 키워드에 해당하는 뉴스가 없습니다.</h3>"

    # ✅ 환경변수에서 이메일 정보 불러오기
    sender = os.getenv("EMAIL_ADDRESS")
    receiver = os.getenv("RECEIVER_EMAIL")
    app_pw = os.getenv("EMAIL_PASSWORD")

    # ✅ 전송
    send_email(
        subject="📬 오늘의 주요 뉴스 브리핑",
        body_html=email_body,
        sender_email=sender,
        receiver_email=receiver,
        app_password=app_pw
    )

    print("✅ 이메일 전송 완료!")

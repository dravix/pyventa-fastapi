import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


async def get_template(template_name: str, context: dict) -> str:
    # In a real implementation, you would load and render an HTML template here.
    # For simplicity, we'll just return a simple HTML string.

    if template_name == "verify-email":
        return templates.get_template("verification_en.html").render(context)
    return ""


async def send_email(to: str, subject: str, template: str, context: dict):
    username = os.environ.get("SMTP_USERNAME", "USERNAME")
    password = os.environ.get("SMTP_PASSWORD", "PASSWORD")
    sender = os.environ.get("SMTP_FROM", "no-reply@pyventa.com")
    msg = MIMEMultipart("mixed")

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    # text_message = MIMEText(message, "plain")
    html_message = MIMEText(await get_template(template, context), "html")
    # msg.attach(text_message)
    msg.attach(html_message)

    mailServer = smtplib.SMTP(
        os.environ.get("SMTP_HOST", "mail.smtp2go.com"),
        int(os.environ.get("SMTP_PORT", "2525")),
    )  #  8025, 587 and 25 can also be used.
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, to, msg.as_string())
    mailServer.close()

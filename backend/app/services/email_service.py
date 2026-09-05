import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional
import aiosmtplib
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an asynchronous email via SMTP."""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.info(f"[EMAIL MOCK] To: {to_email} | Subject: {subject}")
            logger.debug(f"[EMAIL CONTENT]\n{html_content}")
            return True

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        message["To"] = to_email

        if text_content:
            message.attach(MIMEText(text_content, "plain", "utf-8"))
        message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.USE_TLS,
                timeout=10,
            )
            logger.info(f"Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_otp_email(self, to_email: str, otp: str, purpose: str = "Email Verification") -> bool:
        subject = f"{purpose} Code - {settings.APP_NAME}"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
                .card {{ max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                .logo {{ color: #2563eb; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
                .code {{ font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e293b; background: #f1f5f9; padding: 12px 24px; border-radius: 6px; display: inline-block; margin: 20px 0; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #64748b; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="logo">{settings.APP_NAME}</div>
                <h2>Your {purpose} Code</h2>
                <p>Please enter the following one-time password (OTP) to complete your request. This code will expire in 10 minutes.</p>
                <div class="code">{otp}</div>
                <p>If you didn't request this code, you can safely ignore this email.</p>
                <div class="footer">© {settings.APP_NAME} Platform. All rights reserved.</div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html, text_content=f"Your OTP code is {otp}")

    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        subject = f"Welcome to {settings.APP_NAME}!"
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Welcome, {name}!</h2>
            <p>We're thrilled to have you join CourseDrive. Start exploring thousands of high-quality courses curated by top educators worldwide.</p>
            <p><a href="{settings.FRONTEND_URL}/courses" style="background:#2563eb;color:#fff;padding:10px 20px;text-decoration:none;border-radius:5px;">Explore Courses</a></p>
        </div>
        """
        return await self.send_email(to_email, subject, html)

    async def send_certificate_email(self, to_email: str, student_name: str, course_title: str, cert_url: str) -> bool:
        subject = f"Congratulations! Your Certificate for '{course_title}' is ready!"
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Congratulations, {student_name}!</h2>
            <p>You have successfully completed <strong>{course_title}</strong>.</p>
            <p>Your verified digital certificate of completion has been issued.</p>
            <p><a href="{cert_url}" style="background:#16a34a;color:#fff;padding:10px 20px;text-decoration:none;border-radius:5px;">View Certificate</a></p>
        </div>
        """
        return await self.send_email(to_email, subject, html)


email_service = EmailService()

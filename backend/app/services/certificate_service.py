import io
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.certificate import Certificate
from app.models.course import Course
from app.models.user import User
from app.services.storage_service import storage_service
from app.services.email_service import email_service


class CertificateService:
    def generate_pdf_bytes(
        self,
        student_name: str,
        course_title: str,
        instructor_name: str,
        certificate_number: str,
        issue_date: datetime,
    ) -> bytes:
        """Generate a professionally styled PDF certificate in memory."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="CertTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=32,
            leading=38,
            textColor=colors.HexColor("#1e293b"),
            alignment=1,  # Center
        )
        subtitle_style = ParagraphStyle(
            name="CertSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#64748b"),
            alignment=1,
        )
        name_style = ParagraphStyle(
            name="CertName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=colors.HexColor("#2563eb"),
            alignment=1,
        )
        course_style = ParagraphStyle(
            name="CertCourse",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            alignment=1,
        )
        meta_style = ParagraphStyle(
            name="CertMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#94a3b8"),
            alignment=1,
        )

        formatted_date = issue_date.strftime("%B %d, %Y")

        elements = [
            Spacer(1, 0.4 * inch),
            Paragraph("COURSEDRIVE ACADEMY", subtitle_style),
            Spacer(1, 0.1 * inch),
            Paragraph("CERTIFICATE OF COMPLETION", title_style),
            Spacer(1, 0.3 * inch),
            Paragraph("This is proudly presented to", subtitle_style),
            Spacer(1, 0.15 * inch),
            Paragraph(student_name, name_style),
            Spacer(1, 0.2 * inch),
            Paragraph("for successfully completing all requirements of the online course", subtitle_style),
            Spacer(1, 0.15 * inch),
            Paragraph(course_title, course_style),
            Spacer(1, 0.4 * inch),
        ]

        # Instructor and Date table
        table_data = [
            [
                Paragraph(f"<b>Instructor:</b> {instructor_name}", ParagraphStyle("Left", parent=styles["Normal"], fontSize=11, alignment=0)),
                Paragraph(f"<b>Issue Date:</b> {formatted_date}", ParagraphStyle("Right", parent=styles["Normal"], fontSize=11, alignment=2)),
            ]
        ]
        t = Table(table_data, colWidths=[4.5 * inch, 4.5 * inch])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"Certificate ID: {certificate_number} | Verify at coursedrive.com/verify", meta_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    async def issue_certificate(
        self,
        db: AsyncSession,
        user_id: int,
        course_id: int,
    ) -> Certificate:
        """Create or return existing certificate for user and course."""
        query = select(Certificate).where(
            Certificate.user_id == user_id,
            Certificate.course_id == course_id,
        )
        existing = await db.scalar(query)
        if existing:
            return existing

        user_q = select(User).where(User.id == user_id)
        user = await db.scalar(user_q)

        course_q = select(Course).where(Course.id == course_id).options(selectinload(Course.instructor))
        course = await db.scalar(course_q)

        if not user or not course:
            raise ValueError("User or Course not found")

        cert_number = f"CD-{uuid.uuid4().hex[:10].upper()}"
        issue_date = datetime.now(timezone.utc)

        instructor_name = course.instructor.full_name if course.instructor else "CourseDrive Instructor"

        pdf_bytes = self.generate_pdf_bytes(
            student_name=user.full_name,
            course_title=course.title,
            instructor_name=instructor_name,
            certificate_number=cert_number,
            issue_date=issue_date,
        )

        filename = f"{cert_number}.pdf"
        pdf_url = storage_service.save_bytes(pdf_bytes, filename, folder="certificates")

        cert = Certificate(
            user_id=user_id,
            course_id=course_id,
            certificate_number=cert_number,
            issue_date=issue_date,
            pdf_url=pdf_url,
        )
        db.add(cert)
        await db.flush()
        await db.refresh(cert)

        # Notify via email
        await email_service.send_certificate_email(
            to_email=user.email,
            student_name=user.full_name,
            course_title=course.title,
            cert_url=pdf_url,
        )

        return cert

    async def verify_certificate(
        self,
        db: AsyncSession,
        certificate_number: str,
    ) -> Tuple[bool, Optional[Certificate]]:
        query = (
            select(Certificate)
            .where(Certificate.certificate_number == certificate_number.strip().upper())
            .options(
                selectinload(Certificate.user),
                selectinload(Certificate.course).selectinload(Course.instructor),
            )
        )
        cert = await db.scalar(query)
        if not cert:
            return False, None
        return True, cert


certificate_service = CertificateService()

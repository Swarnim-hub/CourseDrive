import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.category import Category
from app.models.course import Course, CourseLevel
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.lesson import Lesson, LessonType
from app.models.review import Review
from app.models.section import Section
from app.models.user import User, UserRole
from app.schemas.courses import CourseCreate, CourseUpdate
from app.schemas.sections import SectionCreate, SectionUpdate
from app.schemas.lessons import LessonCreate, LessonUpdate


def slugify(text: str) -> str:
    """Generate a clean URL slug from text."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


class CourseService:
    async def generate_unique_slug(self, db: AsyncSession, title: str, course_id: Optional[int] = None) -> str:
        base_slug = slugify(title)
        if not base_slug:
            base_slug = "course"
        slug = base_slug
        counter = 1
        while True:
            query = select(Course.id).where(Course.slug == slug)
            if course_id:
                query = query.where(Course.id != course_id)
            result = await db.scalar(query)
            if not result:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    async def create_course(self, db: AsyncSession, instructor_id: int, data: CourseCreate) -> Course:
        slug = await self.generate_unique_slug(db, data.title)
        
        course = Course(
            instructor_id=instructor_id,
            category_id=data.category_id,
            title=data.title,
            slug=slug,
            subtitle=data.subtitle,
            description=data.description,
            requirements=data.requirements,
            what_you_will_learn=data.what_you_will_learn,
            level=data.level,
            language=data.language,
            price=0.0 if data.is_free else data.price,
            is_free=data.is_free,
            promotional_video_url=data.promotional_video_url,
            thumbnail_url=data.thumbnail_url,
            is_published=True,
        )
        db.add(course)
        await db.flush()
        await db.refresh(course)
        return course

    async def update_course(
        self,
        db: AsyncSession,
        course_id: int,
        user: User,
        data: CourseUpdate,
    ) -> Course:
        course = await self.get_course_by_id(db, course_id)
        if not course:
            raise NotFoundException("Course", course_id)

        # Check ownership or admin
        if user.role != UserRole.ADMIN and course.instructor_id != user.id:
            raise ForbiddenException("You can only modify your own courses")

        update_dict = data.model_dump(exclude_unset=True)
        if "title" in update_dict and update_dict["title"] != course.title:
            update_dict["slug"] = await self.generate_unique_slug(db, update_dict["title"], course_id)

        if "is_free" in update_dict and update_dict["is_free"]:
            update_dict["price"] = 0.0

        for field, val in update_dict.items():
            setattr(course, field, val)

        await db.flush()
        await db.refresh(course)
        return course

    async def get_course_by_id(self, db: AsyncSession, course_id: int) -> Optional[Course]:
        query = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.instructor),
                selectinload(Course.category),
                selectinload(Course.sections).selectinload(Section.lessons),
            )
        )
        return await db.scalar(query)

    async def get_course_by_slug(self, db: AsyncSession, slug: str) -> Optional[Course]:
        query = (
            select(Course)
            .where(Course.slug == slug)
            .options(
                selectinload(Course.instructor),
                selectinload(Course.category),
                selectinload(Course.sections).selectinload(Section.lessons),
            )
        )
        return await db.scalar(query)

    async def list_courses(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        level: Optional[CourseLevel] = None,
        is_free: Optional[bool] = None,
        is_published: Optional[bool] = True,
        instructor_id: Optional[int] = None,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 12,
    ) -> Tuple[List[Course], int]:
        query = select(Course).options(
            selectinload(Course.instructor),
            selectinload(Course.category),
        )

        if is_published is not None:
            query = query.where(Course.is_published == is_published)
        if instructor_id:
            query = query.where(Course.instructor_id == instructor_id)
        if category_id:
            query = query.where(Course.category_id == category_id)
        if level:
            query = query.where(Course.level == level)
        if is_free is not None:
            query = query.where(Course.is_free == is_free)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Course.title.ilike(search_pattern)) | (Course.description.ilike(search_pattern))
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.scalar(count_query)) or 0

        # Sorting
        if sort_by == "newest":
            query = query.order_by(desc(Course.created_at))
        elif sort_by == "oldest":
            query = query.order_by(asc(Course.created_at))
        elif sort_by == "price_low":
            query = query.order_by(asc(Course.price))
        elif sort_by == "price_high":
            query = query.order_by(desc(Course.price))
        else:
            query = query.order_by(desc(Course.created_at))

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        courses = list(result.scalars().all())
        return courses, total

    async def get_course_stats(self, db: AsyncSession, course_id: int) -> Dict[str, Any]:
        """Fetch rating average, review count, and enrolled count for a course."""
        enroll_count_q = select(func.count(Enrollment.id)).where(
            Enrollment.course_id == course_id,
            Enrollment.status.in_([EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED]),
        )
        enroll_count = (await db.scalar(enroll_count_q)) or 0

        review_stats_q = select(
            func.coalesce(func.avg(Review.rating), 0.0),
            func.count(Review.id),
        ).where(Review.course_id == course_id)
        avg_rating, review_count = (await db.execute(review_stats_q)).one()

        return {
            "enrolled_count": enroll_count,
            "rating": round(float(avg_rating), 1),
            "reviews_count": review_count,
        }

    async def recalculate_duration(self, db: AsyncSession, course_id: int) -> int:
        """Recalculate total duration of all lessons in course."""
        query = (
            select(func.coalesce(func.sum(Lesson.duration_seconds), 0))
            .select_from(Lesson)
            .join(Section, Lesson.section_id == Section.id)
            .where(Section.course_id == course_id)
        )
        total_seconds = (await db.scalar(query)) or 0
        course_q = select(Course).where(Course.id == course_id)
        course = await db.scalar(course_q)
        if course:
            course.total_duration_seconds = total_seconds
            await db.flush()
        return total_seconds

    # Sections
    async def create_section(self, db: AsyncSession, user: User, data: SectionCreate) -> Section:
        course = await self.get_course_by_id(db, data.course_id)
        if not course:
            raise NotFoundException("Course", data.course_id)
        if user.role != UserRole.ADMIN and course.instructor_id != user.id:
            raise ForbiddenException("Unauthorized to add section to this course")

        section = Section(
            course_id=data.course_id,
            title=data.title,
            order_index=data.order_index,
        )
        db.add(section)
        await db.flush()
        
        # Load with lessons eager to prevent MissingGreenlet in Pydantic serialization
        query = select(Section).where(Section.id == section.id).options(selectinload(Section.lessons))
        return await db.scalar(query)

    async def update_section(self, db: AsyncSession, section_id: int, user: User, data: SectionUpdate) -> Section:
        query = select(Section).where(Section.id == section_id).options(selectinload(Section.course))
        section = await db.scalar(query)
        if not section:
            raise NotFoundException("Section", section_id)
        if user.role != UserRole.ADMIN and section.course.instructor_id != user.id:
            raise ForbiddenException("Unauthorized to modify this section")

        update_dict = data.model_dump(exclude_unset=True)
        for field, val in update_dict.items():
            setattr(section, field, val)

        await db.flush()
        query = select(Section).where(Section.id == section_id).options(selectinload(Section.lessons))
        return await db.scalar(query)

    async def delete_section(self, db: AsyncSession, section_id: int, user: User) -> bool:
        query = select(Section).where(Section.id == section_id).options(selectinload(Section.course))
        section = await db.scalar(query)
        if not section:
            raise NotFoundException("Section", section_id)
        if user.role != UserRole.ADMIN and section.course.instructor_id != user.id:
            raise ForbiddenException("Unauthorized to delete this section")

        course_id = section.course_id
        await db.delete(section)
        await db.flush()
        await self.recalculate_duration(db, course_id)
        return True

    # Lessons
    async def create_lesson(self, db: AsyncSession, user: User, data: LessonCreate) -> Lesson:
        query = select(Section).where(Section.id == data.section_id).options(selectinload(Section.course))
        section = await db.scalar(query)
        if not section:
            raise NotFoundException("Section", data.section_id)
        if user.role != UserRole.ADMIN and section.course.instructor_id != user.id:
            raise ForbiddenException("Unauthorized to add lesson to this section")

        lesson = Lesson(
            section_id=data.section_id,
            title=data.title,
            lesson_type=data.lesson_type,
            content=data.content,
            video_url=data.video_url,
            duration_seconds=data.duration_seconds,
            is_preview=data.is_preview,
            order_index=data.order_index,
        )
        db.add(lesson)
        await db.flush()
        await db.refresh(lesson)
        await self.recalculate_duration(db, section.course_id)
        return lesson

    async def update_lesson(self, db: AsyncSession, lesson_id: int, user: User, data: LessonUpdate) -> Lesson:
        query = select(Lesson).where(Lesson.id == lesson_id).options(
            selectinload(Lesson.section).selectinload(Section.course)
        )
        lesson = await db.scalar(query)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        if user.role != UserRole.ADMIN and lesson.section.course.instructor_id != user.id:
            raise ForbiddenException("Unauthorized to modify this lesson")

        update_dict = data.model_dump(exclude_unset=True)
        for field, val in update_dict.items():
            setattr(lesson, field, val)

        await db.flush()
        await db.refresh(lesson)
        await self.recalculate_duration(db, lesson.section.course_id)
        return lesson

    async def delete_lesson(self, db: AsyncSession, lesson_id: int, user: User) -> bool:
        query = select(Lesson).where(Lesson.id == lesson_id).options(
            selectinload(Lesson.section).selectinload(Section.course)
        )
        lesson = await db.scalar(query)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        if user.role != UserRole.ADMIN and lesson.section.course.instructor_id != user.id:
            raise ForbiddenException("Unauthorized to delete this lesson")

        course_id = lesson.section.course_id
        await db.delete(lesson)
        await db.flush()
        await self.recalculate_duration(db, course_id)
        return True


course_service = CourseService()

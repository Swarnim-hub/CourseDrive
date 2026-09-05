from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.quiz import QuestionType


class QuizQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=2)
    question_type: QuestionType = QuestionType.SINGLE_CHOICE
    options: List[Dict[str, Any]] = [] # e.g. [{"id": "a", "text": "Option A"}, {"id": "b", "text": "Option B"}]
    points: int = 1
    explanation: Optional[str] = None
    order_index: int = 0


class QuizQuestionCreate(QuizQuestionBase):
    correct_answers: List[str] = [] # list of correct option IDs or string values


class QuizQuestionResponse(QuizQuestionBase):
    id: int
    quiz_id: int

    model_config = ConfigDict(from_attributes=True)


class QuizQuestionAdminResponse(QuizQuestionResponse):
    correct_answers: List[str] = []


class QuizBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    passing_score: int = Field(70, ge=1, le=100)
    time_limit_minutes: Optional[int] = None


class QuizCreate(QuizBase):
    course_id: int
    lesson_id: Optional[int] = None
    questions: Optional[List[QuizQuestionCreate]] = []


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    passing_score: Optional[int] = Field(None, ge=1, le=100)
    time_limit_minutes: Optional[int] = None


class QuizResponse(QuizBase):
    id: int
    course_id: int
    lesson_id: Optional[int] = None
    created_at: datetime
    questions_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class QuizDetailResponse(QuizResponse):
    questions: List[QuizQuestionResponse] = []


class QuizAttemptSubmit(BaseModel):
    answers: Dict[str, Any] # e.g. {"question_id_or_index": ["selected_option_id"]}


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: float
    passed: bool
    answers_json: Dict[str, Any]
    started_at: datetime
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)

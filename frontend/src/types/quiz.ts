export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  prompt: string;
  options: QuizOption[];
  explanation?: string;
  order_index: number;
}

export interface Quiz {
  id: string;
  lesson_id?: string;
  course_id: string;
  title: string;
  description?: string;
  passing_score_percent: number;
  questions: QuizQuestion[];
}

export interface QuizSubmissionPayload {
  answers: Record<string, string>;
}

export interface QuizResult {
  score_percent: number;
  passed: boolean;
  total_questions: number;
  correct_count: number;
  answers_analysis: {
    question_id: string;
    is_correct: boolean;
    correct_option_id: string;
    explanation?: string;
  }[];
}

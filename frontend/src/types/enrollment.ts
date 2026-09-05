import { Course } from "./course";

export interface LessonProgress {
  lesson_id: string;
  completed: boolean;
  last_watched_second: number;
  completed_at?: string;
}

export interface Enrollment {
  id: string;
  user_id: string;
  course_id: string;
  course: Course;
  progress_percent: number;
  completed_lessons: string[];
  last_lesson_id?: string;
  certificate_id?: string;
  enrolled_at: string;
  completed_at?: string;
}

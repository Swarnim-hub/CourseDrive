import { User } from "./user";

export type DifficultyLevel = "beginner" | "intermediate" | "advanced" | "all_levels";
export type CourseStatus = "draft" | "published" | "archived";

export interface LessonResource {
  id: string;
  title: string;
  file_url: string;
  file_size?: number;
  resource_type: string;
}

export interface Lesson {
  id: string;
  section_id: string;
  title: string;
  description?: string;
  video_url?: string;
  duration_minutes: number;
  order_index: number;
  is_preview: boolean;
  resources?: LessonResource[];
  quiz_id?: string;
}

export interface Section {
  id: string;
  course_id: string;
  title: string;
  order_index: number;
  lessons: Lesson[];
}

export interface CourseReview {
  id: string;
  user_id: string;
  user: User;
  course_id: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface Course {
  id: string;
  slug: string;
  title: string;
  subtitle?: string;
  description: string;
  category?: any;
  category_id?: number | null;
  difficulty?: DifficultyLevel;
  level?: string;
  price: number;
  is_free?: boolean;
  is_published?: boolean;
  discount_price?: number | null;
  thumbnail_url?: string;
  trailer_video_url?: string;
  instructor_id?: string;
  instructor?: User;
  status?: CourseStatus;
  learning_objectives?: string[];
  what_you_will_learn?: string[];
  requirements?: string[];
  sections?: Section[];
  average_rating?: number;
  total_reviews?: number;
  total_students?: number;
  total_duration_minutes?: number;
  total_lessons?: number;
  created_at?: string;
  updated_at?: string;
}

export interface CourseFilterParams {
  category_id?: number;
  level?: string;
  price_type?: "all" | "free" | "paid";
  rating?: number;
  search?: string;
  instructor_id?: string;
  sort_by?: "popularity" | "rating" | "newest" | "price_asc" | "price_desc";
  page?: number;
  limit?: number;
}

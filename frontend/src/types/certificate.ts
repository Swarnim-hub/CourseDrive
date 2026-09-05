export interface Certificate {
  id: string;
  certificate_code: string;
  user_id: string;
  user_name: string;
  course_id: string;
  course_title: string;
  instructor_name: string;
  issue_date: string;
  verification_url: string;
  pdf_download_url?: string;
}

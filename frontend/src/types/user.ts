export type UserRole = "student" | "instructor" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  avatar_url?: string | null;
  bio?: string | null;
  headline?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

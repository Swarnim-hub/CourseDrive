export const API_BASE_URL = typeof window !== "undefined" ? "/api/v1" : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");



export const DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "all_levels"] as const;

export const ROLES = {
  STUDENT: "student",
  INSTRUCTOR: "instructor",
  ADMIN: "admin",
} as const;

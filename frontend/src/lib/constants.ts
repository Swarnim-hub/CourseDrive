export const API_BASE_URL = typeof window !== "undefined" ? "/api/v1" : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");

export const COURSE_CATEGORIES = [
  { id: "development", name: "Development", icon: "Code", count: "120+ courses" },
  { id: "business", name: "Business", icon: "Briefcase", count: "85+ courses" },
  { id: "data-science", name: "Data Science & AI", icon: "BrainCircuit", count: "95+ courses" },
  { id: "design", name: "Design & UX", icon: "Palette", count: "60+ courses" },
  { id: "marketing", name: "Marketing", icon: "TrendingUp", count: "45+ courses" },
  { id: "cybersecurity", name: "Cybersecurity", icon: "Shield", count: "40+ courses" },
] as const;

export const DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "all_levels"] as const;

export const ROLES = {
  STUDENT: "student",
  INSTRUCTOR: "instructor",
  ADMIN: "admin",
} as const;

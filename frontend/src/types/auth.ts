import { User } from "./user";

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  tokens?: AuthTokens;
  message?: string;
}

export interface LoginPayload {
  email: string;
  password?: string;
  otp?: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role?: "student" | "instructor";
}

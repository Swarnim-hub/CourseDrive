import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Enrollment } from "@/types/enrollment";

export function useMyEnrollments() {
  return useQuery({
    queryKey: ["my-enrollments"],
    queryFn: async () => {
      const res = await api.get<Enrollment[]>("/enrollments/me");
      return res.data;
    },
  });
}

export function useEnrollment(courseId: string) {
  return useQuery({
    queryKey: ["enrollment", courseId],
    queryFn: async () => {
      const res = await api.get<Enrollment>(`/enrollments/course/${courseId}`);
      return res.data;
    },
    enabled: Boolean(courseId),
  });
}

export function useEnrollCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (courseId: string) => {
      const res = await api.post<Enrollment>("/enrollments", { course_id: Number(courseId) });
      return res.data;
    },
    onSuccess: (_, courseId) => {
      queryClient.invalidateQueries({ queryKey: ["enrollment", courseId] });
      queryClient.invalidateQueries({ queryKey: ["my-enrollments"] });
    },
  });
}

export function useUpdateProgress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { courseId: string; lessonId: string; completed?: boolean; lastWatchedSecond?: number }) => {
      const res = await api.post(`/enrollments/${payload.courseId}/progress`, {
        lesson_id: payload.lessonId,
        completed: payload.completed,
        last_watched_second: payload.lastWatchedSecond,
      });
      return res.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["enrollment", variables.courseId] });
      queryClient.invalidateQueries({ queryKey: ["my-enrollments"] });
    },
  });
}

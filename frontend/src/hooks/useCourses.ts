import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Course, CourseFilterParams } from "@/types/course";

export function useCourses(courseParams?: CourseFilterParams) {
  return useQuery({
    queryKey: ["courses", courseParams],
    queryFn: async () => {
      const res = await api.get<{ items: Course[]; total: number; page: number }>("/courses", {
        params: courseParams,
      });
      return { courses: res.data.items || [], total: res.data.total, page: res.data.page };
    },
  });
}

export function useCourse(slugOrId: string) {
  return useQuery({
    queryKey: ["course", slugOrId],
    queryFn: async () => {
      const res = await api.get<Course>(`/courses/${slugOrId}`);
      return res.data;
    },
    enabled: Boolean(slugOrId),
  });
}

export function useCreateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Course>) => {
      const res = await api.post<Course>("/courses", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useUpdateCourse(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Course>) => {
      const res = await api.put<Course>(`/courses/${courseId}`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

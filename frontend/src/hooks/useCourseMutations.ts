import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Lesson, Section } from "@/types/course";

export function useCreateSection(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { title: string; order_index?: number }) => {
      const res = await api.post<Section>(`/courses/${courseId}/sections`, {
        title: payload.title,
        order: payload.order_index ?? 0,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useUpdateSection(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ sectionId, title, order_index }: { sectionId: string; title: string; order_index?: number }) => {
      const res = await api.put<Section>(`/courses/sections/${sectionId}`, {
        title,
        order: order_index,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useDeleteSection(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (sectionId: string) => {
      await api.delete(`/courses/sections/${sectionId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useCreateLesson(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      section_id: number;
      title: string;
      lesson_type?: string;
      content?: string;
      video_url?: string;
      pdf_url?: string;
      duration_seconds?: number;
      is_preview?: boolean;
      order?: number;
    }) => {
      const res = await api.post<Lesson>("/lessons", payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useUpdateLesson(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      lessonId,
      ...payload
    }: {
      lessonId: string;
      title?: string;
      content?: string;
      video_url?: string;
      pdf_url?: string;
      duration_seconds?: number;
      is_preview?: boolean;
      order?: number;
    }) => {
      const res = await api.put<Lesson>(`/lessons/${lessonId}`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useDeleteLesson(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (lessonId: string) => {
      await api.delete(`/lessons/${lessonId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course", courseId] });
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useUploadLessonVideo() {
  return useMutation({
    mutationFn: async ({ lessonId, file }: { lessonId: string; file: File }) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post<{ video_url: string }>(`/lessons/${lessonId}/video`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
  });
}

export function useUploadLessonPdf() {
  return useMutation({
    mutationFn: async ({ lessonId, file }: { lessonId: string; file: File }) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post<{ pdf_url: string }>(`/lessons/${lessonId}/pdf`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
  });
}

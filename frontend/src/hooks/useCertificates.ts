import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface CertificateItem {
  id: number;
  user_id: number;
  course_id: number;
  certificate_number: string;
  issue_date: string;
  pdf_url?: string;
  course: {
    id: number;
    title: string;
    slug: string;
    instructor?: {
      full_name: string;
    };
  };
}

export function useMyCertificates() {
  return useQuery({
    queryKey: ["my-certificates"],
    queryFn: async () => {
      const res = await api.get<CertificateItem[]>("/certificates/my");
      return res.data;
    },
  });
}

export function useClaimCertificate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (courseId: number | string) => {
      const res = await api.get<CertificateItem>(`/certificates/course/${courseId}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-certificates"] });
    },
  });
}

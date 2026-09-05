"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCourse } from "@/hooks/useCourses";
import { useEnrollment, useEnrollCourse } from "@/hooks/useEnrollment";
import { useAuth } from "@/hooks/useAuth";
import { RatingStars } from "@/components/course/RatingStars";
import { CurriculumList } from "@/components/course/CurriculumList";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatPrice } from "@/lib/utils";

export default function CourseDetailPage() {
  const { slug } = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const { data: course, isLoading } = useCourse(slug as string);
  const { data: enrollment } = useEnrollment(course?.id || "");
  const enrollMutation = useEnrollCourse();

  if (isLoading) {
    return <div className="max-w-7xl mx-auto px-4 py-16">Loading course details...</div>;
  }

  if (!course) {
    return <div className="max-w-7xl mx-auto px-4 py-16">Course not found.</div>;
  }

  const handleEnroll = async () => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    await enrollMutation.mutateAsync(course.id);
    router.push(`/courses/${course.slug}/learn`);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-4">
            <Badge variant="secondary" className="bg-slate-800 text-slate-200">{course.category}</Badge>
            <h1 className="text-3xl sm:text-4xl font-bold">{course.title}</h1>
            <p className="text-slate-300 text-lg">{course.subtitle || course.description}</p>

            <div className="flex flex-wrap items-center gap-4 text-sm">
              <RatingStars rating={course.average_rating || 0} />
              <span>({course.total_reviews} ratings)</span>
              <span>{course.total_students} students</span>
            </div>

            <div className="flex items-center gap-2 text-sm text-slate-300">
              <span>Created by</span>
              <span className="font-semibold text-white">{course.instructor?.full_name || "Instructor"}</span>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 shadow-xl space-y-5">
              <div className="relative aspect-video w-full rounded-lg bg-slate-900 overflow-hidden">
                {course.thumbnail_url ? (
                  <img src={course.thumbnail_url} alt={course.title} className="h-full w-full object-cover" />
                ) : (
                  <div className="h-full w-full flex items-center justify-center text-slate-500">No Image</div>
                )}
              </div>

              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold">
                  {formatPrice(course.discount_price !== undefined && course.discount_price !== null ? course.discount_price : course.price)}
                </span>
              </div>

              {enrollment ? (
                <Link href={`/courses/${course.slug}/learn`}>
                  <Button className="w-full" size="lg">Go to Course</Button>
                </Link>
              ) : (
                <Button
                  onClick={handleEnroll}
                  isLoading={enrollMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  Enroll Now
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Course Curriculum</h2>
        <CurriculumList sections={course.sections || []} isEnrolled={Boolean(enrollment)} />
      </div>
    </div>
  );
}

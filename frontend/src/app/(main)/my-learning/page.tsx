"use client";

import Link from "next/link";
import { useMyEnrollments } from "@/hooks/useEnrollment";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { BookOpen, Play } from "lucide-react";

export default function MyLearningPage() {
  const { data: enrollments, isLoading } = useMyEnrollments();

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">My Learning</h1>
      <p className="text-sm text-slate-500">Track your courses, lesson progress, and certificates.</p>

      {isLoading ? (
        <div className="py-16 text-center text-slate-500">Loading your enrollments...</div>
      ) : !enrollments || enrollments.length === 0 ? (
        <div className="text-center py-16 rounded-xl border border-dashed border-slate-300 mt-8">
          <BookOpen className="mx-auto h-12 w-12 text-slate-400" />
          <h3 className="mt-4 text-lg font-semibold text-slate-900">No enrolled courses yet</h3>
          <p className="mt-1 text-sm text-slate-500">Find your first course and start learning today!</p>
          <div className="mt-6">
            <Link href="/courses">
              <Button>Explore Courses</Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          {enrollments.map((enroll) => (
            <div
              key={enroll.id}
              className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm flex flex-col"
            >
              <div className="relative aspect-video bg-slate-100 overflow-hidden">
                {enroll.course?.thumbnail_url ? (
                  <img
                    src={enroll.course.thumbnail_url}
                    alt={enroll.course?.title || "Course"}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center bg-blue-50 text-blue-600">
                    <BookOpen className="h-10 w-10 opacity-50" />
                  </div>
                )}
              </div>

              <div className="p-5 flex flex-1 flex-col justify-between">
                <div>
                  <h3 className="font-semibold text-base text-slate-900 line-clamp-2">
                    {enroll.course?.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    By {enroll.course?.instructor?.full_name || "Instructor"}
                  </p>

                  <div className="mt-4 space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span>Progress</span>
                      <span className="font-semibold text-slate-700">{enroll.progress_percent}%</span>
                    </div>
                    <Progress value={enroll.progress_percent} />
                  </div>
                </div>

                <div className="mt-6">
                  <Link href={`/courses/${enroll.course?.slug}/learn`}>
                    <Button className="w-full">
                      <Play className="w-4 h-4 mr-2" />
                      {enroll.progress_percent > 0 ? "Continue Learning" : "Start Course"}
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

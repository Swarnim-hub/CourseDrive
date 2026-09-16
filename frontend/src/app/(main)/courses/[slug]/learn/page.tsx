"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useCourse } from "@/hooks/useCourses";
import { useEnrollment, useUpdateProgress } from "@/hooks/useEnrollment";
import { VideoPlayer } from "@/components/learning/VideoPlayer";
import { QuizPlayer } from "@/components/quiz/QuizPlayer";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, ChevronLeft, PlayCircle, HelpCircle, Award } from "lucide-react";

export default function CourseLearningPlayerPage() {
  const { slug } = useParams();
  const { data: course, isLoading } = useCourse(slug as string);
  const { data: enrollment } = useEnrollment(course?.id || "");
  const updateProgressMutation = useUpdateProgress();

  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);

  if (isLoading) return <div className="p-8 text-white bg-slate-900 min-h-screen">Loading learning experience...</div>;
  if (!course) return <div className="p-8 text-white bg-slate-900 min-h-screen">Course not found.</div>;

  const allLessons = (course.sections || []).flatMap((s) => s.lessons || []);
  const currentLesson = allLessons.find((l) => l.id === activeLessonId) || allLessons[0];

  const handleLessonComplete = async () => {
    if (currentLesson && course) {
      await updateProgressMutation.mutateAsync({
        courseId: course.id,
        lessonId: currentLesson.id,
        completed: true,
      });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-white">
      {/* Top Navigation Bar */}
      <div className="flex h-14 items-center justify-between border-b border-slate-800 px-4 bg-slate-950">
        <div className="flex items-center gap-4">
          <Link href={`/courses/${course.slug}`} className="text-slate-400 hover:text-white">
            <ChevronLeft className="h-5 w-5" />
          </Link>
          <h1 className="font-semibold text-sm sm:text-base truncate max-w-md lg:max-w-2xl">
            {course.title}
          </h1>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden sm:flex items-center gap-3">
            <Progress value={enrollment?.progress_percentage ?? enrollment?.progress_percent ?? 0} className="w-32 h-2 bg-slate-800" />
            <span className="text-xs text-slate-400">
              {Math.round(enrollment?.progress_percentage ?? enrollment?.progress_percent ?? 0)}% Completed
            </span>
          </div>

          {(enrollment?.progress_percentage === 100 || enrollment?.progress_percent === 100 || enrollment?.status === "completed") && (
            <Link href="/certificates">
              <Button size="sm" variant="secondary" className="bg-emerald-600 hover:bg-emerald-700 text-white animate-pulse">
                <Award className="h-4 w-4 mr-2" />
                Claim / View Certificate
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Main Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Player & Content Area */}
        <div className="flex-1 flex flex-col overflow-y-auto">
          <div className="p-6 max-w-5xl mx-auto w-full">
            {currentLesson?.quiz_id ? (
              <QuizPlayer
                quiz={{
                  id: currentLesson.quiz_id,
                  course_id: course.id,
                  title: `Quiz: ${currentLesson.title}`,
                  passing_score_percent: 80,
                  questions: [
                    {
                      id: "q1",
                      quiz_id: currentLesson.quiz_id,
                      prompt: "What is the primary benefit of React Server Components?",
                      options: [
                        { id: "o1", text: "Reduced client-bundle size and direct database access" },
                        { id: "o2", text: "Faster client-side animations" },
                        { id: "o3", text: "Automatic CSS generation" },
                      ],
                      order_index: 1,
                    },
                  ],
                }}
                onFinish={handleLessonComplete}
              />
            ) : (
              <VideoPlayer
                url={currentLesson?.video_url}
                onComplete={handleLessonComplete}
              />
            )}

            <div className="mt-6 flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-xl font-semibold">{currentLesson?.title}</h2>
                <p className="text-sm text-slate-400 mt-1">{currentLesson?.description || currentLesson?.content || "No description provided."}</p>
                
                {currentLesson?.pdf_url && (
                  <div className="mt-4">
                    <a
                      href={currentLesson.pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      download
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-800/40 text-sm font-medium transition-colors"
                    >
                      <Award className="w-4 h-4 text-purple-400" />
                      Download Lesson Notes &amp; Resources (PDF)
                    </a>
                  </div>
                )}
              </div>
              <Button
                onClick={handleLessonComplete}
                variant="outline"
                className="border-slate-700 text-white hover:bg-slate-800"
              >
                <CheckCircle className="w-4 h-4 mr-2 text-emerald-500" />
                Mark as Complete
              </Button>
            </div>
          </div>
        </div>

        {/* Sidebar Lesson List */}
        <div className="w-80 bg-slate-950 border-l border-slate-800 flex flex-col overflow-y-auto">
          <div className="p-4 border-b border-slate-800">
            <h3 className="font-semibold text-sm">Course Content</h3>
          </div>
          <div className="divide-y divide-slate-900">
            {course.sections?.map((s) => (
              <div key={s.id}>
                <div className="px-4 py-2.5 bg-slate-900/80 text-xs font-semibold text-slate-400">
                  {s.title}
                </div>
                <div>
                  {s.lessons?.map((lesson) => {
                    const isActive = currentLesson?.id === lesson.id;
                    const isDone = enrollment?.completed_lessons?.includes(lesson.id);
                    return (
                      <button
                        key={lesson.id}
                        onClick={() => setActiveLessonId(lesson.id)}
                        className={`flex w-full items-center justify-between px-4 py-3 text-sm text-left transition-colors ${
                          isActive
                            ? "bg-blue-600/20 text-blue-400 border-l-2 border-blue-500"
                            : "hover:bg-slate-900 text-slate-300"
                        }`}
                      >
                        <div className="flex items-center gap-2.5">
                          {isDone ? (
                            <CheckCircle className="h-4 w-4 text-emerald-500" />
                          ) : lesson.quiz_id ? (
                            <HelpCircle className="h-4 w-4 text-purple-400" />
                          ) : (
                            <PlayCircle className="h-4 w-4 text-slate-500" />
                          )}
                          <span className="line-clamp-1">{lesson.title}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

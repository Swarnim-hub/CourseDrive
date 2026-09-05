import Link from "next/link";
import { Course } from "@/types/course";
import { RatingStars } from "./RatingStars";
import { Badge } from "@/components/ui/badge";
import { Clock, BookOpen, Users } from "lucide-react";
import { formatPrice, formatDuration } from "@/lib/utils";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/courses/${course.slug}`}
      className="group flex flex-col rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm transition-all duration-200 hover:shadow-md hover:-translate-y-1"
    >
      <div className="relative aspect-video w-full bg-slate-100 overflow-hidden">
        {course.thumbnail_url ? (
          <img
            src={course.thumbnail_url}
            alt={course.title}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-blue-50 text-blue-600">
            <BookOpen className="h-12 w-12 opacity-50" />
          </div>
        )}
        <div className="absolute top-3 left-3">
          <Badge variant="secondary" className="bg-white/90 backdrop-blur-sm">
            {typeof course.category === "object" && course.category !== null ? (course.category as any).name : (course.category || "General")}
          </Badge>
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-between p-5">
        <div>
          <h3 className="font-semibold text-base text-slate-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
            {course.title}
          </h3>
          <p className="mt-1 text-xs text-slate-500 line-clamp-1">
            By {course.instructor?.full_name || "Expert Instructor"}
          </p>

          <div className="mt-2.5">
            <RatingStars rating={course.average_rating || 5.0} />
          </div>

          <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              <span>{formatDuration(course.total_duration_minutes || 120)}</span>
            </div>
            <div className="flex items-center gap-1">
              <Users className="h-3.5 w-3.5" />
              <span>{course.total_students || 0} learners</span>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-slate-900">
              {formatPrice(course.discount_price !== undefined && course.discount_price !== null ? course.discount_price : course.price)}
            </span>
            {course.discount_price !== undefined && course.discount_price !== null && course.price > course.discount_price && (
              <span className="text-sm line-through text-slate-400">
                {formatPrice(course.price)}
              </span>
            )}
          </div>
          <Badge variant="outline" className="capitalize">
            {course.difficulty ? course.difficulty.replace("_", " ") : "All Levels"}
          </Badge>
        </div>
      </div>
    </Link>
  );
}

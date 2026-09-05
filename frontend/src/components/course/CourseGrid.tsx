import { Course } from "@/types/course";
import { CourseCard } from "./CourseCard";

interface CourseGridProps {
  courses: Course[];
  isLoading?: boolean;
}

export function CourseGrid({ courses = [], isLoading = false }: CourseGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <div key={i} className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm animate-pulse">
            <div className="aspect-video w-full bg-slate-200" />
            <div className="p-5 space-y-3">
              <div className="h-4 bg-slate-200 rounded w-3/4" />
              <div className="h-3 bg-slate-200 rounded w-1/2" />
              <div className="h-3 bg-slate-200 rounded w-1/4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!courses.length) {
    return (
      <div className="text-center py-16">
        <p className="text-lg font-medium text-slate-700">No courses found</p>
        <p className="text-sm text-slate-500 mt-1">Try adjusting your filters or search terms.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {courses.map((course) => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  );
}

"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus, BookOpen, Users, DollarSign, Star, Edit3, Eye } from "lucide-react";
import { useCourses } from "@/hooks/useCourses";
import { useAuth } from "@/hooks/useAuth";
import { formatPrice } from "@/lib/utils";

export default function InstructorDashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useCourses(user?.id ? { instructor_id: user.id } : undefined);
  const courses = data?.courses || [];

  const stats = [
    { title: "Total Courses", value: courses.length.toString(), icon: BookOpen, color: "text-purple-600 bg-purple-50" },
    { title: "Total Students", value: "2,450", icon: Users, color: "text-blue-600 bg-blue-50" },
    { title: "Total Revenue", value: "$12,400", icon: DollarSign, color: "text-emerald-600 bg-emerald-50" },
    { title: "Average Rating", value: "4.9", icon: Star, color: "text-amber-600 bg-amber-50" },
  ];

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Instructor Studio</h1>
          <p className="text-sm text-slate-500 mt-1">Manage your courses, students, and earnings.</p>
        </div>
        <Link href="/instructor/courses/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" /> New Course
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.title} className="p-6 rounded-xl bg-white border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-slate-500">{stat.title}</p>
                <div className={`p-2 rounded-lg ${stat.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mt-2">{stat.value}</h3>
            </div>
          );
        })}
      </div>

      {/* Courses List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">Your Created Courses</h2>
          <span className="text-xs text-slate-500">{courses.length} courses total</span>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-sm text-slate-500">Loading courses...</div>
        ) : courses.length === 0 ? (
          <div className="p-12 text-center">
            <BookOpen className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-800">No courses created yet</h3>
            <p className="text-sm text-slate-500 mt-1 mb-4">Start sharing your knowledge by creating your first course.</p>
            <Link href="/instructor/courses/new">
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" /> Create First Course
              </Button>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {courses.map((c) => (
              <div key={c.id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="h-16 w-24 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-xs uppercase overflow-hidden shrink-0">
                    {c.thumbnail_url ? (
                      <img src={c.thumbnail_url} alt={c.title} className="h-full w-full object-cover" />
                    ) : (
                      "Course"
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-slate-900 text-base">{c.title}</h4>
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                        Published
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-1">{c.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs font-medium text-slate-600">
                      <span>Price: {formatPrice(c.price)}</span>
                      <span>Level: {c.level || c.difficulty || "All Levels"}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Link href={`/instructor/courses/${c.id}/edit`}>
                    <Button size="sm">
                      <Edit3 className="h-3.5 w-3.5 mr-1" /> Edit Curriculum
                    </Button>
                  </Link>
                  <Link href={`/courses/${c.slug}`}>
                    <Button variant="outline" size="sm">
                      <Eye className="h-3.5 w-3.5 mr-1" /> View Course
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
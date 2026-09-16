"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CourseGrid } from "@/components/course/CourseGrid";

import * as Icons from "lucide-react";
import { useCourses, useCategories } from "@/hooks/useCourses";

export default function HomePage() {
  const { data: coursesData, isLoading } = useCourses({ limit: 8 });
  const { data: categories } = useCategories();
  const courses = coursesData?.courses || [];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/50 via-white to-slate-50 py-20 lg:py-28 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100/80 text-blue-800 text-sm font-medium">
              <Icons.Sparkles className="h-4 w-4" />
              <span>#1 Rated Online Learning Platform</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
              Learn Without Limits with{" "}
              <span className="text-blue-600">CourseDrive</span>
            </h1>

            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed">
              Build skills with courses, certificates, and degrees online from world-class universities and leading companies.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/courses">
                <Button size="lg" className="w-full sm:w-auto px-8 shadow-md">
                  Explore Courses
                </Button>
              </Link>
              <Link href="/register">
                <Button size="lg" variant="outline" className="w-full sm:w-auto px-8">
                  Join for Free
                </Button>
              </Link>
            </div>

            {/* Platform Stats */}
            <div className="pt-12 grid grid-cols-2 sm:grid-cols-4 gap-6 text-center border-t border-slate-200 mt-12">
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-slate-900">50K+</div>
                <div className="text-sm text-slate-500 mt-1">Active Students</div>
              </div>
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-slate-900">1,200+</div>
                <div className="text-sm text-slate-500 mt-1">Expert Courses</div>
              </div>
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-slate-900">300+</div>
                <div className="text-sm text-slate-500 mt-1">Instructors</div>
              </div>
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-slate-900">4.9/5</div>
                <div className="text-sm text-slate-500 mt-1">Average Rating</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Category Explorer */}
      <section className="py-16 bg-white border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Explore Top Categories</h2>
              <p className="text-slate-500 mt-1">Find the right path to accelerate your professional growth.</p>
            </div>
            <Link href="/courses" className="text-blue-600 font-semibold hover:underline mt-2 sm:mt-0 text-sm">
              All Categories &rarr;
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {(categories || []).map((cat) => {
              const Icon = (Icons as any)[cat.icon || "Code"] || Icons.Code;
              return (
                <Link
                  key={cat.id}
                  href={`/courses?category=${cat.id}`}
                  className="flex flex-col items-center text-center p-5 rounded-xl border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all group bg-white"
                >
                  <div className="p-3.5 rounded-xl bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors mb-3">
                    <Icon className="h-6 w-6" />
                  </div>
                  <span className="font-semibold text-sm text-slate-900 group-hover:text-blue-600 transition-colors">
                    {cat.name}
                  </span>
                  <span className="text-xs text-slate-400 mt-1">{cat.count}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Featured Courses */}
      <section className="py-16 bg-slate-50/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Featured Courses</h2>
              <p className="text-slate-500 mt-1">Handpicked courses designed to help you succeed.</p>
            </div>
            <Link href="/courses" className="text-blue-600 font-semibold hover:underline mt-2 sm:mt-0 text-sm">
              View all courses &rarr;
            </Link>
          </div>

          <CourseGrid courses={courses} isLoading={isLoading} />
        </div>
      </section>

      {/* Why CourseDrive */}
      <section className="py-16 bg-white border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Why Learn with CourseDrive?</h2>
            <p className="text-slate-600 mt-2">Everything you need to advance your career and master in-demand skills.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/50">
              <div className="h-12 w-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4">
                <Icons.PlayCircle className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Learn at Your Own Pace</h3>
              <p className="text-sm text-slate-600">
                Enjoy lifetime access to courses on mobile and desktop. Learn whenever and wherever you want.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/50">
              <div className="h-12 w-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4">
                <Icons.Award className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Verified Certificates</h3>
              <p className="text-sm text-slate-600">
                Earn verifiable certificates upon course and quiz completion to showcase on your resume and LinkedIn.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/50">
              <div className="h-12 w-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4">
                <Icons.GraduationCap className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Industry Expert Instructors</h3>
              <p className="text-sm text-slate-600">
                Learn from industry veterans, experienced developers, and thought leaders at the top of their fields.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Instructor CTA */}
      <section className="py-20 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h2 className="text-3xl sm:text-4xl font-bold">Become an Instructor on CourseDrive</h2>
            <p className="text-slate-300 text-base sm:text-lg">
              Top instructors from around the world teach millions of students on CourseDrive. We provide the tools and skills to teach what you love.
            </p>
            <div className="pt-2">
              <Link href="/instructor/courses/new">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 shadow-lg">
                  Start Teaching Today
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
"use client";

import { useState, useEffect } from "react";
import { CourseGrid } from "@/components/course/CourseGrid";
import { useCourses } from "@/hooks/useCourses";
import { api } from "@/lib/api";
import { Search, Sliders } from "lucide-react";

export default function CoursesCatalogPage() {
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<number | "all">("all");
  const [level, setLevel] = useState("all");
  const [categories, setCategories] = useState<{id: number, name: string}[]>([]);

  useEffect(() => {
    api.get("/categories").then(res => setCategories(res.data)).catch(console.error);
  }, []);

  const { data, isLoading } = useCourses({
    search: search || undefined,
    category_id: categoryId === "all" ? undefined : Number(categoryId),
    level: level === "all" ? undefined : level,
  });

  const courses = data?.courses || [];

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Explore Courses</h1>
          <p className="text-sm text-slate-500 mt-1">Discover the best courses to achieve your career goals.</p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or topic..."
            className="w-full h-10 pl-10 pr-4 text-sm rounded-md border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
        </div>
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap items-center gap-3 mb-8">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 mr-2">
          <Sliders className="h-4 w-4" /> Filters:
        </div>

        {/* Category Filter */}
        <select
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value === "all" ? "all" : Number(e.target.value))}
          className="h-9 px-3 text-sm rounded-md border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
        >
          <option value="all">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        {/* Difficulty Filter */}
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="h-9 px-3 text-sm rounded-md border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
        >
          <option value="all">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      {/* Courses List */}
      <CourseGrid courses={courses} isLoading={isLoading} />
    </div>
  );
}

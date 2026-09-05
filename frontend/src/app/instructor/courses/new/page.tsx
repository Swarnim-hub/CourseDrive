"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateCourse } from "@/hooks/useCourses";
import { COURSE_CATEGORIES } from "@/lib/constants";

export default function NewCoursePage() {
  const router = useRouter();
  const createMutation = useCreateCourse();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("49.99");
  const [category, setCategory] = useState("Development");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numPrice = parseFloat(price) || 0;
    await createMutation.mutateAsync({
      title,
      subtitle: title,
      description,
      category_id: 1,
      price: numPrice,
      is_free: numPrice === 0,
      level: "all_levels" as any,
      requirements: ["Basic understanding of the subject"],
      what_you_will_learn: ["Practical skills and real-world projects"],
    });
    router.push("/instructor");
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Create New Course</h1>
      <p className="text-sm text-slate-500 mb-8">Fill in the basic course details to get started.</p>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Course Title</label>
          <Input
            type="text"
            required
            placeholder="e.g. Master Modern Web Architecture"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Course Description</label>
          <textarea
            required
            rows={4}
            placeholder="Describe what students will learn in this course..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded-md border border-slate-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full h-10 px-3 text-sm rounded-md border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              {COURSE_CATEGORIES.map((c) => (
                <option key={c.id} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Price (USD)</label>
            <Input
              type="number"
              step="0.01"
              required
              placeholder="49.99"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
            />
          </div>
        </div>

        <div className="pt-4 flex justify-end gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={createMutation.isPending}
          >
            Create Course
          </Button>
        </div>
      </form>
    </div>
  );
}
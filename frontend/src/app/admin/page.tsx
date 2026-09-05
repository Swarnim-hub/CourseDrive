"use client";

import { Users, BookOpen, Activity, Award } from "lucide-react";

export default function AdminKPIDashboardPage() {
  const stats = [
    { title: "Total Users", value: "54,200", change: "+12% this month", icon: Users, color: "text-blue-600 bg-blue-50" },
    { title: "Published Courses", value: "1,240", change: "+8 new this week", icon: BookOpen, color: "text-emerald-600 bg-emerald-50" },
    { title: "Active Enrollments", value: "128,450", change: "+24% this month", icon: Activity, color: "text-purple-600 bg-purple-50" },
    { title: "Certificates Issued", value: "18,920", change: "+15% this month", icon: Award, color: "text-amber-600 bg-amber-50" },
  ];

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Admin Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Platform overview, system metrics, and analytics.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
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
              <p className="text-xs text-emerald-600 mt-1 font-medium">{stat.change}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
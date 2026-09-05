import Link from "next/link";
import { BookOpen } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 text-slate-600">
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2.5 font-bold text-xl">
              <div className="p-1.5 bg-blue-600 text-white rounded-lg">
                <BookOpen className="h-5 w-5" />
              </div>
              <span className="text-slate-900">Course<span className="text-blue-600">Drive</span></span>
            </Link>
            <p className="text-sm text-slate-500">
              Empowering learners around the globe with world-class courses, interactive quizzes, and accredited certifications.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Platform</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/courses" className="hover:text-blue-600">Browse Courses</Link></li>
              <li><Link href="/certificates" className="hover:text-blue-600">Certificates</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Instructors</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/instructor/courses/new" className="hover:text-blue-600">Teach on CourseDrive</Link></li>
              <li><Link href="/instructor" className="hover:text-blue-600">Instructor Dashboard</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/courses" className="hover:text-blue-600">Explore</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-slate-200 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>&copy; {new Date().getFullYear()} CourseDrive, Inc. All rights reserved.</p>
          <p>Built for learners everywhere.</p>
        </div>
      </div>
    </footer>
  );
}

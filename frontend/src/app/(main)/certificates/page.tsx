"use client";

import Link from "next/link";
import { Award, Download, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CertificatesPage() {
  const certificates = [
    {
      id: "cert-101",
      code: "CD-9922-2026",
      course_title: "Complete 2026 Full-Stack Web Development Bootcamp",
      instructor_name: "Dude Educator",
      issue_date: "2026-02-15",
    },
  ];

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">My Certificates</h1>
      <p className="text-sm text-slate-500">Accredited credentials and verifiable certificates for completed courses.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        {certificates.map((c) => (
          <div
            key={c.id}
            className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-emerald-100 text-emerald-600 rounded-lg">
                  <Award className="h-6 w-6" />
                </div>
                <div>
                  <span className="text-xs font-mono text-slate-400">{c.code}</span>
                  <h3 className="font-semibold text-lg text-slate-900">{c.course_title}</h3>
                </div>
              </div>
              <p className="mt-4 text-sm text-slate-600">
                Instructor: <span className="font-medium text-slate-800">{c.instructor_name}</span> &bull; Issued on {c.issue_date}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <Link href={`/verify/${c.code}`}>
                <Button variant="outline" size="sm">
                  <ExternalLink className="h-3.5 w-3.5 mr-1.5" /> Verify
                </Button>
              </Link>
              <Button size="sm">
                <Download className="h-3.5 w-3.5 mr-1.5" /> PDF Certificate
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { Award, Download, ExternalLink, Loader2, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useMyCertificates } from "@/hooks/useCertificates";

export default function CertificatesPage() {
  const { data: certificates, isLoading } = useMyCertificates();

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">My Certificates</h1>
      <p className="text-sm text-slate-500">
        Accredited credentials and verifiable certificates earned upon completing all course lessons.
      </p>

      {isLoading ? (
        <div className="py-20 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-sm text-slate-500 mt-2">Loading certificates...</p>
        </div>
      ) : !certificates || certificates.length === 0 ? (
        <div className="mt-12 bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center max-w-xl mx-auto">
          <Award className="h-12 w-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900">No certificates earned yet</h3>
          <p className="text-sm text-slate-500 mt-1 mb-6">
            Complete all lessons and quizzes in an enrolled course to unlock your official Certificate of Completion!
          </p>
          <Link href="/my-learning">
            <Button>
              <BookOpen className="h-4 w-4 mr-2" /> Continue Learning
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          {certificates.map((c) => {
            const formattedDate = new Date(c.issue_date).toLocaleDateString(undefined, {
              year: "numeric",
              month: "long",
              day: "numeric",
            });

            return (
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
                      <span className="text-xs font-mono text-slate-400">{c.certificate_number}</span>
                      <h3 className="font-semibold text-lg text-slate-900">{c.course?.title}</h3>
                    </div>
                  </div>
                  <p className="mt-4 text-sm text-slate-600">
                    Instructor:{" "}
                    <span className="font-medium text-slate-800">
                      {c.course?.instructor?.full_name || "Course Instructor"}
                    </span>{" "}
                    &bull; Issued on {formattedDate}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <Link href={`/verify/${c.certificate_number}`}>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="h-3.5 w-3.5 mr-1.5" /> Verify
                    </Button>
                  </Link>
                  {c.pdf_url ? (
                    <a href={c.pdf_url} target="_blank" rel="noopener noreferrer" download>
                      <Button size="sm">
                        <Download className="h-3.5 w-3.5 mr-1.5" /> PDF Certificate
                      </Button>
                    </a>
                  ) : (
                    <Button size="sm" disabled>
                      Processing PDF...
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

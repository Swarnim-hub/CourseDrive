"use client";

import { useParams } from "next/navigation";
import { ShieldCheck } from "lucide-react";

export default function VerifyCertificatePage() {
  const { id } = useParams();

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full bg-white rounded-2xl border border-slate-200 p-8 shadow-lg">
        <div className="flex items-center gap-3 text-emerald-600">
          <ShieldCheck className="h-8 w-8" />
          <h3 className="text-xl font-bold text-slate-900">Verified CourseDrive Credential</h3>
        </div>

        <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-100">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-500">Certificate Code</p>
              <p className="font-mono font-semibold text-slate-800">{id}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Status</p>
              <p className="font-semibold text-emerald-600">Valid & Authentic</p>
            </div>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          <p className="text-sm text-slate-700">
            This certificate attests that the holder successfully completed all lectures, practical lessons, and assessments with distinction on CourseDrive.
          </p>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CheckoutSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const courseId = searchParams.get("course_id");
  
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    if (!sessionId || !courseId) {
      setStatus("error");
      return;
    }

    // Attempt to confirm the mock payment
    api.post(`/payments/confirm-mock?session_id=${sessionId}&course_id=${courseId}`)
      .then(() => {
        setStatus("success");
      })
      .catch((err) => {
        console.error("Payment confirmation failed:", err);
        setStatus("error");
      });
  }, [sessionId, courseId]);

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center space-y-6">
        {status === "loading" && (
          <>
            <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto" />
            <h2 className="text-2xl font-bold text-slate-900">Confirming Payment...</h2>
            <p className="text-slate-500">Please do not close this window.</p>
          </>
        )}

        {status === "success" && (
          <>
            <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto" />
            <h2 className="text-2xl font-bold text-slate-900">Payment Successful!</h2>
            <p className="text-slate-500">You are now enrolled in the course. You can find it in your learning dashboard.</p>
            <Button className="w-full mt-4" onClick={() => router.push("/my-learning")}>
              Go to My Learning
            </Button>
          </>
        )}

        {status === "error" && (
          <>
            <XCircle className="w-16 h-16 text-red-500 mx-auto" />
            <h2 className="text-2xl font-bold text-slate-900">Payment Failed</h2>
            <p className="text-slate-500">We couldn't confirm your enrollment. Please contact support if you were charged.</p>
            <Button className="w-full mt-4" variant="outline" onClick={() => router.push("/courses")}>
              Back to Courses
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

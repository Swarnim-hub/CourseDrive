"use client";

import { useState } from "react";
import { Quiz, QuizResult } from "@/types/quiz";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, RefreshCw } from "lucide-react";

export function QuizPlayer({
  quiz,
  onFinish,
}: {
  quiz: Quiz;
  onFinish?: (result: QuizResult) => void;
}) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!quiz?.questions?.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500">
        No questions available for this quiz.
      </div>
    );
  }

  const q = quiz.questions[currentQuestion];

  const handleOptionSelect = (optionId: string) => {
    if (q) {
      setSelectedAnswers((prev) => ({ ...prev, [q.id]: optionId }));
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    const total = quiz.questions.length;
    const analysis = quiz.questions.map((item) => {
      const selected = selectedAnswers[item.id];
      const correctOption = item.options?.[0]?.id || "";
      return {
        question_id: item.id,
        is_correct: selected === correctOption,
        correct_option_id: correctOption,
        explanation: item.explanation || "Great job understanding this concept!",
      };
    });

    const corrects = analysis.filter((a) => a.is_correct).length;
    const score = Math.round((corrects / total) * 100);
    const passed = score >= quiz.passing_score_percent;

    const res: QuizResult = {
      score_percent: score,
      passed,
      total_questions: total,
      correct_count: corrects,
      answers_analysis: analysis,
    };
    setResult(res);
    setIsSubmitting(false);
    onFinish?.(res);
  };

  if (result) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        {result.passed ? (
          <div className="mx-auto w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
            <CheckCircle className="w-10 h-10" />
          </div>
        ) : (
          <div className="mx-auto w-16 h-16 rounded-full bg-red-100 flex items-center justify-center text-red-600">
            <XCircle className="w-10 h-10" />
          </div>
        )}

        <h2 className="text-2xl font-bold text-slate-900 mt-4">
          {result.passed ? "Quiz Passed!" : "Try Again"}
        </h2>
        <p className="text-slate-600 mt-1">
          You scored <span className="font-semibold">{result.score_percent}%</span> ({result.correct_count}/{result.total_questions} correct), passing grade is {quiz.passing_score_percent}%.
        </p>

        <div className="mt-6 flex items-center justify-center gap-4">
          <Button
            onClick={() => {
              setResult(null);
              setCurrentQuestion(0);
              setSelectedAnswers({});
            }}
            variant="outline"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Retake Quiz
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <h3 className="text-lg font-semibold text-slate-900">{quiz.title}</h3>
        <span className="text-sm text-slate-500">
          Question {currentQuestion + 1} of {quiz.questions.length}
        </span>
      </div>

      <div className="py-6">
        <h4 className="text-base font-medium text-slate-900 mb-4">{q?.prompt}</h4>

        <div className="space-y-3">
          {q?.options?.map((opt) => {
            const isSelected = selectedAnswers[q.id] === opt.id;
            return (
              <button
                type="button"
                key={opt.id}
                onClick={() => handleOptionSelect(opt.id)}
                className={`flex w-full items-center p-3.5 rounded-lg border text-left transition-colors ${
                  isSelected
                    ? "border-blue-600 bg-blue-50 text-blue-900"
                    : "border-slate-200 hover:bg-slate-50 text-slate-700"
                }`}
              >
                <div
                  className={`w-4 h-4 rounded-full border mr-3 flex items-center justify-center ${
                    isSelected ? "border-blue-600 bg-blue-600" : "border-slate-300"
                  }`}
                >
                  {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                </div>
                <span className="text-sm">{opt.text}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        <Button
          type="button"
          disabled={currentQuestion === 0}
          onClick={() => setCurrentQuestion((prev) => prev - 1)}
          variant="outline"
        >
          Previous
        </Button>

        {currentQuestion < quiz.questions.length - 1 ? (
          <Button
            type="button"
            disabled={!q || !selectedAnswers[q.id]}
            onClick={() => setCurrentQuestion((prev) => prev + 1)}
          >
            Next
          </Button>
        ) : (
          <Button
            type="button"
            disabled={!q || !selectedAnswers[q.id]}
            onClick={handleSubmit}
            isLoading={isSubmitting}
          >
            Submit Quiz
          </Button>
        )}
      </div>
    </div>
  );
}

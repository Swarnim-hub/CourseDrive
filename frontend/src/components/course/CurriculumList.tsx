"use client";

import { useState } from "react";
import { Section } from "@/types/course";
import { ChevronDown, ChevronUp, PlayCircle, HelpCircle, Lock } from "lucide-react";
import { formatDuration } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface CurriculumListProps {
  sections: Section[];
  isEnrolled?: boolean;
}

export function CurriculumList({ sections = [], isEnrolled = false }: CurriculumListProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>(() =>
    sections.reduce((acc, s, i) => ({ ...acc, [s.id]: i === 0 }), {})
  );

  const toggleSection = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (!sections || sections.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-center text-slate-500">
        No curriculum available for this course yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sections.map((section, sectionIndex) => {
        const isSectionExpanded = expanded[section.id] ?? false;
        const totalSectionDuration = (section.lessons || []).reduce(
          (acc, l) => acc + (l.duration_minutes || 0),
          0
        );

        return (
          <div key={section.id || sectionIndex} className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
            <button
              type="button"
              onClick={() => toggleSection(section.id)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold text-slate-500">
                  Section {sectionIndex + 1}:
                </span>
                <span className="font-semibold text-slate-900">{section.title}</span>
              </div>

              <div className="flex items-center gap-4 text-sm text-slate-500">
                <span>
                  {section.lessons?.length || 0} lessons &bull; {formatDuration(totalSectionDuration)}
                </span>
                {isSectionExpanded ? (
                  <ChevronUp className="h-5 w-5 text-slate-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-slate-400" />
                )}
              </div>
            </button>

            {isSectionExpanded && (
              <div className="border-t border-slate-100 divide-y divide-slate-100 bg-slate-50/50">
                {section.lessons?.map((lesson, lessonIndex) => {
                  const canAccess = isEnrolled || lesson.is_preview;

                  return (
                    <div
                      key={lesson.id || lessonIndex}
                      className="flex items-center justify-between px-6 py-3.5 hover:bg-white transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        {lesson.quiz_id ? (
                          <HelpCircle className="h-4 w-4 text-blue-500 shrink-0" />
                        ) : (
                          <PlayCircle className="h-4 w-4 text-slate-400 shrink-0" />
                        )}
                        <span className="text-sm text-slate-700">{lesson.title}</span>
                        {lesson.is_preview && !isEnrolled && (
                          <Badge variant="outline" className="text-xs text-blue-600 border-blue-200 bg-blue-50">
                            Preview
                          </Badge>
                        )}
                      </div>

                      <div className="flex items-center gap-3 text-xs text-slate-400">
                        <span>{formatDuration(lesson.duration_minutes || 0)}</span>
                        {!canAccess && <Lock className="h-3.5 w-3.5 text-slate-400" />}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
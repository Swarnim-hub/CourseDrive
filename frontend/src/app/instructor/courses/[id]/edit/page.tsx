"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useCourse, useUpdateCourse } from "@/hooks/useCourses";
import {
  useCreateSection,
  useUpdateSection,
  useDeleteSection,
  useCreateLesson,
  useUpdateLesson,
  useDeleteLesson,
  useUploadLessonVideo,
  useUploadLessonPdf,
} from "@/hooks/useCourseMutations";
import { api } from "@/lib/api";
import { DIFFICULTY_LEVELS } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ChevronLeft,
  Plus,
  Trash2,
  Video,
  FileText,
  Upload,
  CheckCircle,
  Loader2,
  Edit2,
  Save,
  Layers,
  Settings,
} from "lucide-react";

export default function EditCoursePage() {
  const { id } = useParams();
  const courseId = id as string;
  const router = useRouter();

  const { data: course, isLoading, refetch } = useCourse(courseId);
  const updateCourseMutation = useUpdateCourse(courseId);
  const createSectionMutation = useCreateSection(courseId);
  const updateSectionMutation = useUpdateSection(courseId);
  const deleteSectionMutation = useDeleteSection(courseId);
  const createLessonMutation = useCreateLesson(courseId);
  const updateLessonMutation = useUpdateLesson(courseId);
  const deleteLessonMutation = useDeleteLesson(courseId);
  const uploadVideoMutation = useUploadLessonVideo();
  const uploadPdfMutation = useUploadLessonPdf();

  const [activeTab, setActiveTab] = useState<"curriculum" | "details">("curriculum");

  // Course Details State
  const [title, setTitle] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("0");
  const [level, setLevel] = useState("all_levels");
  const [categories, setCategories] = useState<{ id: number; name: string }[]>([]);
  const [categoryId, setCategoryId] = useState<number>(1);
  const [detailsSaved, setDetailsSaved] = useState(false);

  // New Section Form
  const [newSectionTitle, setNewSectionTitle] = useState("");
  const [showAddSection, setShowAddSection] = useState(false);

  // Editing Section State
  const [editingSectionId, setEditingSectionId] = useState<string | null>(null);
  const [editingSectionTitle, setEditingSectionTitle] = useState("");

  // New Lesson Form
  const [addingLessonSectionId, setAddingLessonSectionId] = useState<string | null>(null);
  const [newLessonTitle, setNewLessonTitle] = useState("");

  // Active Lesson Editor
  const [expandedLessonId, setExpandedLessonId] = useState<string | null>(null);
  const [lessonFormData, setLessonFormData] = useState<{
    title: string;
    description: string;
    video_url: string;
    pdf_url: string;
    duration_seconds: number;
    is_preview: boolean;
  }>({
    title: "",
    description: "",
    video_url: "",
    pdf_url: "",
    duration_seconds: 0,
    is_preview: false,
  });

  // Upload States
  const [uploadingVideoLessonId, setUploadingVideoLessonId] = useState<string | null>(null);
  const [uploadingPdfLessonId, setUploadingPdfLessonId] = useState<string | null>(null);

  useEffect(() => {
    api
      .get("/categories")
      .then((res) => setCategories(res.data))
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (course) {
      setTitle(course.title || "");
      setSubtitle(course.subtitle || "");
      setDescription(course.description || "");
      setPrice(String(course.price ?? "0"));
      setLevel(course.level || "all_levels");
      if (course.category_id) {
        setCategoryId(course.category_id);
      }
    }
  }, [course]);

  const handleSaveDetails = async (e: React.FormEvent) => {
    e.preventDefault();
    const numPrice = parseFloat(price) || 0;
    await updateCourseMutation.mutateAsync({
      title,
      subtitle,
      description,
      price: numPrice,
      is_free: numPrice === 0,
      level: level as any,
      category_id: categoryId,
    });
    setDetailsSaved(true);
    setTimeout(() => setDetailsSaved(false), 3000);
  };

  const handleAddSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSectionTitle.trim()) return;
    const orderIndex = (course?.sections?.length || 0) + 1;
    try {
      await createSectionMutation.mutateAsync({
        title: newSectionTitle.trim(),
        order_index: orderIndex,
      });
      setNewSectionTitle("");
      setShowAddSection(false);
      refetch();
    } catch (error: any) {
      console.error("Section creation error:", error);
      alert("Failed to save section: " + (error?.response?.data?.detail || error.message || "Unknown error"));
    }
  };

  const handleSaveSectionTitle = async (sectionId: string) => {
    if (!editingSectionTitle.trim()) return;
    await updateSectionMutation.mutateAsync({
      sectionId,
      title: editingSectionTitle.trim(),
    });
    setEditingSectionId(null);
    refetch();
  };

  const handleDeleteSection = async (sectionId: string) => {
    if (confirm("Are you sure you want to delete this section and all its lessons?")) {
      await deleteSectionMutation.mutateAsync(sectionId);
      refetch();
    }
  };

  const handleAddLesson = async (sectionId: string) => {
    if (!newLessonTitle.trim()) return;
    const section = course?.sections?.find((s) => String(s.id) === String(sectionId));
    const orderIndex = (section?.lessons?.length || 0) + 1;

    try {
      await createLessonMutation.mutateAsync({
        section_id: Number(sectionId),
        title: newLessonTitle.trim(),
        lesson_type: "video",
        order: orderIndex,
      });
      setNewLessonTitle("");
      setAddingLessonSectionId(null);
      refetch();
    } catch (error: any) {
      console.error("Lesson creation error:", error);
      alert("Failed to add lesson: " + (error?.response?.data?.detail || error.message || "Unknown error"));
    }
  };

  const handleDeleteLesson = async (lessonId: string) => {
    if (confirm("Are you sure you want to delete this lesson?")) {
      await deleteLessonMutation.mutateAsync(lessonId);
      if (expandedLessonId === lessonId) {
        setExpandedLessonId(null);
      }
      refetch();
    }
  };

  const openLessonEditor = (lesson: any) => {
    if (expandedLessonId === String(lesson.id)) {
      setExpandedLessonId(null);
    } else {
      setExpandedLessonId(String(lesson.id));
      setLessonFormData({
        title: lesson.title || "",
        description: lesson.description || lesson.content || "",
        video_url: lesson.video_url || "",
        pdf_url: lesson.pdf_url || "",
        duration_seconds: lesson.duration_seconds || (lesson.duration_minutes ? lesson.duration_minutes * 60 : 0),
        is_preview: Boolean(lesson.is_preview),
      });
    }
  };

  const handleSaveLesson = async (lessonId: string) => {
    await updateLessonMutation.mutateAsync({
      lessonId,
      title: lessonFormData.title,
      content: lessonFormData.description,
      video_url: lessonFormData.video_url,
      pdf_url: lessonFormData.pdf_url,
      duration_seconds: Number(lessonFormData.duration_seconds),
      is_preview: lessonFormData.is_preview,
    });
    alert("Lesson details updated successfully!");
    refetch();
  };

  const handleVideoUpload = async (lessonId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingVideoLessonId(lessonId);
    try {
      const res = await uploadVideoMutation.mutateAsync({ lessonId, file });
      setLessonFormData((prev) => ({ ...prev, video_url: res.video_url }));
      refetch();
      alert("Video uploaded successfully!");
    } catch (err) {
      console.error(err);
      alert("Video upload failed. Please try again.");
    } finally {
      setUploadingVideoLessonId(null);
    }
  };

  const handlePdfUpload = async (lessonId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingPdfLessonId(lessonId);
    try {
      const res = await uploadPdfMutation.mutateAsync({ lessonId, file });
      setLessonFormData((prev) => ({ ...prev, pdf_url: res.pdf_url }));
      refetch();
      alert("PDF resource uploaded successfully!");
    } catch (err) {
      console.error(err);
      alert("PDF upload failed. Please try again.");
    } finally {
      setUploadingPdfLessonId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-slate-600">Loading course builder...</span>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="py-16 text-center max-w-xl mx-auto">
        <h2 className="text-xl font-bold text-slate-900">Course not found</h2>
        <Link href="/instructor">
          <Button className="mt-4" variant="outline">
            Back to Studio
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      {/* Top Header */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/instructor" className="text-slate-500 hover:text-slate-900 transition-colors">
              <ChevronLeft className="h-5 w-5" />
            </Link>
            <div>
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">Course Builder</span>
              <h1 className="text-lg font-bold text-slate-900 line-clamp-1">{course.title}</h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link href={`/courses/${course.slug}`} target="_blank">
              <Button variant="outline" size="sm">
                Preview Course
              </Button>
            </Link>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-8">
          <button
            onClick={() => setActiveTab("curriculum")}
            className={`flex items-center gap-2 py-3 border-b-2 text-sm font-semibold transition-colors ${
              activeTab === "curriculum"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-900"
            }`}
          >
            <Layers className="h-4 w-4" /> Curriculum & Lessons
          </button>
          <button
            onClick={() => setActiveTab("details")}
            className={`flex items-center gap-2 py-3 border-b-2 text-sm font-semibold transition-colors ${
              activeTab === "details"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-900"
            }`}
          >
            <Settings className="h-4 w-4" /> Course Details
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {/* TAB 1: CURRICULUM */}
        {activeTab === "curriculum" && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Curriculum Structure</h2>
                <p className="text-sm text-slate-500 mt-1">
                  Organize your course into sections and upload video lessons with supplementary PDF resources.
                </p>
              </div>
              <Button onClick={() => setShowAddSection(true)} className="shrink-0">
                <Plus className="h-4 w-4 mr-2" /> Add Section
              </Button>
            </div>

            {/* Add Section Modal / Box */}
            {showAddSection && (
              <form
                onSubmit={handleAddSection}
                className="bg-blue-50 border border-blue-200 p-6 rounded-xl space-y-4 transition-all"
              >
                <h3 className="font-semibold text-slate-900 text-base">New Section</h3>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Section Title</label>
                  <Input
                    type="text"
                    required
                    placeholder="e.g. Introduction & Setup"
                    value={newSectionTitle}
                    onChange={(e) => setNewSectionTitle(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setShowAddSection(false);
                      setNewSectionTitle("");
                    }}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" size="sm" isLoading={createSectionMutation.isPending}>
                    Save Section
                  </Button>
                </div>
              </form>
            )}

            {/* Section List */}
            {(!course.sections || course.sections.length === 0) && !showAddSection ? (
              <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center">
                <Layers className="h-10 w-10 text-slate-300 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-slate-800">No sections added yet</h3>
                <p className="text-sm text-slate-500 mt-1 mb-4">
                  Every course needs at least one section before adding video lessons.
                </p>
                <Button onClick={() => setShowAddSection(true)}>
                  <Plus className="h-4 w-4 mr-2" /> Create First Section
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {course.sections?.map((section, sIndex) => (
                  <div key={section.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    {/* Section Header */}
                    <div className="bg-slate-100/70 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                      {editingSectionId === String(section.id) ? (
                        <div className="flex items-center gap-2 flex-1 mr-4">
                          <Input
                            value={editingSectionTitle}
                            onChange={(e) => setEditingSectionTitle(e.target.value)}
                            className="h-8 text-sm"
                            autoFocus
                          />
                          <Button size="sm" onClick={() => handleSaveSectionTitle(String(section.id))}>
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setEditingSectionId(null)}>
                            Cancel
                          </Button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                            Section {sIndex + 1}:
                          </span>
                          <h3 className="font-bold text-slate-900 text-base">{section.title}</h3>
                          <button
                            onClick={() => {
                              setEditingSectionId(String(section.id));
                              setEditingSectionTitle(section.title);
                            }}
                            className="text-slate-400 hover:text-slate-600 p-1 rounded"
                            title="Rename Section"
                          >
                            <Edit2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setAddingLessonSectionId(String(section.id));
                            setNewLessonTitle("");
                          }}
                        >
                          <Plus className="h-3.5 w-3.5 mr-1" /> Add Lesson
                        </Button>
                        <button
                          onClick={() => handleDeleteSection(String(section.id))}
                          className="text-slate-400 hover:text-red-600 p-1.5 rounded transition-colors"
                          title="Delete Section"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    {/* Add Lesson inline form */}
                    {addingLessonSectionId === String(section.id) && (
                      <div className="p-4 bg-emerald-50 border-b border-emerald-100 flex items-center gap-3">
                        <Input
                          placeholder="e.g. Lesson 1: Welcome & Environment Setup"
                          value={newLessonTitle}
                          onChange={(e) => setNewLessonTitle(e.target.value)}
                          className="h-9 text-sm"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              handleAddLesson(String(section.id));
                            }
                          }}
                        />
                        <Button size="sm" onClick={() => handleAddLesson(String(section.id))} isLoading={createLessonMutation.isPending}>
                          Add
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setAddingLessonSectionId(null)}>
                          Cancel
                        </Button>
                      </div>
                    )}

                    {/* Lesson Items */}
                    <div className="divide-y divide-slate-100">
                      {(!section.lessons || section.lessons.length === 0) && addingLessonSectionId !== String(section.id) ? (
                        <div className="p-6 text-center text-sm text-slate-400">
                          No lessons in this section yet. Click &quot;Add Lesson&quot; to begin.
                        </div>
                      ) : (
                        section.lessons?.map((lesson, lIndex) => {
                          const isExpanded = expandedLessonId === String(lesson.id);
                          return (
                            <div key={lesson.id} className="transition-colors">
                              {/* Lesson Row */}
                              <div className="p-4 flex items-center justify-between hover:bg-slate-50 gap-4">
                                <div
                                  className="flex items-center gap-3 flex-1 cursor-pointer select-none"
                                  onClick={() => openLessonEditor(lesson)}
                                >
                                  <span className="text-xs font-mono font-semibold text-slate-400 w-6">
                                    {lIndex + 1}.
                                  </span>
                                  <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                                    <Video className="h-4 w-4" />
                                  </div>
                                  <div>
                                    <h4 className="font-semibold text-slate-900 text-sm hover:text-blue-600 transition-colors">
                                      {lesson.title}
                                    </h4>
                                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                                      {lesson.video_url ? (
                                        <span className="flex items-center text-emerald-600">
                                          <CheckCircle className="h-3 w-3 mr-1" /> Video Uploaded
                                        </span>
                                      ) : (
                                        <span className="text-amber-500">No video</span>
                                      )}
                                      {lesson.pdf_url && (
                                        <span className="flex items-center text-blue-600">
                                          <FileText className="h-3 w-3 mr-1" /> PDF Attached
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                </div>

                                <div className="flex items-center gap-2">
                                  <Button
                                    size="sm"
                                    variant={isExpanded ? "secondary" : "outline"}
                                    onClick={() => openLessonEditor(lesson)}
                                    className="text-xs"
                                  >
                                    {isExpanded ? "Close" : "Edit & Upload"}
                                  </Button>
                                  <button
                                    onClick={() => handleDeleteLesson(String(lesson.id))}
                                    className="text-slate-400 hover:text-red-600 p-1.5 rounded transition-colors"
                                    title="Delete Lesson"
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </button>
                                </div>
                              </div>

                              {/* Expanded Lesson Editor Panel */}
                              {isExpanded && (
                                <div className="p-6 bg-slate-50 border-t border-slate-200 space-y-6">
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                                        Lesson Title
                                      </label>
                                      <Input
                                        value={lessonFormData.title}
                                        onChange={(e) =>
                                          setLessonFormData({ ...lessonFormData, title: e.target.value })
                                        }
                                      />
                                    </div>

                                    <div>
                                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                                        Estimated Duration (seconds)
                                      </label>
                                      <Input
                                        type="number"
                                        value={lessonFormData.duration_seconds}
                                        onChange={(e) =>
                                          setLessonFormData({
                                            ...lessonFormData,
                                            duration_seconds: Number(e.target.value),
                                          })
                                        }
                                        placeholder="e.g. 600 (10 mins)"
                                      />
                                    </div>
                                  </div>

                                  <div>
                                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                                      Lesson Notes / Description
                                    </label>
                                    <textarea
                                      rows={3}
                                      value={lessonFormData.description}
                                      onChange={(e) =>
                                        setLessonFormData({ ...lessonFormData, description: e.target.value })
                                      }
                                      className="w-full rounded-md border border-slate-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                                      placeholder="Summary of what is covered in this video..."
                                    />
                                  </div>

                                  {/* Upload Section: Video & PDF */}
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                                    {/* Video Upload Box */}
                                    <div className="p-4 bg-white rounded-xl border border-slate-200">
                                      <div className="flex items-center gap-2 mb-2 text-slate-900 font-semibold text-sm">
                                        <Video className="h-4 w-4 text-blue-600" />
                                        <span>Lesson Video</span>
                                      </div>
                                      {lessonFormData.video_url ? (
                                        <div className="space-y-2">
                                          <p className="text-xs text-emerald-600 flex items-center font-medium">
                                            <CheckCircle className="h-3.5 w-3.5 mr-1" /> Video file available
                                          </p>
                                          <div className="truncate text-xs font-mono text-slate-500 bg-slate-50 p-2 rounded border border-slate-200">
                                            {lessonFormData.video_url}
                                          </div>
                                        </div>
                                      ) : (
                                        <p className="text-xs text-slate-400 mb-3">No video uploaded yet.</p>
                                      )}
                                      <div className="mt-3">
                                        <label className="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-300 hover:bg-slate-50 text-xs font-medium text-slate-700">
                                          <Upload className="h-3.5 w-3.5 text-slate-500" />
                                          {uploadingVideoLessonId === String(lesson.id) ? (
                                            <>
                                              <Loader2 className="h-3 w-3 animate-spin" /> Uploading Video...
                                            </>
                                          ) : (
                                            "Upload Video File (MP4/WebM)"
                                          )}
                                          <input
                                            type="file"
                                            accept="video/*"
                                            className="hidden"
                                            onChange={(e) => handleVideoUpload(String(lesson.id), e)}
                                            disabled={uploadingVideoLessonId === String(lesson.id)}
                                          />
                                        </label>
                                      </div>
                                    </div>

                                    {/* PDF Resource Upload Box */}
                                    <div className="p-4 bg-white rounded-xl border border-slate-200">
                                      <div className="flex items-center gap-2 mb-2 text-slate-900 font-semibold text-sm">
                                        <FileText className="h-4 w-4 text-purple-600" />
                                        <span>Lesson PDF Resource</span>
                                      </div>
                                      {lessonFormData.pdf_url ? (
                                        <div className="space-y-2">
                                          <p className="text-xs text-purple-600 flex items-center font-medium">
                                            <CheckCircle className="h-3.5 w-3.5 mr-1" /> PDF resource available
                                          </p>
                                          <div className="truncate text-xs font-mono text-slate-500 bg-slate-50 p-2 rounded border border-slate-200">
                                            {lessonFormData.pdf_url}
                                          </div>
                                        </div>
                                      ) : (
                                        <p className="text-xs text-slate-400 mb-3">No supplementary PDF attached.</p>
                                      )}
                                      <div className="mt-3">
                                        <label className="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-300 hover:bg-slate-50 text-xs font-medium text-slate-700">
                                          <Upload className="h-3.5 w-3.5 text-slate-500" />
                                          {uploadingPdfLessonId === String(lesson.id) ? (
                                            <>
                                              <Loader2 className="h-3 w-3 animate-spin" /> Uploading PDF...
                                            </>
                                          ) : (
                                            "Upload PDF Notes / Handout"
                                          )}
                                          <input
                                            type="file"
                                            accept=".pdf,application/pdf"
                                            className="hidden"
                                            onChange={(e) => handlePdfUpload(String(lesson.id), e)}
                                            disabled={uploadingPdfLessonId === String(lesson.id)}
                                          />
                                        </label>
                                      </div>
                                    </div>
                                  </div>

                                  <div className="flex items-center justify-between pt-2 border-t border-slate-200">
                                    <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                                      <input
                                        type="checkbox"
                                        checked={lessonFormData.is_preview}
                                        onChange={(e) =>
                                          setLessonFormData({ ...lessonFormData, is_preview: e.target.checked })
                                        }
                                        className="rounded text-blue-600 focus:ring-blue-500"
                                      />
                                      Free Preview Lesson (allow non-enrolled students to watch)
                                    </label>

                                    <Button
                                      size="sm"
                                      onClick={() => handleSaveLesson(String(lesson.id))}
                                      isLoading={updateLessonMutation.isPending}
                                    >
                                      <Save className="h-3.5 w-3.5 mr-1" /> Save Lesson Details
                                    </Button>
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: COURSE DETAILS */}
        {activeTab === "details" && (
          <form
            onSubmit={handleSaveDetails}
            className="space-y-6 bg-white p-8 rounded-xl border border-slate-200 shadow-sm max-w-3xl"
          >
            <div>
              <h2 className="text-xl font-bold text-slate-900">General Course Information</h2>
              <p className="text-sm text-slate-500 mt-1">Update basic metadata, category, and pricing.</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Course Title</label>
              <Input required value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Subtitle</label>
              <Input value={subtitle} onChange={(e) => setSubtitle(e.target.value)} />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Course Description</label>
              <textarea
                required
                rows={5}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full rounded-md border border-slate-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(Number(e.target.value))}
                  className="w-full h-10 px-3 text-sm rounded-md border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Difficulty Level</label>
                <select
                  value={level}
                  onChange={(e) => setLevel(e.target.value)}
                  className="w-full h-10 px-3 text-sm rounded-md border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  {DIFFICULTY_LEVELS.map((dl) => (
                    <option key={dl} value={dl}>
                      {dl.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Price (USD)</label>
                <Input
                  type="number"
                  step="0.01"
                  required
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              {detailsSaved && (
                <span className="text-sm font-semibold text-emerald-600 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-1.5" /> Details saved successfully!
                </span>
              )}
              <div className="ml-auto">
                <Button type="submit" isLoading={updateCourseMutation.isPending}>
                  <Save className="h-4 w-4 mr-1.5" /> Save Changes
                </Button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

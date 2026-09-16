"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/ui/avatar";
import { BookOpen, Search, LogOut, LayoutDashboard, Menu, X } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout, isInstructor, isAdmin } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Logo & Main Nav */}
          <div className="flex items-center gap-4 md:gap-8">
            {/* Mobile Menu Toggle */}
            <button 
              className="md:hidden text-slate-600 hover:text-slate-900 focus:outline-none" 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>

            <Link href="/" className="flex items-center gap-2.5 font-bold text-xl text-blue-600">
              <div className="p-1.5 bg-blue-600 text-white rounded-lg hidden sm:block">
                <BookOpen className="h-6 w-6" />
              </div>
              <span className="text-slate-900">Course<span className="text-blue-600">Drive</span></span>
            </Link>

            <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
              <Link
                href="/courses"
                className={pathname === "/courses" ? "text-blue-600" : "text-slate-600 hover:text-slate-900"}
              >
                Explore Courses
              </Link>
              {isAuthenticated && (
                <Link
                  href="/my-learning"
                  className={pathname === "/my-learning" ? "text-blue-600" : "text-slate-600 hover:text-slate-900"}
                >
                  My Learning
                </Link>
              )}
              {isAuthenticated && (
                <Link
                  href="/certificates"
                  className={pathname === "/certificates" ? "text-blue-600" : "text-slate-600 hover:text-slate-900"}
                >
                  Certificates
                </Link>
              )}
            </nav>
          </div>

          {/* Search & Actions */}
          <div className="flex items-center gap-2 md:gap-4 flex-1 justify-end">
            <div className="hidden lg:flex items-center w-72 relative">
              <Search className="absolute left-3 h-4 w-4 text-slate-400" />
              <input
                placeholder="What do you want to learn?"
                className="w-full h-9 pl-9 pr-4 text-sm rounded-full border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-600"
              />
            </div>

            {isAuthenticated ? (
              <div className="flex items-center gap-3 relative">
                {isInstructor && (
                  <Link href="/instructor">
                    <Button variant="outline" size="sm" className="hidden sm:inline-flex">
                      Instructor Studio
                    </Button>
                  </Link>
                )}
                {isAdmin && (
                  <Link href="/admin">
                    <Button variant="secondary" size="sm" className="hidden sm:inline-flex">
                      Admin
                    </Button>
                  </Link>
                )}

                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setMenuOpen(!menuOpen)}
                    className="flex items-center gap-2 focus:outline-none"
                  >
                    <Avatar src={user?.avatar_url} fallback={user?.full_name?.charAt(0) || "U"} size="sm" />
                    <span className="hidden md:inline text-sm font-medium text-slate-700">
                      {user?.full_name}
                    </span>
                  </button>

                  {menuOpen && (
                    <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white p-1 shadow-lg border border-slate-100 z-50">
                      <div className="px-3 py-2 border-b border-slate-100">
                        <p className="text-sm font-semibold text-slate-900">{user?.full_name}</p>
                        <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                      </div>
                      <div className="py-1">
                        <Link
                          href="/my-learning"
                          onClick={() => setMenuOpen(false)}
                          className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-md"
                        >
                          <BookOpen className="h-4 w-4" /> My Learning
                        </Link>
                        {isInstructor && (
                          <Link
                            href="/instructor"
                            onClick={() => setMenuOpen(false)}
                            className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-md"
                          >
                            <LayoutDashboard className="h-4 w-4" /> Instructor Studio
                          </Link>
                        )}
                        <button
                          type="button"
                          onClick={() => {
                            setMenuOpen(false);
                            logout();
                          }}
                          className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
                        >
                          <LogOut className="h-4 w-4" /> Sign Out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link href="/login" className="hidden sm:block">
                  <Button variant="ghost" size="sm">Log in</Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Join for Free</Button>
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-100 space-y-4">
            <nav className="flex flex-col gap-4 text-sm font-medium px-2">
              <Link
                href="/courses"
                onClick={() => setMobileMenuOpen(false)}
                className={pathname === "/courses" ? "text-blue-600" : "text-slate-600"}
              >
                Explore Courses
              </Link>
              {isAuthenticated && (
                <>
                  <Link
                    href="/my-learning"
                    onClick={() => setMobileMenuOpen(false)}
                    className={pathname === "/my-learning" ? "text-blue-600" : "text-slate-600"}
                  >
                    My Learning
                  </Link>
                  <Link
                    href="/certificates"
                    onClick={() => setMobileMenuOpen(false)}
                    className={pathname === "/certificates" ? "text-blue-600" : "text-slate-600"}
                  >
                    Certificates
                  </Link>
                  {isInstructor && (
                    <Link
                      href="/instructor"
                      onClick={() => setMobileMenuOpen(false)}
                      className={pathname === "/instructor" ? "text-blue-600" : "text-slate-600"}
                    >
                      Instructor Studio
                    </Link>
                  )}
                  {isAdmin && (
                    <Link
                      href="/admin"
                      onClick={() => setMobileMenuOpen(false)}
                      className={pathname === "/admin" ? "text-blue-600" : "text-slate-600"}
                    >
                      Admin Dashboard
                    </Link>
                  )}
                </>
              )}
              {!isAuthenticated && (
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-slate-600"
                >
                  Log in
                </Link>
              )}
            </nav>
            {/* Mobile Search */}
            <div className="px-2">
              <div className="flex items-center w-full relative">
                <Search className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  placeholder="What do you want to learn?"
                  className="w-full h-10 pl-9 pr-4 text-sm rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-600"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

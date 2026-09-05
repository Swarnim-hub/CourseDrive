"""
CourseDrive comprehensive functionality test script.
Run: python test_all.py
"""
import asyncio
import httpx
import sys

BASE = "http://localhost:8000/api/v1"
FRONTEND = "http://localhost:3000"

passed = 0
failed = 0
results = []


async def test(label, coro):
    global passed, failed
    try:
        result = await coro
        passed += 1
        results.append(f"  [PASS] {label}")
        return result
    except Exception as e:
        failed += 1
        msg = str(e)[:120]
        results.append(f"  [FAIL] {label} => {msg}")
        return None


async def run():
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as c:

        # ── AUTH ────────────────────────────────────────────
        print("\n[AUTH]")
        admin_r = await test("Admin Login", c.post(f"{BASE}/auth/login", json={"email": "admin@coursedrive.com", "password": "admin123"}))
        AH = {"Authorization": f"Bearer {admin_r.json()['access_token']}"} if admin_r else {}

        ir = await test("Instructor Login", c.post(f"{BASE}/auth/login", json={"email": "prof2@cd.com", "password": "pass1234"}))
        IH = {"Authorization": f"Bearer {ir.json()['access_token']}"} if ir else {}

        sr = await test("Student Login", c.post(f"{BASE}/auth/login", json={"email": "jane2@cd.com", "password": "pass1234"}))
        SH = {"Authorization": f"Bearer {sr.json()['access_token']}"} if sr else {}

        r = await test("Get My Profile", c.get(f"{BASE}/users/me", headers=SH))
        await test("Update Profile Bio", c.put(f"{BASE}/users/me", json={"bio": "Love learning!"}, headers=SH))
        await test("Token Refresh", c.post(f"{BASE}/auth/refresh", json={"refresh_token": sr.json()["refresh_token"]}))

        # ── CATEGORIES ──────────────────────────────────────
        print("\n[CATEGORIES]")
        cats_r = await test("List Categories", c.get(f"{BASE}/categories"))
        cats = cats_r.json() if cats_r else []
        cat_id = cats[0]["id"] if cats else 1
        print(f"         Found {len(cats)} categories, using id={cat_id}")

        # ── COURSES ─────────────────────────────────────────
        print("\n[COURSES]")
        course_r = await test("Create Course (instructor)", c.post(f"{BASE}/courses", json={
            "title": "Python Masterclass", "description": "Complete Python A-Z guide",
            "level": "beginner", "price": 0, "category_id": cat_id, "is_free": True,
            "subtitle": "Zero to Hero"
        }, headers=IH))
        course = course_r.json() if course_r else {}
        cid = course.get("id")
        slug = course.get("slug")
        print(f"         Created course id={cid} slug={slug}")

        await test("Publish Course", c.put(f"{BASE}/courses/{cid}", json={"is_published": True}, headers=IH))
        cl = await test("List Published Courses", c.get(f"{BASE}/courses"))
        if cl: print(f"         Total published: {cl.json()['total']}")
        await test("Search Courses by keyword", c.get(f"{BASE}/courses?search=Python"))
        await test("Get Course by Slug", c.get(f"{BASE}/courses/{slug}"))

        # ── SECTIONS & LESSONS ───────────────────────────────
        print("\n[CONTENT]")
        sec_r = await test("Add Section", c.post(f"{BASE}/courses/{cid}/sections", json={"title": "Getting Started", "order": 1}, headers=IH))
        sec_id = sec_r.json()["id"] if sec_r else None

        les_r = await test("Add Video Lesson", c.post(f"{BASE}/lessons", json={
            "title": "Intro to Python", "section_id": sec_id, "lesson_type": "video",
            "order": 1, "video_url": "https://youtu.be/abc123", "duration_seconds": 600
        }, headers=IH))
        les_id = les_r.json()["id"] if les_r else None

        await test("List Course Sections", c.get(f"{BASE}/courses/{cid}/sections"))

        # ── ENROLLMENTS ─────────────────────────────────────
        print("\n[ENROLLMENTS]")
        enr_r = await test("Enroll in Free Course", c.post(f"{BASE}/enrollments", json={"course_id": cid}, headers=SH))
        if enr_r: print(f"         Status: {enr_r.json().get('status')}")
        await test("My Enrollments", c.get(f"{BASE}/enrollments/my", headers=SH))
        await test("Check Enrollment for Course", c.get(f"{BASE}/enrollments/course/{cid}", headers=SH))

        # ── PROGRESS ────────────────────────────────────────
        print("\n[PROGRESS]")
        await test("Mark Lesson Completed", c.post(f"{BASE}/lessons/{les_id}/progress", json={"is_completed": True, "time_spent_seconds": 600}, headers=SH))
        await test("Get Lesson Progress", c.get(f"{BASE}/lessons/{les_id}/progress", headers=SH))
        prog_r = await test("Get Course Progress", c.get(f"{BASE}/courses/{cid}/progress", headers=SH))
        if prog_r: print(f"         Progress: {prog_r.json().get('progress_percentage', '?')}%")

        # ── REVIEWS ─────────────────────────────────────────
        print("\n[REVIEWS]")
        await test("Add Review (5 stars)", c.post(f"{BASE}/courses/{cid}/reviews", json={"rating": 5, "comment": "Excellent course!"}, headers=SH))
        rev_r = await test("Get Course Reviews", c.get(f"{BASE}/courses/{cid}/reviews"))
        if rev_r: print(f"         Reviews: {len(rev_r.json())}")

        # ── DASHBOARD ────────────────────────────────────────
        print("\n[DASHBOARD]")
        await test("Student Dashboard", c.get(f"{BASE}/dashboard/student", headers=SH))
        await test("Instructor Dashboard", c.get(f"{BASE}/dashboard/instructor", headers=IH))
        await test("Instructor Analytics", c.get(f"{BASE}/dashboard/instructor/analytics", headers=IH))

        # ── NOTIFICATIONS ────────────────────────────────────
        print("\n[NOTIFICATIONS]")
        notif_r = await test("Get Notifications", c.get(f"{BASE}/notifications/", headers=SH))
        if notif_r: print(f"         Notifications: {len(notif_r.json())}")
        await test("Mark All Read", c.post(f"{BASE}/notifications/read", json={"mark_all": True}, headers=SH))

        # ── ADMIN ────────────────────────────────────────────
        print("\n[ADMIN]")
        stats_r = await test("Admin: Platform Stats", c.get(f"{BASE}/admin/stats", headers=AH))
        if stats_r: print(f"         users={stats_r.json().get('total_users')} courses={stats_r.json().get('total_courses')}")
        await test("Admin: List Users", c.get(f"{BASE}/admin/users", headers=AH))
        await test("Admin: List Courses", c.get(f"{BASE}/admin/courses", headers=AH))

        # ── FRONTEND PAGES ───────────────────────────────────
        print("\n[FRONTEND]")
        for path in ["/", "/courses", "/login", "/register", "/verify-otp"]:
            r = await test(f"Page {path}", c.get(f"{FRONTEND}{path}"))
            if r: print(f"         {path} => HTTP {r.status_code}")

    # ── RESULTS ─────────────────────────────────────────────
    print("\n" + "=" * 50)
    for line in results:
        color = "\033[92m" if "[PASS]" in line else "\033[91m"
        print(f"{color}{line}\033[0m")
    print("=" * 50)
    print(f"  PASSED: {passed}   FAILED: {failed}   TOTAL: {passed + failed}")
    print("=" * 50)
    return failed


if __name__ == "__main__":
    fails = asyncio.run(run())
    sys.exit(0 if fails == 0 else 1)

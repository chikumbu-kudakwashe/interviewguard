InterviewGuard
==============

InterviewGuard is a lightweight Django + vanilla JavaScript app for interview preparation, profile-based emergency alerts, and simple browser network checks. It is designed to stay usable on modest internet connections: no frontend build step, no heavy JavaScript framework, and a small JSON API.

Requirements
------------

- Python 3.12+
- `uv`
- A modern browser

Install
-------

```bash
uv sync
```

Database Setup
--------------

```bash
uv run python manage.py migrate
uv run python manage.py seed_data
```

`seed_data` is safe to run multiple times. It uses the existing `InterviewQuestion` model and updates or creates approved seed questions without duplicating matching question text.

Run The Backend
---------------

```bash
uv run python manage.py runserver 127.0.0.1:8000
```

Open The Frontend
-----------------

For a quick local static server:

```bash
cd frontend
python3 -m http.server 5050
```

Then open:

```txt
http://127.0.0.1:5050/index.html
```

API Endpoints
-------------

```txt
GET  /api/summary/
GET  /api/summary
GET  /api/questions/
POST /api/questions/submit/
GET  /api/questions/pending/   admin only
GET  /api/profiles/
POST /api/profiles/
PATCH /api/profiles/<uuid>/
POST /api/profiles/<uuid>/send_email/
GET  /api/ping/
GET  /api/download/?size=200000
POST /api/upload/
```

Question Review Flow
--------------------

InterviewGuard now uses one question model: `InterviewQuestion`.

- Seeded questions are saved with `status="approved"`.
- Public `GET /api/questions/` only returns approved questions.
- User submissions go through `POST /api/questions/submit/` and are saved with `status="pending"`.
- Pending questions are not public until approved in Django admin.
- Admins can approve or reject questions from `/admin/core/interviewquestion/`.

Summary Endpoint
----------------

`GET /api/summary/` returns dashboard data:

- total, approved, pending, and rejected question counts
- saved profile count
- approved counts by faculty
- approved counts by difficulty
- latest approved questions

Seed Data Sources
-----------------

The question bank is based on common internship and entry-level interview themes from university career centers and career-readiness guidance, including:

- NACE career readiness competencies: https://www.naceweb.org/career-readiness/competencies/career-readiness-defined
- University of Maryland interview types and STAR guidance: https://careers.umd.edu/find-jobs-internships/interviewing/types-of-interviews
- University of Cincinnati STAR method guide: https://www.uc.edu/campus-life/career-co-op-support/interviews/biginterview/star-method-behavioral-interview.html
- Harvard FAS technical interview guidance: https://careerservices.fas.harvard.edu/resources/technical-interviews/
- UMBC technical interview guidance: https://careers.umbc.edu/students/interview/types/technical-interviews/

Useful Checks
-------------

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test
node --check frontend/app.js
```

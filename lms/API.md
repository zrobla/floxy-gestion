# LMS API (DRF)

Base path: `/api/lms/`

## Auth & roles
- Auth: JWT via `Authorization: Bearer <token>`
- Roles: OWNER/ADMIN/MANAGER = full access; STAFF/CASHIER = read-only on catalog,
  can create their own enrollments, update their lesson progress, and submit quizzes/assignments.

## Core resources
- `GET /courses/` list courses
- `GET /modules/` list modules
- `GET /lessons/` list lessons
- `GET /resources/` list lesson resources
- `GET /assignments/` list assignments
- `GET /enrollments/` list enrollments (user-scoped)
- `GET /lesson-progress/` list lesson progress (user-scoped)
- `GET /assignment-submissions/` list submissions (user-scoped)
- `GET /badges/` list badges
- `GET /badge-awards/` list badge awards (user-scoped)
- `GET /certificates/` list certificates (user-scoped)

Admin users (OWNER/ADMIN/MANAGER) can `POST/PUT/PATCH/DELETE` on core resources.
Non-admin users can create their own enrollment via `POST /enrollments/` and manage
their own lesson progress via `POST/PUT/PATCH /lesson-progress/`.

## Example cURL
List courses:
```bash
curl -H "Authorization: Bearer $TOKEN" \\
  http://localhost:8000/api/lms/courses/
```

Submit a quiz:
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"enrollment_id":1,"answers":[{"question_id":10,"choice_id":55}]}' \\
  http://localhost:8000/api/lms/quizzes/1/submit/
```

Submit an assignment with KPI evidence:
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"enrollment_id":1,"response_text":"Mission terminée","evidence":[{"requirement_id":3,"value":8,"proof_url":"https://example.com/preuve"}]}' \\
  http://localhost:8000/api/lms/assignments/1/submit/
```

## Quiz submission
`POST /quizzes/{id}/submit/`
```json
{
  "enrollment_id": 1,
  "answers": [
    {"question_id": 10, "choice_id": 55},
    {"question_id": 11, "text_answer": "abidjan"}
  ]
}
```

## Assignment submission (KPI evidence)
`POST /assignments/{id}/submit/`
Accepte du `multipart/form-data` si `proof_file` est envoyé.
```json
{
  "enrollment_id": 1,
  "response_text": "Mission terminée",
  "evidence": [
    {
      "requirement_id": 3,
      "value": 8,
      "proof_url": "https://example.com/preuve",
      "proof_file": "<fichier>",
      "crm_client_id": 2,
      "activity_id": 5
    }
  ]
}
```

## Progress + awards
- `POST /enrollments/{id}/refresh/` recalculer la progression
- `POST /enrollments/{id}/award_badges/` attribuer les badges
- `POST /enrollments/{id}/issue_certificate/` émettre un certificat (admin)

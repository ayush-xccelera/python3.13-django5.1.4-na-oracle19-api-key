COMMIT_MESSAGE: Add note sharing (share/unshare, shared-with-me, shared retrieve) to Notes API

## Summary
We were asked to let a note's owner share notes with other API-key clients, revoke that
access, and let both owners and shared clients read a note. We added a `shared_with`
many-to-many relationship on `Note`, four new/changed endpoints on the existing
`NoteViewSet` (share, unshare, retrieve, shared-with-me), and matching tests. All existing
and new tests pass locally against the project's own SQLite fallback database.

## Features Added
- `POST /api/v1/notes/{id}/share/` — owner shares a note with another client via `client_id`.
  Returns 200 with the note (including a `shared_with` array), 404 if note/client don't
  exist, 400 if sharing with the owner itself.
- `DELETE /api/v1/notes/{id}/share/{client_id}` — owner revokes a client's access.
  Returns 204 on success, 404 if the note or client doesn't have access. This route is
  wired without a trailing slash to match the literal spec path.
- `GET /api/v1/notes/{id}/` — now also returns the note when the caller is a client the
  note was shared with (previously owner-only).
- `GET /api/v1/notes/shared-with-me/` — paginated (limit/offset, default 20), newest-first
  list of notes shared with the authenticated caller.
- Ownership/access rules preserved: only the owner can share/revoke/update/delete a note;
  shared clients get read-only access via retrieve/shared-with-me and cannot modify notes
  (update/delete/archive/restore/share/unshare remain scoped to `get_object()`, which is
  owner-only, so a shared (non-owner) caller gets 404 on those).

## Files Modified
- `notes/models.py` — added `Note.shared_with` (M2M to `ApiKey`, related_name `shared_notes`).
- `notes/serializers.py` — `NoteSerializer` now exposes read-only `shared_with` (list of client IDs).
- `notes/views.py` — added `retrieve` override (owner or shared client), `shared_with_me`,
  `share`, and `unshare` actions on `NoteViewSet`.
- `notes/urls.py` — added an explicit `re_path` for the no-trailing-slash
  `DELETE .../share/{client_id}` route (DRF's router otherwise forces a trailing slash).
- `config/settings.py` — `load_dotenv` now points at `.env_68c8a273c320d894` (was pointing
  at a job-specific env filename from a previous run).
- `tests/test_notes.py` — added tests covering share success, self-share rejection, missing
  client/note 404s, shared client read-only retrieve, shared-with-me listing, and unshare.

## Files Added
- `notes/migrations/0002_note_shared_with.py` — migration adding the `shared_with` M2M table.

## Secrets Extracted
- No new hardcoded secrets were introduced. Existing `os.getenv(...)` values (SECRET_KEY,
  ADMIN_API_KEY, DB_USER, DB_PASSWORD, etc.) were consolidated into
  `.env_68c8a273c320d894` (variable names: SECRET_KEY, DEBUG, ADMIN_API_KEY, DB_ENGINE,
  DB_NAME, DB_HOST, DB_PORT, DB_SERVICE_NAME, DB_USER, DB_PASSWORD, FORCE_ORACLE).

## DB URLs Resolved
- None. The project targets Oracle via DB_HOST/DB_PORT/DB_SERVICE_NAME/DB_USER/DB_PASSWORD,
  but automatically falls back to a local SQLite database (`db.sqlite3`) when the Oracle
  instance is unreachable — this fallback triggered in this sandbox, so no external DB URL
  resolution was required.

## Test Results Summary
22 PASSED, 0 FAILED, 0 SKIPPED (pytest suite, including 7 new sharing tests). Manual curl
verification of all 4 new/changed endpoints and their success/error paths also passed.

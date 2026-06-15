# Repository and Deployment Handoff

Private GitHub repository:

<https://github.com/laraimad/roadsense-response>

The local challenge folder is linked to this repository on the `main` branch. The `.gitignore` excludes virtual environments, runtime state, caches, test artifacts, and local source-package archives.

## Render deployment

1. Sign in to <https://render.com>.
2. Choose **New > Blueprint**.
3. Connect the GitHub repository.
4. Confirm the service name and deploy.
5. Open `/api/health`; it should return `{"status":"ok"}`.
6. Add the public URL to `SUBMISSION_CHECKLIST.md`.

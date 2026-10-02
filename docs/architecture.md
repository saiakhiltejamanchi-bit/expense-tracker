# Architecture

Django follows Model–Template–View (MTV):

```
Browser → config/urls.py → app urls.py → view → (models) → template → HTML
```

- **config/** — project settings and the root URL file. Settings read secrets and
  the database choice from environment variables (`.env`).
- **accounts/** — will hold registration/login/logout. Uses Django's built-in
  `User`; no custom user model, so there is nothing to migrate for it.
- **tracker/** — the domain: models (Category, Transaction, Budget), admin, views.
- **templates/** — project-level templates; `base.html` is extended by pages.
- **static/** — CSS and JavaScript served by `django.contrib.staticfiles`.

Security foundation: CSRF middleware, session authentication, password
validators, no secrets in the repository (`.env` is git-ignored, and the app
refuses to start without `DJANGO_SECRET_KEY`).

Every record belongs to a user. Later views must always filter by
`request.user` so users can never see each other's data.

# CI/CD Pipeline for SaaS CRM + Booking Backend

This directory contains CI/CD workflow files for automated testing and deployment.

## Files

1. `.github/workflows/ci.yml` - Continuous Integration
2. `.github/workflows/cd.yml` - Continuous Deployment (manual trigger)

---

## CI Pipeline (.github/workflows/ci.yml)

Triggers on:
- Push to `main` and `develop` branches
- Pull requests to `main` and `develop`

Jobs:
1. **Lint** - Code quality checks
2. **Test** - Unit and integration tests
3. **Security** - Vulnerability scanning

---

## CD Pipeline (.github/workflows/cd.yml)

Manual trigger with workflow dispatch.

Requires secrets:
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `JWT_SECRET` - JWT signing secret
- `DEPLOY_HOST` - SSH host for deployment
- `DEPLOY_USER` - SSH username
- `DEPLOY_KEY` - SSH private key

---

## Usage

### CI runs automatically on:
```bash
git push origin main
git push origin develop
```

### CD requires manual trigger:
Go to GitHub → Actions → Deploy Production → Run workflow

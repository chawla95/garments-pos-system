## Azure Deployment (Frontend + Backend)

This guide deploys:
- Frontend (React CRA) to Azure Static Web Apps
- Backend (FastAPI) to Azure App Service (Linux)

You’ll set two GitHub Actions workflows that auto-deploy on push to `main`.

### Prerequisites
- Azure subscription
- GitHub repo connected to this codebase
- Admin access to set GitHub Secrets

---

## 1) Frontend → Azure Static Web Apps

### Create Static Web App
1. In Azure Portal, create “Static Web App”.
   - Deployment source: GitHub (you can also choose “Other” and supply token later)
   - Build preset: React
   - App location: `pos-frontend`
   - Output location: `build`
2. After creation, open the Static Web App → Overview to note the default domain (e.g., `https://<name>.azurestaticapps.net`).
3. Get your Deployment Token: Static Web App → Manage deployment token.

### GitHub Secret
Add a repository secret:
- `AZURE_STATIC_WEB_APPS_API_TOKEN`: paste the deployment token

### Frontend environment
If your frontend needs backend URL at build/run time, set it via SWA “Configuration” or as a GitHub Actions env:
- `REACT_APP_API_URL` → your backend URL once it’s live (you can update later).

### Deploy
The workflow `.github/workflows/frontend-azure-swa.yml` builds and deploys the app.

---

## 2) Backend → Azure App Service (Linux)

We’ll deploy the FastAPI app to an Azure Web App (Linux, Python) using a Publish Profile.

### Create the Web App
1. In Azure Portal: Create → Web App
   - Publish: Code
   - Runtime stack: Python 3.11 (Linux)
   - Region/Resource group: your choice
2. After creation, in the Web App → Settings → Configuration, add App Settings (Environment Variables) from your current deployment:
   - Database credentials (e.g., `DATABASE_URL`)
   - JWT secret(s) (e.g., `SECRET_KEY`)
   - Any other required envs used by `config.py`/`main.py`
3. Optional (recommended): Set Startup Command to run with Gunicorn + Uvicorn worker:
   - Startup Command: `gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app`
4. Get “Publish Profile”: Web App → Get publish profile (downloads an XML file).

### GitHub Secret
Add a repository secret:
- `AZURE_WEBAPP_PUBLISH_PROFILE`: contents of the downloaded publish profile XML

### CORS
Update `main.py` CORS `allow_origins` to include your SWA domain (e.g., `https://<name>.azurestaticapps.net`). Keep `http://localhost:3000` for local dev.

### Deploy
The workflow `.github/workflows/backend-azure-appservice.yml` installs dependencies, zips the app, and deploys via the publish profile.

Secrets required:
- `AZURE_WEBAPP_NAME`: your Web App name
- `AZURE_WEBAPP_PUBLISH_PROFILE`: XML contents of the publish profile

---

## 3) Wire Frontend to Backend
- In SWA configuration or in the frontend build environment, set `REACT_APP_API_URL` to your Web App URL (e.g., `https://<backend-app-name>.azurewebsites.net`).
- Redeploy frontend to pick up the new environment variable if needed.

### CORS updates in `main.py`
Add your SWA hostname to `allow_origins`:
- `https://<your-swa>.azurestaticapps.net`
- keep local dev origins too

---

## 4) Custom Domains (Optional)
- Add custom domains in Static Web Apps and App Service → Custom domains
- Configure DNS (CNAME)

---

## 5) GitHub Actions Summary

Frontend (Static Web Apps):
- Triggers on push to `main` in `pos-frontend/`
- Builds CRA → `build`
- Deploys to SWA using `AZURE_STATIC_WEB_APPS_API_TOKEN`

Backend (App Service):
- Triggers on push to `main` backend paths
- Installs Python deps
- Deploys via `AZURE_WEBAPP_PUBLISH_PROFILE`

---

## 6) Post-Deploy Checks
1. Backend health: `https://<backend-app-name>.azurewebsites.net/health`
2. Frontend loads and calls API successfully
3. CORS headers present in backend responses for SWA origin
4. Returns logic, products, invoices all functional


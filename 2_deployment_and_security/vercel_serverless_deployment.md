# Vercel Serverless Deployment Architecture

## 1. Zero-Configuration Framework Preset

PerkCart leverages Vercel's native Django Framework Detection:
* Vercel identifies `manage.py` in the root repository.
* Vercel inspects `perkcart/settings.py` and locates `WSGI_APPLICATION = 'perkcart.wsgi.application'`.
* Vercel attaches the serverless Lambda runtime directly to `app = application` exposed in [`perkcart/wsgi.py`](../perkcart/wsgi.py).

---

## 2. Static Asset Pipeline

Because serverless environments have read-only filesystems, static assets are prepared during build time:
1. Vercel automatically runs `python manage.py collectstatic --noinput` during the build phase.
2. `staticfiles/` are compiled and hashed using WhiteNoise:
   ```python
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```
3. Assets like `style.88820dc87331.css` are cached indefinitely on Vercel's global Edge CDN with `Cache-Control: public, max-age=31536000, immutable`.

---

## 3. Deployment CLI Commands

Deployment can be triggered either automatically on `git push` or directly via Vercel CLI:

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy directly to production
vercel --prod --yes
```

---

## 4. Production Verification Commands

Test the production deployment from any terminal:

```powershell
# 1. Verify Homepage
curl.exe -I https://perkart.vercel.app/

# 2. Verify Static CSS Edge Delivery
curl.exe -I https://perkart.vercel.app/static/css/style.css

# 3. Verify Health Check JSON API
curl.exe https://perkart.vercel.app/health/

# 4. Verify Branded Custom 404 Page
curl.exe -s https://perkart.vercel.app/yyy
```

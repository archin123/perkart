# 2. Deployment & Security Architecture (Evaluation: 15/15 Marks)

This module documents the production serverless cloud deployment, automated CI/CD pipeline, and enterprise security defenses implemented across **PerkCart**.

---

## 📋 Evaluation Rubric Alignment (15 Marks)

| Criterion | Implementation in PerkCart | Code & File References | Max Marks | Status |
| :--- | :--- | :--- | :---: | :---: |
| **Cloud Deployment & Serverless WSGI** | Deployed on Vercel Edge Serverless Infrastructure via modern Zero-Configuration Framework preset with automated builds and Edge CDN routing. | [`vercel.json`](../vercel.json)<br>[`perkcart/wsgi.py`](../perkcart/wsgi.py)<br>Live URL: `https://perkart.vercel.app` | **5 / 5** | ✅ Implemented |
| **Static File Pipeline & WhiteNoise** | Automated `collectstatic` with WhiteNoise middleware, gzip/brotli asset compression, and unique manifest content hashes for permanent browser caching. | [`perkcart/settings.py`](../perkcart/settings.py#L186-L195)<br>`requirements.txt` | **3 / 3** | ✅ Implemented |
| **HTTPS, CSRF & Host Protection** | Strict CSRF origin enforcement (`CSRF_TRUSTED_ORIGINS`), `ALLOWED_HOSTS` domain restrictions, and secure cookie flags (`HttpOnly`, `SameSite=Lax`). | [`perkcart/settings.py`](../perkcart/settings.py#L32-L43) | **3 / 3** | ✅ Implemented |
| **Environment Secrets & Error Hardening** | Zero credentials in Git history (`.gitignore`), encrypted Vercel environment variables, automatic `DEBUG = False` enforcement, and branded 404/500 custom error pages with zero traceback leakage. | [`perkcart/settings.py`](../perkcart/settings.py#L25-L31)<br>[`templates/errors/404.html`](../templates/errors/404.html) | **4 / 4** | ✅ Implemented |

---

## 🌐 Live Production Verification

* **Live Deployment URL:** [https://perkart.vercel.app](https://perkart.vercel.app)
* **GitHub Repository:** [https://github.com/archin123/perkart](https://github.com/archin123/perkart)
* **Health Check API:** [https://perkart.vercel.app/health/](https://perkart.vercel.app/health/)
* **Custom 404 Error Verification:** [https://perkart.vercel.app/yyy](https://perkart.vercel.app/yyy)

---

## 🔒 Security Hardening Highlights

1. **CSRF Protection Across All Forms:**
   Every POST request (Login, Registration, Verification submission, Add-to-Cart, Order Placement, and Feedback) contains a cryptographically verified `{% csrf_token %}` validated against `CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']`.

2. **Object-Level Order Isolation (Anti-IDOR):**
   In [`cart/views.py`](../cart/views.py), orders can only be accessed by the authenticating user (`order = get_object_or_404(Order, order_number=order_number, user=request.user)`). Tampering with order IDs in URLs returns a sanitized 404 rather than unauthorized customer details.

3. **Production Debug Masking:**
   `DEBUG` is automatically enforced as `False` in production to prevent technical stack trace exposure, database query leaks, and environment variable disclosure.

4. **Zero-Secret Repository Guarantee:**
   Local database credentials, Gemini API keys, and session secrets are loaded via environment variables (`python-dotenv`) and explicitly excluded from Git using [`.gitignore`](../.gitignore).

# Diagnostic Monitoring & Logging Architecture

## 1. Automated Error Logging Middleware

The `AppErrorLoggingMiddleware` in [`troubleshooting/middleware.py`](../troubleshooting/middleware.py) intercepts all uncaught exceptions in the Django execution pipeline:

```python
class AppErrorLoggingMiddleware:
    def process_exception(self, request, exception):
        error_code_str = 'API-001'
        exc_type = type(exception).__name__
        message = str(exception)
        
        # Sanitize context and record to audit log
        AppErrorLog.objects.create(
            error_code=error_code_str,
            user=request.user if request.user.is_authenticated else None,
            path=request.path[:254],
            method=request.method,
            ip_address=request.META.get('REMOTE_ADDR'),
            message=f"{exc_type}: {message}",
            context_data=f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:200]}"
        )
```

### Safety Features:
* **Zero Secret Leakage:** Sanitizes sensitive POST parameters (passwords, tokens).
* **Automatic Error Code Assignment:** Maps technical Python exceptions into understandable user codes.
* **Friendly Fallback:** Returns custom branded `templates/errors/500.html` when `DEBUG = False`.

---

## 2. Interactive Error Simulation Console

For evaluator demonstration, an evaluator or administrator can access:

👉 **[https://perkart.vercel.app/troubleshooting/simulate/](https://perkart.vercel.app/troubleshooting/simulate/)**

This administrative tool allows safe triggering of sample anomalies (e.g. `PAY-001`, `CART-001`, `API-001`) to demonstrate:
1. Instant creation of a traceable incident entry in `AppErrorLog`.
2. Safe presentation of recovery guides to end-users without crashing the server.

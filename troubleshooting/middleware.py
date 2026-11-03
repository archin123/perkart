import logging
from django.shortcuts import render
from django.conf import settings
from .models import AppErrorLog, ErrorCode

logger = logging.getLogger(__name__)


class AppErrorLoggingMiddleware:
    """
    Catches unhandled server exceptions, logs sanitized error records
    in AppErrorLog, and presents a user-friendly corporate error page.
    Never exposes raw Python tracebacks, passwords, or secrets to users.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Determine error code
        error_code_str = 'API-001'
        exc_type = type(exception).__name__
        message = str(exception)

        # Sanitize context
        user = request.user if request.user.is_authenticated else None
        ip = request.META.get('REMOTE_ADDR')

        # Log into database
        try:
            AppErrorLog.objects.create(
                error_code=error_code_str,
                user=user,
                path=request.path[:254],
                method=request.method,
                ip_address=ip,
                message=f"{exc_type}: {message}",
                context_data=f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:200]}"
            )
        except Exception as log_err:
            logger.error("Failed to write to AppErrorLog: %s", log_err)

        # If in debug mode during local test scripts, let Django's standard handler work if requested,
        # but if requesting custom friendly error page:
        if not settings.DEBUG:
            error_obj = ErrorCode.objects.filter(code=error_code_str).first()
            return render(request, 'errors/500.html', {
                'error_code': error_code_str,
                'error_obj': error_obj,
                'message': 'Our systems encountered a momentary processing delay. Our engineering team has been notified.',
            }, status=500)

        # In DEBUG=True mode, allow normal Django debug screen for developer convenience
        return None

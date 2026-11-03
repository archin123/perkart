from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ErrorCode, AppErrorLog


def error_code_list_view(request):
    """
    Searchable, filterable troubleshooting knowledgebase for error codes.
    Filter by category and severity with real-time feedback.
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    severity = request.GET.get('severity', '').strip()

    error_codes = ErrorCode.objects.filter(is_active=True)

    if query:
        error_codes = error_codes.filter(
            Q(code__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(troubleshooting_steps__icontains=query)
        )

    if category:
        error_codes = error_codes.filter(category=category)

    if severity:
        error_codes = error_codes.filter(severity=severity)

    return render(request, 'troubleshooting/error_list.html', {
        'error_codes': error_codes,
        'query': query,
        'selected_category': category,
        'selected_severity': severity,
        'categories': ErrorCode.CATEGORY_CHOICES,
        'severities': ErrorCode.SEVERITY_CHOICES,
        'total_count': error_codes.count(),
    })


def error_code_detail_view(request, code):
    """
    Detailed resolution guide for a specific error code.
    """
    error_obj = get_object_or_404(ErrorCode, code=code.upper(), is_active=True)
    related_errors = ErrorCode.objects.filter(
        category=error_obj.category,
        is_active=True
    ).exclude(code=error_obj.code)[:4]

    return render(request, 'troubleshooting/error_detail.html', {
        'error_obj': error_obj,
        'related_errors': related_errors,
    })


@login_required
def simulate_error_view(request):
    """
    Safe administrative demonstration feature:
    Allows an evaluator or admin to trigger sample errors, inspect the generated
    AppErrorLog entry, and observe how the application handles and resolves them
    without exposing raw Python tracebacks.
    """
    if not request.user.is_staff:
        messages.error(request, "Access restricted. Staff / Evaluator privileges required (SEC-001).")
        return redirect('troubleshooting:error_list')

    recent_logs = AppErrorLog.objects.all().order_by('-timestamp')[:10]
    error_choices = ErrorCode.objects.filter(is_active=True)

    if request.method == 'POST':
        selected_code = request.POST.get('error_code', 'CART-001')
        simulation_note = request.POST.get('simulation_note', 'Admin simulated error demonstration')

        error_item = ErrorCode.objects.filter(code=selected_code).first()
        err_msg = error_item.title if error_item else "Simulated demonstration anomaly."

        # Create simulated log entry
        log_entry = AppErrorLog.objects.create(
            error_code=selected_code,
            user=request.user,
            path=request.path,
            method='POST',
            ip_address=request.META.get('REMOTE_ADDR'),
            message=f"[DEMO SIMULATION] {err_msg}",
            context_data=f"Triggered by admin '{request.user.username}'. Note: {simulation_note}"
        )

        messages.info(
            request,
            f"Simulated error [{selected_code}] recorded in AppErrorLog (ID #{log_entry.id}). Inspect details below."
        )
        return redirect('troubleshooting:simulate_error')

    return render(request, 'troubleshooting/simulate_error.html', {
        'recent_logs': recent_logs,
        'error_choices': error_choices,
    })

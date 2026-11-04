import time
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from products.models import Product, ProductCategory, Offer
from faq.models import FAQ
from troubleshooting.models import ErrorCode
from .models import Feedback


def home_view(request):
    """
    PerkCart Homepage inspired by Samsung corporate shopping portal:
    - Clean white background, generous whitespace, modern typography
    - Hero promotional banner
    - Product categories
    - Featured products
    - Corporate employee privileges banner
    - Active promotional coupon deals
    - Quick AI assistant spotlight
    """
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
    categories = ProductCategory.objects.filter(is_active=True).order_by('order')[:6]
    offers = Offer.objects.filter(is_active=True).order_by('-discount_percent')[:3]
    top_faqs = FAQ.objects.filter(is_active=True).order_by('-helpful_count')[:4]

    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'offers': offers,
        'top_faqs': top_faqs,
    })


def global_search_view(request):
    """
    Unified multi-domain search across Products, FAQs, Error Codes, and Offers.
    """
    query = request.GET.get('q', '').strip()

    products = []
    faqs = []
    error_codes = []
    offers = []

    if query:
        products = Product.objects.filter(is_active=True).filter(
            name__icontains=query
        )[:6]
        faqs = FAQ.objects.filter(is_active=True).filter(
            question__icontains=query
        )[:4]
        error_codes = ErrorCode.objects.filter(is_active=True).filter(
            code__icontains=query
        ) | ErrorCode.objects.filter(is_active=True).filter(
            title__icontains=query
        )[:3]
        offers = Offer.objects.filter(is_active=True).filter(
            code__icontains=query
        ) | Offer.objects.filter(is_active=True).filter(
            title__icontains=query
        )[:3]

    total_results = len(products) + len(faqs) + len(error_codes) + len(offers)

    return render(request, 'core/search_results.html', {
        'query': query,
        'products': products,
        'faqs': faqs,
        'error_codes': error_codes,
        'offers': offers,
        'total_results': total_results,
    })


def feedback_view(request):
    """
    Feedback submission form with server-side validation and database storage.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        category = request.POST.get('category', 'EXPERIENCE')
        rating_str = request.POST.get('rating', '5')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                rating = 5
        except (ValueError, TypeError):
            rating = 5

        if not (name and email and message):
            messages.error(request, "Please fill in all required fields (Name, Email, Message).")
            return render(request, 'core/feedback.html', {'form_data': request.POST})

        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            company_name=company_name,
            category=category,
            rating=rating,
            subject=subject or f"Employee Feedback ({category})",
            message=message,
        )

        messages.success(
            request,
            "Thank you! Your feedback has been received and forwarded to our Corporate Partner Operations team."
        )
        return redirect('core:feedback')

    initial_data = {}
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        initial_data = {
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': profile.corporate_email if profile and profile.corporate_email else request.user.email,
            'company_name': profile.company_name if profile else '',
        }

    feedbacks = Feedback.objects.filter(rating__gte=4).order_by('-created_at')[:4]

    return render(request, 'core/feedback.html', {
        'form_data': initial_data,
        'categories': Feedback.CATEGORY_CHOICES,
        'feedbacks': feedbacks,
    })


def health_check_view(request):
    """
    Basic health-check endpoint.
    Returns JSON with operational health without revealing internal credentials or secrets.
    """
    db_status = "connected"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_status = "unavailable"

    status_code = 200 if db_status == "connected" else 503

    from django.conf import settings
    return JsonResponse({
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "debug": settings.DEBUG,
        "env_debug": os.getenv('DEBUG'),
        "has_env": (settings.BASE_DIR / '.env').exists(),
        "timestamp": timezone.now().isoformat(),
        "service": "PerkCart Corporate Platform",
        "version": "1.0.0",
    }, status=status_code)


def system_status_view(request):
    """
    Operational status page displaying system metrics, uptime, and service health.
    """
    db_status = "Operational"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_status = "Degraded"

    from django.conf import settings
    ai_engine = "Gemini AI API (Online)" if getattr(settings, 'GEMINI_API_KEY', '') else "Search-Based Fallback Engine (Active)"

    product_count = Product.objects.filter(is_active=True).count()
    faq_count = FAQ.objects.filter(is_active=True).count()
    error_count = ErrorCode.objects.filter(is_active=True).count()

    return render(request, 'core/system_status.html', {
        'db_status': db_status,
        'ai_engine': ai_engine,
        'product_count': product_count,
        'faq_count': faq_count,
        'error_count': error_count,
        'current_time': timezone.now(),
    })

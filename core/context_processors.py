from django.conf import settings
from products.models import ProductCategory, Offer, Wishlist
from cart.cart import Cart


def global_perkcart_context(request):
    """
    Supplies global template context across all pages:
    - Cart items count
    - Wishlist count for logged-in user
    - Product categories for navigation bar
    - Active promotional corporate offers
    - Corporate verification status
    """
    cart = Cart(request)
    cart_count = len(cart)
    
    wishlist_count = 0
    user_profile = None
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        user_profile = getattr(request.user, 'profile', None)

    categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    active_offers = Offer.objects.filter(is_active=True).order_by('-discount_percent')[:3]

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'nav_categories': categories,
        'active_offers': active_offers,
        'user_profile': user_profile,
        'IS_DEBUG': settings.DEBUG,
        'SITE_NAME': 'PerkCart',
        'SITE_TAGLINE': 'Corporate Employee Privilege Shopping',
    }

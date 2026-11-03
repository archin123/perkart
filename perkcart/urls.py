"""
URL configuration for perkcart project.
PerkCart - Corporate Employee Shopping Platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom Admin branding
admin.site.site_header = "PerkCart Corporate Portal Administration"
admin.site.site_title = "PerkCart Admin"
admin.site.index_title = "Corporate Portal Management & Monitoring"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('faq/', include('faq.urls')),
    path('troubleshooting/', include('troubleshooting.urls')),
    path('ai-assistant/', include('assistant.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth (allauth)
    path('auth/', include('allauth.urls')),

    # App URLs
    path('', include('apps.users.urls')),
    path('panel/', include('apps.users.admin_urls')),
    path('memberships/', include('apps.memberships.urls')),
    path('workouts/', include('apps.workouts.urls')),
    path('diet/', include('apps.diet.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('payments/', include('apps.payments.urls')),

    # API
    path('api/v1/', include([
        path('users/', include('apps.users.api_urls')),
        path('memberships/', include('apps.memberships.api_urls')),
        path('workouts/', include('apps.workouts.api_urls')),
        path('diet/', include('apps.diet.api_urls')),
        path('bookings/', include('apps.bookings.api_urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site
admin.site.site_header = "GymPlatform Admin"
admin.site.site_title = "GymPlatform"
admin.site.index_title = "Platform Management"

# Custom error handlers
handler404 = 'apps.users.views.error_404'
handler500 = 'apps.users.views.error_500'

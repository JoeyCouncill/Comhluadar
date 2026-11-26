from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import activity_counts


urlpatterns = [
    path('', include('services.urls')),
    path('', include('accounts.urls')),
    path('', include('messaging.urls')),
    path('notifications/', include("notifications.urls")),
    path("activity/counts/", activity_counts, name="activity_counts"),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

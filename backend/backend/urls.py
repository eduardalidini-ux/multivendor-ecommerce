"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView
# drf-yasg imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="E-commerce Backend APIs",
      default_version='v1',
      description="This is the API documentation for e-commerce project APIs",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="eduard.alidini@fshnstudent.info"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   authentication_classes=(),
   permission_classes=(permissions.AllowAny,),
)


@require_http_methods(["GET", "POST"])
def admin_logout(request):
    logout(request)
    return redirect(request.GET.get("next") or "/admin/")

urlpatterns = [
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API V1 Urls
    path("api/v1/", include("api.urls")),

    # Admin URL
    path('admin/logout/', admin_logout, name='admin-logout'),
    path('admin/', admin.site.urls),
]


if not getattr(settings, "USE_S3_MEDIA", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
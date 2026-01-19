from django.db.utils import OperationalError, ProgrammingError


def site_branding(request):
    try:
        from addon.models import SiteBranding
        branding = SiteBranding.objects.first()
    except (OperationalError, ProgrammingError):
        branding = None
    except Exception:
        branding = None

    return {"site_branding": branding}

from django.contrib import admin
from addon.models import Tax, ConfigSettings, SiteBranding
from import_export.admin import ImportExportModelAdmin

class TaxAdmin(ImportExportModelAdmin):
    list_editable = [ 'rate', 'active']
    list_display = ['country', 'rate', 'active']

admin.site.register(Tax, TaxAdmin)
admin.site.register(ConfigSettings)


@admin.register(SiteBranding)
class SiteBrandingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteBranding.objects.exists()
# Register your models here.

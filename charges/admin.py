from django.contrib import admin
from .models import ChargeType

# Register your models here.
class ChargeTypeAdmin(admin.ModelAdmin):
    search_fields = ['code','name']
    def get_queryset(self, request):
        return ChargeType.objects.all()

admin.site.register(ChargeType, ChargeTypeAdmin)

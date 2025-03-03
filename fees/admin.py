from django.contrib import admin
from .models import Agent, BkgeClass, Producer

class AgentAdmin(admin.ModelAdmin):
    search_fields = ['first_name','last_name','agent_code','is_external','is_gst_exempt']
    def get_queryset(self, request):
        return Agent.objects.all()

class BkgeClassAdmin(admin.ModelAdmin):
    search_fields = ['code','name']
    def get_queryset(self, request):
        return BkgeClass.objects.all()

class ProducerAdmin(admin.ModelAdmin):
    search_fields = ['code','name']
    def get_queryset(self, request):
        return Producer.objects.all()

admin.site.register(Agent, AgentAdmin)
admin.site.register(Producer, ProducerAdmin)
admin.site.register(BkgeClass, BkgeClassAdmin)


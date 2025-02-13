from django.contrib import admin
from .models import Agent

class AgentAdmin(admin.ModelAdmin):
    search_fields = ['first_name','last_name','agent_code','is_external','is_gst_exempt']
    def get_queryset(self, request):
        return Agent.objects.all()

admin.site.register(Agent, AgentAdmin)

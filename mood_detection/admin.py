from django.contrib import admin
from .models import MoodDetectionResult

@admin.register(MoodDetectionResult)
class MoodDetectionResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'confidence', 'detected_at']
    list_filter = ['mood', 'detected_at']
    search_fields = ['user__email', 'mood']
    readonly_fields = ['detected_at']
    date_hierarchy = 'detected_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
from django.contrib import admin
from .models import Competition, Participant

# This allows you to view and edit Competitions in the Admin Panel
@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'church_name', 'created_by', 'is_active')
    list_filter = ('is_active',)

# This allows you to view and edit Participants in the Admin Panel
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'access_code', 'competition', 'status')
    list_filter = ('competition', 'status')
    readonly_fields = ('access_code',) # Prevents manual editing of the auto-generated code
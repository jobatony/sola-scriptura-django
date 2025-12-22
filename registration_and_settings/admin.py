from django.contrib import admin
from .models import User, UserSettings, Competition, Participant
from django.contrib.auth.admin import UserAdmin

# Register the custom User model using the built-in UserAdmin
# This ensures passwords are hashed correctly and you get the standard user management interface
admin.site.register(User, UserAdmin)

# Register the UserSettings model
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'notifications_enabled')
    search_fields = ('user__username', 'user__email')
    list_filter = ('theme', 'notifications_enabled')

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
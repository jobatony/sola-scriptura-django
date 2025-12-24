from django.contrib import admin
from .models import BibleQuestion, CompetitorState, GameTracker, ParticipantResponse

admin.site.register(BibleQuestion)
admin.site.register(CompetitorState)  # Register Competition model for admin panel
admin.site.register(GameTracker)
admin.site.register(ParticipantResponse)
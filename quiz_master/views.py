import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from registration_and_settings.models import Participant, Competition
from .models import GameTracker, BibleQuestion
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@api_view(['POST'])
@permission_classes([AllowAny]) # Important: Users are not logged in yet
def join_competition(request):
    access_code = request.data.get('access_code')
    
    if not access_code:
        return Response({'error': 'Code is required'}, status=400)

    try:
        # Find the participant
        participant = Participant.objects.select_related('competition').get(access_code=access_code)
        
        # Check if competition is active (Optional but recommended)
        # if not participant.competition.is_active:
        #     return Response({'error': 'Competition is not active yet'}, status=403)

        return Response({
            'success': True,
            'competition_id': participant.competition.id,
            'participant_id': participant.id,
            'participant_name': participant.full_name,
            'competition_name': participant.competition.name
        })
    except Participant.DoesNotExist:
        return Response({'error': 'Invalid Access Code'}, status=404)
    
@api_view(['POST'])
def generate_questions(request):
    competition_id = request.data.get('competition_id')
    competition = get_object_or_404(Competition, id=competition_id)

    # 1. Calculate Round Number
    # Check if there are previous rounds for this competition
    previous_rounds = GameTracker.objects.filter(competition=competition)
    if previous_rounds.exists():
        # Get the highest round number and add 1
        last_round = previous_rounds.order_by('-round_number').first()
        new_round_number = last_round.round_number + 1
    else:
        new_round_number = 1

    # 2. Pick 6 Random Questions
    # Note: efficient for small datasets. For huge DBs, use other methods.
    questions_query = BibleQuestion.objects.order_by('?')[:6]
    
    if len(questions_query) < 6:
        return Response({'error': 'Not enough questions in the database'}, status=400)

    # Serialize questions to send to frontend (ID, Text, Options, etc.)
    # We send the FULL data so the frontend doesn't need to fetch again
    questions_data = []
    question_ids = []
    
    for q in questions_query:
        question_ids.append(q.id)
        questions_data.append({
            'id': q.id,
            'text': q.verse_text,
            'options': [q.wrong_option_1, q.wrong_option_2, q.wrong_option_3, q.correct_book],
            'correct_option': q.correct_book, # Only needed for Mod/Corrections
            'chapter': q.chapter,
            'verse': q.verse
        })

    # 3. Save to GameTracker
    GameTracker.objects.create(
        competition=competition,
        round_number=new_round_number,
        generated_questions=question_ids
    )

    # 4. Broadcast via WebSocket (The "Disperse" Step)
    channel_layer = get_channel_layer()
    room_group_name = f'competition_{competition_id}'

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'game_message', # Handled by Consumer
            'message': 'game_questions_update',
            'payload': {
                'round': new_round_number,
                'questions': questions_data
            }
        }
    )

    return Response({'success': True, 'round': new_round_number})
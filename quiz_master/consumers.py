import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import BibleQuestion
from registration_and_settings.models import Competition, Participant

class CompetitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.competition_id = self.scope['url_route']['kwargs']['competition_id']
        self.room_group_name = f'competition_{self.competition_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'participant_join':
            # 1. Look for 'access_code' in the payload
            access_code = data.get('access_code')
            
            # 2. Check if this is a moderator (bypass verification) or a participant
            if data.get('is_moderator'):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'broadcast_participant',
                        'name': "Moderator"
                    }
                )
            elif access_code:
                # 3. Verify the code against the database
                participant = await self.verify_participant(access_code)
                
                if participant:
                    # --- CHANGE START ---
                    # Send direct confirmation to the user who joined
                    await self.send(text_data=json.dumps({
                        'type': 'join_success',
                        'participant': {
                            'name': participant.full_name,
                            'id': participant.id
                        }
                    }))
                    # --- CHANGE END ---

                    # Success: Broadcast the real name from the DB
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'broadcast_participant',
                            'name': participant.full_name
                        }
                    )
                else:
                    # Failure: Send error message back to this specific socket
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Invalid access code or participant not found.'
                    }))
            else:
                # Fallback or Error if no code provided
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Access code required.'
                }))

        elif action == 'generate_questions':
            # Fetch random questions and send to everyone
            questions = await self.get_random_questions(6)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_questions',
                    'questions': questions
                }
            )

        elif action == 'start_round':
            # Trigger the start for everyone
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game_round',
                }
            )

    # Handlers for group messages
    async def broadcast_participant(self, event):
        await self.send(text_data=json.dumps({
            'type': 'participant_update',
            'name': event['name']
        }))

    async def send_questions(self, event):
        await self.send(text_data=json.dumps({
            'type': 'questions_ready',
            'payload': event['questions']
        }))

    async def start_game_round(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_round'
        }))

    @database_sync_to_async
    def verify_participant(self, access_code):
        """
        Verifies that the access code belongs to a participant 
        registered for the current competition.
        """
        try:
            return Participant.objects.get(
                access_code=access_code, 
                competition_id=self.competition_id
            )
        except Participant.DoesNotExist:
            return None

    @database_sync_to_async
    def get_random_questions(self, count):
        # Logic to pick random BibleQuestions
        # In a real scenario, you might want to filter by difficulty or tags
        items = list(BibleQuestion.objects.all())
        if len(items) < count:
            selected = items # Or duplicate if not enough
        else:
            selected = random.sample(items, count)
        
        # Serialize for frontend
        return [
            {
                'id': q.id,
                'verse_text': q.verse_text,
                'options': self.shuffle_options(q)
            }
            for q in selected
        ]

    def shuffle_options(self, question):
        opts = [
            {'text': question.correct_book, 'is_correct': True},
            {'text': question.wrong_option_1, 'is_correct': False},
            {'text': question.wrong_option_2, 'is_correct': False},
            {'text': question.wrong_option_3, 'is_correct': False},
        ]
        random.shuffle(opts)
        return opts
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from .models import CompetitorState
from registration_and_settings.models import Competition

class CompetitionConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def register_participant_entry(self, competition_id, code):
        """
        Creates a CompetitorState record if it doesn't exist.
        Returns the state object or None if competition is missing.
        """
        try:
            competition = Competition.objects.get(id=competition_id)
        except Competition.DoesNotExist:
            return None

        obj, created = CompetitorState.objects.get_or_create(
            competition=competition,
            participant_access_code=code,
            defaults={'state': 'qualified'}
        )
        return obj

    @database_sync_to_async
    def get_active_participants(self, competition_id):
        """ Fetch a list of access_codes for all QUALIFIED participants """
        return list(CompetitorState.objects.filter(
            competition_id=competition_id, 
            state='qualified'
        ).values_list('participant_access_code', flat=True))

    async def connect(self):
        # 1. Get Competition ID and Setup Room Name
        self.competition_id = self.scope['url_route']['kwargs']['competition_id']
        self.room_group_name = f'competition_{self.competition_id}'
        self.role = None
        self.identity = None

        # 2. Parse Query Parameters
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)

        # --- LOGIC A: IS IT A MODERATOR? ---
        if 'token' in params:
            # Note: In a production app, verify the token here.
            self.role = 'moderator'
            self.identity = 'Admin'
            
            # Add to group and accept immediately
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            
            print(f"✅ Moderator joined Room {self.competition_id}")

            # Send the "Who is already here?" list to the Moderator only
            existing_codes = await self.get_active_participants(self.competition_id)
            await self.send(text_data=json.dumps({
                'type': 'initial_state',
                'active_players': existing_codes 
            }))
            return

        # --- LOGIC B: IS IT A PARTICIPANT? ---
        elif 'code' in params:
            code = params['code'][0]
            self.role = 'participant'
            self.identity = code

            # Verify Database State
            competitor_state = await self.register_participant_entry(self.competition_id, code)

            # Case 1: Competition doesn't exist
            if not competitor_state:
                print(f"❌ Connection rejected: Competition {self.competition_id} not found")
                await self.close()
                return

            # Case 2: Player is Disqualified
            if competitor_state.state == 'disqualified':
                print(f"🚫 Connection Rejected: Participant {code} is DISQUALIFIED.")
                # Accept momentarily to send the error message, then close
                await self.accept()
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You have been disqualified from this competition.'
                }))
                await self.close()
                return

            # Case 3: Valid Player - Proceed to Join
            print(f"✅ Participant {code} joined Room {self.competition_id}")
            
            # Add to group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            # Broadcast 'player_joined' to the group (so Moderator sees it)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': 'player_joined',
                    'payload': {'code': self.identity}
                }
            )

        # --- LOGIC C: NO CREDENTIALS ---
        else:
            print("❌ Connection rejected: No credentials provided")
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        
        print(f"📡 [Server Received] Role: {self.role}, Type: {data.get('type')}, Room: {self.room_group_name}")

        # LOGIC: Moderator Commands
        if self.role == 'moderator':
            msg_type = data.get('type')
            
            # 1. Translate "Trigger" to actual "Action"
            if msg_type == 'start_round':
                # Broadcast to everyone (including Mod) that round has started
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message',
                        'message': 'start_round_trigger',  # <--- matches UserLobby listener
                        'payload': {}
                    }
                )
            else:
                # Pass through other messages
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message',
                        'message': msg_type,
                        'payload': data.get('payload')
                    }
                )
        
        # LOGIC: Participant Messages (e.g. submitting answers)
        elif self.role == 'participant':
            msg_type = data.get('type')
            
            if msg_type == 'player_ready':
                # Broadcast that this specific player (self.identity) is ready
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message', # This routes to game_message() handler
                        'message': 'player_ready_update', # The frontend listener type
                        'payload': {
                            'code': self.identity,   # The participant's access code
                            'status': data.get('status', True)
                        }
                    }
                )
            # --- NEW CODE END ---

    # Handler for 'game_message' type sent via group_send
    async def game_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['message'],
            'payload': event.get('payload')
        }))
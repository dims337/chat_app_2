import asyncio
import json

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Thread, ChatMessage

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        #print('connected', event)
        await self.send({
            "type": "websocket.accept"
        })

        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        thread_obj = await self.get_thread(me, other_user)
        chat_room = f"thread_{thread_obj.id}"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        #print (thread_obj)
        #print(other_user, me)



        #await self.accept()
        await self.send({
            "type": "websocket.send",
            "text": "hello world"
        })

    async def websocket_receive(self, event):
        print('receive', event)
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            user = self.scope['user']
            username = 'default'
            if user.is_authenticated:
                username = user.username
            response = {
                'message' : msg ,
                'user' : username
            }

            await self.create_chat_message(user, msg)
            
            #broadcast message to group
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type" : "chat_message",
                    "text" : json.dumps(response)
                }

            )

        #{'type' : 'websocket.receive', 'text': '{"message" : "xxx"}'} type coming from front_end
    async def chat_message(self, event):
       # print('text', event) for testing method in backend

       #send the message
       await self.send({
           "type" : "websocket.send",
           "text" : event['text']
       })

    async def websocket_disconnect(self, event):
        print('disconnected', event)

    @database_sync_to_async # decorator to grab the thread and not to overload the database/ too many requests    
    def get_thread (self, user, other_username):
        return Thread.objects.get_or_new(user,other_username)[0]  

    @database_sync_to_async    
    def create_chat_message (self, me,  msg):
        thread_obj= self.thread_obj
        return ChatMessage.objects.create(thread=thread_obj, user=me, message=msg)[0]  



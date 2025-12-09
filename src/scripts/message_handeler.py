from PIL import Image
from io import BytesIO

import numpy as np
import flet as ft

import base64
import socket
import os

class Message:
    def __init__(self, user_name: str, data, message_type: str, chat: str) -> None:
        self.user_name = user_name
        self.data = data
        self.message_type = message_type
        self.chat = chat
    
    def send_message(self) -> ft.Row:
        if self.message_type == "chat_message":
            message = TextMessage(self)
            
        elif self.message_type == "image_message":
            message = ImageMessage(self)
            
        return message
    
    
    def get_initials(self, user_name: str) -> str:
                return user_name[:1].capitalize() if user_name else socket.gethostbyname()


    def get_avatar_color(self, user_name: str) -> str:
        colors_lookup= [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


class TextMessage(ft.Row):
    def __init__(self, message: Message) -> None:
        super().__init__()
        
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(message.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=message.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold", selectable=True),
                    ft.Text(message.data, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]


class ImageMessage(ft.Row):
    def __init__(self, message: Message) -> None:
        super().__init__()
        
        image_path = os.path.normpath(f"{os.getcwd()}/src/{message.data}")
        pillow_photo = Image.open(image_path)
        arr = np.asarray(pillow_photo)

        pillow_img = Image.fromarray(arr)
        buff = BytesIO()
        pillow_img.save(buff, format=pillow_photo.format)
        
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(message.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=message.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold", selectable=True),
                    ft.Image(src_base64=base64.b64encode(buff.getvalue()).decode('utf-8'),
                            width=pillow_photo.width if pillow_photo.width < 600 else 600),
                ],
                tight=True,
                spacing=5,
            ),
        ]
from PIL import Image
from io import BytesIO

import flet as ft
import numpy as np

import sqlite3
import base64
import socket
import os

host_ip = socket.gethostbyname(socket.gethostname())

os.environ["FLET_SECRET_KEY"] = os.urandom(12).hex()
os.environ["FLET_SERVER_PORT"] = "9892"

class Database:
    def __init__(self) -> None:
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        
        self.cursor.execute("""
            DROP TABLE IF EXISTS USERS
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            USER_NAME TEXT NOT NULL PRIMARY KEY,
            IP_ADDRESS TEXT NOT NULL UNIQUE,
            BANNED BOOL NOT NULL DEFAULT 0
        )""")
        
    def add_user(self, user_name: str, ip_address: str) -> None:
        self.cursor.execute(f"""INSERT INTO USERS (USER_NAME, IP_ADDRESS, BANNED) VALUES (
            '{user_name}',
            '{ip_address}',
            0
        )""")
        
        self.connection.commit()
    
    def remove_user(self, user_name: str) -> None:
        self.cursor.execute(f"""DELETE FROM USERS WHERE USER_NAME = '{user_name}'""")
        self.connection.commit()
    
    def get_users(self) -> list[str]:
        result = self.cursor.execute(f"""SELECT USER_NAME, IP_ADDRESS, BANNED FROM USERS""")
        return result.fetchall()
    
    def add_banned_user(self, user_name: str) -> None:
        self.cursor.execute(f"""UPDATE USERS SET BANNED = 1 WHERE USER_NAME = '{user_name}'""")
        self.connection.commit()
    
    def remove_banned_user(self, user_name: str) -> None:
        self.cursor.execute(f"""UPDATE USERS SET BANNED = 0 WHERE USER_NAME = '{user_name}'""")
        self.connection.commit()
    
    def get_banned_users(self) -> list[str]:
        result = self.cursor.execute(f"""SELECT USER_NAME, IP_ADDRESS, BANNED FROM USERS WHERE BANNED = 1""")
        return result.fetchall()


class Message:
    def __init__(self, user_name: str, data, message_type: str) -> None:
        self.user_name = user_name
        self.data = data
        self.message_type = message_type
    
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
        
        image_path = os.path.normpath(f"{os.getcwd()}/src/assets/{message.data}")
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


def main(page: ft.Page) -> None:
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Teeny Chat"
    
    DataBase = Database()
    
    def on_exit(event) -> None:        
        page.pubsub.send_all(
            Message(
                user_name=f"{page.session.get('user_name')}",
                data=f"{page.session.get('user_name')} has left the chat.",
                message_type="login_message"
            )
        )

    page.on_disconnect = on_exit
    
    
    def on_join(event) -> None:
        if page.client_ip in DataBase.get_banned_users():
            new_message.disabled = True
            send_message.disabled = True
        
        page.update()
    
    
    page.on_connect = on_join

    
    def verify_admin() -> bool:
        return page.session.get("user_name") == "Teeny" and (page.client_ip == host_ip or page.client_ip == "127.0.0.1")
    

    def join_chat_click(event) -> None:
        if join_user_name.value == "":
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
            return
        
        if " " in join_user_name.value:
            join_user_name.error_text = "Name cannot contain spaces!"
            join_user_name.update()
            return
        
        if join_user_name.value == "Teeny" and page.client_ip != host_ip and page.client_ip != "127.0.0.1":
            join_user_name.error_text = "This name is reserved!"
            join_user_name.update()
            return
        
        if join_user_name.value in DataBase.get_users():
            join_user_name.error_text = "This name is already taken!"
            join_user_name.update()
            return
        
        
        DataBase.add_user(join_user_name.value, page.client_ip)
        page.session.set("user_name", join_user_name.value)
        
        welcome_dlg.open = False
        new_message.prefix = ft.Text(f"{join_user_name.value}: ")
        
        if page.client_ip in DataBase.get_users():
            new_message.disabled = True
            send_message.disabled = True
            new_message.hint_text = "You have been banned from the chat"
        
        page.pubsub.send_all(
            Message(
                user_name=f"{join_user_name.value}",
                data=f"The ghost {join_user_name.value} has joined the chat."
                    if page.client_ip in DataBase.get_banned_users()
                    else f"{join_user_name.value} has joined the chat.",
                message_type="login_message",
            )
        )
        page.update()


    def send_message_click(event) -> None:
        if new_message.value != "":
            page.pubsub.send_all(
                Message(
                    user_name=page.session.get("user_name"),
                    data=new_message.value,
                    message_type="command" if "/" == new_message.value[0] and verify_admin() else "chat_message"
                )
            )
            new_message.value = ""
            new_message.focus()
            page.update()


    def send_image_click(event) -> None:      
        if event.progress == 1.0:
            page.pubsub.send_all(
                Message(
                    user_name=page.session.get("user_name"),
                    data=f"upload/images/{event.file_name}",
                    message_type="image_message"
                )
            )
            new_message.focus()
            page.update()


    async def on_message(message: Message) -> None:
        if message.message_type == "login_message":
            m = ft.Text(message.data, italic=True, color=ft.Colors.BLUE_400, size=12)
            
        elif message.message_type == "command":
            command_args: list[str] = message.data.split()
            match command_args[0]:
                case "/say":
                    m = ft.Text("God says: "+" ".join(command_args[1::1]) , size=24)
                
                case "/clear":
                    chat.controls.clear()
                    m = ft.Text("Chat cleared by god", italic=True, color=ft.Colors.RED, size=12)
                
                case "/clear-img":
                    for file in os.scandir("src/assets/upload/images"):
                        os.remove(f"src/assets/upload/images/{file.name}")
                    
                    if message.user_name == page.session.get("user_name"):
                        m = ft.Text("Images cleared by god", italic=True, color=ft.Colors.RED, size=12)
                    
                case "/ban":
                    if page.session.get("user_name") == command_args[1]:
                        new_message.disabled = True
                        send_message.disabled = True
                        new_message.hint_text = "You have been banned from the chat"
                        
                        DataBase.add_banned_user(command_args[1])
                        
                    m = ft.Text(f"User {command_args[1]} has been banned", italic=True, color=ft.Colors.RED, size=12)
                
                case "/unban":
                    if page.session.get("user_name") == command_args[1]:
                        new_message.disabled = False
                        send_message.disabled = False
                        new_message.hint_text = "Write a message..."
                        
                        DataBase.remove_banned_user(command_args[1]) if command_args[1] in DataBase.get_banned_users() else None
                        
                    m = ft.Text(f"User {command_args[1]} has been unbanned", italic=True, color=ft.Colors.BLUE_400, size=12)
                
                case "/kick":
                    if page.session.get("user_name") == command_args[1]:
                        import random
                        kick_urls = ["https://classicgamezone.com/es/games/pokemon-girls-hunter-3"]
                        page.launch_url(random.choice(kick_urls), web_popup_window=False)
                        page.update()
                        page.window.destroy()
                        
                    m = ft.Text(f"User {command_args[1]} has been kicked", italic=True, color=ft.Colors.RED, size=12)

                case "/users":
                    if page.session.get("user_name") == message.user_name:
                        users = " ".join(DataBase.get_users())
                        m = ft.Text(f"Current users: {users}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                    
                case _:
                    m = ft.Text(f"Unknown command: {message.data}", italic=True, color=ft.Colors.RED, size=12)
        else:
            m = message.send_message()
        
        
        chat.controls.append(m)

        page.update()

    page.pubsub.subscribe(on_message)

    # A dialog asking for a user display name
    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
        max_length=32
    )
    welcome_dlg = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.overlay.append(welcome_dlg)

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )
    
    
    def pick_image(event) -> None:
        image_file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "gif"]
        )
        
    def upload_image(event) -> None:
        upload_file = ft.FilePickerUploadFile(
            name = image_file_picker.result.files[0].name,
            upload_url = page.get_upload_url(f"images/{image_file_picker.result.files[0].name}", 60)
        )
        
        image_file_picker.upload([upload_file])
    
    image_file_picker = ft.FilePicker(on_result=upload_image, on_upload=send_image_click)
    
    
    send_image = ft.IconButton(
        icon=ft.Icons.IMAGE_ROUNDED,
        tooltip="Send image",
        on_click=pick_image
    )
    
    send_message = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        tooltip="Send message",
        on_click=send_message_click
    )
    
    
    page.overlay.append(image_file_picker)
    
    # Add everything to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                send_image,
                send_message
            ]
        ),
    )


ft.app(target=main, assets_dir="assets", upload_dir="assets/upload")
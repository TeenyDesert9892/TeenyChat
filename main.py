import flet as ft
import socket
import os

host_ip = socket.gethostbyname(socket.gethostname())

os.environ["FLET_SECRET_KEY"] = os.urandom(12).hex()
os.environ["FLET_SERVER_PORT"] = "9892"

class UsersList:
    def __init__(self) -> None:
        self._users_list = []
        self._banned_users = []
        
    def add_user(self, user_name: str) -> None:
        self._users_list.append(user_name)
    
    def remove_user(self, user_name: str) -> None:
        self._users_list.remove(user_name)
    
    def get_users(self) -> list[str]:
        return self._users_list
    
    def add_banned_user(self, user_name: str) -> None:
        self._banned_users.append(user_name)
    
    def remove_banned_user(self, user_name: str) -> None:
        self._banned_users.remove(user_name)
    
    def get_banned_users(self) -> list[str]:
        return self._banned_users


class IP_List:
    def __init__(self) -> None:
        self._ips = []
        self._banned_ips = []
        
    def add_ip(self, ip_address: str) -> None:
        self._ips.append(ip_address)
    
    def remove_ip(self, ip_address:str) -> None:
        self._ips.remove(ip_address)
        
    def get_ips(self) -> list[str]:
        return self._ips

    def add_banned_ip(self, ip_address: str) -> None:
        self._banned_ips.append(ip_address)
    
    def remove_banned_ip(self, ip_address: str) -> None:
        self._banned_ips.remove(ip_address)
        
    def get_banned_ips(self) -> list[str]:
        return self._banned_ips


user_list = UsersList()
ip_list = IP_List()


class Message:
    def __init__(self, user_name: str, data, message_type: str) -> None:
        self.user_name = user_name
        self.data = data
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message) -> None:
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
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


class ImageMessage(ft.Row):
    def __init__(self, message: Message) -> None:
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold", selectable=True),
                    ft.Image(src=os.path.normpath(f"{os.getcwd()}/assets/{message.data}"), width=200),
                ],
                tight=True,
                spacing=5,
            ),
        ]
    
    
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


def main(page: ft.Page) -> None:
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Teeny Chat"
    
    
    def on_exit(event) -> None:
        user_list.remove_user(page.session.get("user_name"))
        ip_list.remove_ip(page.client_ip)
        
        page.pubsub.send_all(
            Message(
                user_name=f"{page.session.get('user_name')}",
                data=f"{page.session.get('user_name')} has left the chat.",
                message_type="login_message"
            )
        )

    page.on_disconnect = on_exit
    
    
    def on_join(event) -> None:
        if page.client_ip in ip_list.get_banned_ips():
            new_message.disabled = True
            send_message.disabled = True
        
        page.session.remove("user_name")
        
        ip_list.add_ip(page.client_ip)
        welcome_dlg.open = True
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
        
        if join_user_name.value in user_list.get_users():
            join_user_name.error_text = "This name is already taken!"
            join_user_name.update()
            return
        
        
        user_list.add_user(join_user_name.value)
        page.session.set("user_name", join_user_name.value)
        
        ip_list.add_ip(page.client_ip)
        
        welcome_dlg.open = False
        new_message.prefix = ft.Text(f"{join_user_name.value}: ")
        
        if page.client_ip in ip_list.get_banned_ips():
            new_message.disabled = True
            send_message.disabled = True
            new_message.hint_text = "You have been banned from the chat"
        
        page.pubsub.send_all(
            Message(
                user_name=f"{join_user_name.value}",
                data=f"The ghost {join_user_name.value} has joined the chat."
                    if page.client_ip in ip_list.get_banned_ips()
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
                    data=f"assets/upload/images/{event.file_name}",
                    message_type="image_message"
                )
            )
            new_message.focus()
            page.update()

    def on_message(message: Message) -> None:
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        
        elif message.message_type == "image_message":
            m = ImageMessage(message)
            
        elif message.message_type == "login_message":
            m = ft.Text(message.data, italic=True, color=ft.Colors.BLUE_400, size=12)
            
        elif message.message_type == "command":
            command_args: list[str] = message.data.split()
            match command_args[0]:
                case "/say":
                    m = ft.Text("God says: "+" ".join(command_args[1::1]) , size=24)
                
                case "/clear":
                    chat.controls.clear()
                    m = ft.Text("Chat cleared by god", italic=True, color=ft.Colors.RED, size=12)
                    
                case "/ban":
                    if page.session.get("user_name") == command_args[1]:
                        new_message.disabled = True
                        send_message.disabled = True
                        new_message.hint_text = "You have been banned from the chat"
                        
                        user_list.add_banned_user(command_args[1])
                        ip_list.add_banned_ip(page.client_ip)
                        
                    m = ft.Text(f"User {command_args[1]} has been banned", italic=True, color=ft.Colors.RED, size=12)
                
                case "/unban":
                    if page.session.get("user_name") == command_args[1]:
                        new_message.disabled = False
                        send_message.disabled = False
                        new_message.hint_text = "Write a message..."
                        
                        user_list.remove_banned_user(command_args[1]) if command_args[1] in user_list.get_banned_users() else None
                        ip_list.remove_banned_ip(page.client_ip) if page.client_ip in ip_list.get_banned_ips() else None
                        
                    m = ft.Text(f"User {command_args[1]} has been banned", italic=True, color=ft.Colors.BLUE_400, size=12)
                
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
                        users = " ".join(user_list.get_users())
                        m = ft.Text(f"Current users: {users}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                    
                case "/ips":
                    if page.session.get("user_name") == message.user_name:
                        ips = " ".join(ip_list.get_ips())
                        m = ft.Text(f"IPs: {ips}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                
                case "/baned_ips":
                    if page.session.get("user_name") == message.user_name:
                        ips = " ".join(ip_list.get_banned_ips())
                        m = ft.Text(f"IPs: {ips}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                    
                case _:
                    m = ft.Text(f"Unknown command: {message.data}", italic=True, color=ft.Colors.RED, size=12)
                    
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
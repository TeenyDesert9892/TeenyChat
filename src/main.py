from scripts.database_handeler import Database
from scripts.message_handeler import Message

import flet as ft

import sqlite3
import socket
import os

host_ip = socket.gethostbyname(socket.gethostname())

os.environ["FLET_SECRET_KEY"] = os.urandom(12).hex()
os.environ["FLET_SERVER_PORT"] = "9892"

os.environ["FLET_ASSETS_DIR"] = os.path.normpath(f"{os.getcwd()}/src/assets")
os.environ["FLET_UPLOAD_DIR"] = os.path.normpath(f"{os.getcwd()}/src/upload")

DataBase = Database(host_ip)

def main(page: ft.Page) -> None:
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Teeny Chat"
    
    def on_exit(event) -> None:
        DataBase.remove_user(page.session.get("user_name"))
        
        if page.session.get("user_name"):
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
            image_file_picker.disabled = True
            send_message.disabled = True
            
        if page.session.get("user_name"):
            DataBase.add_user(page.session.get("user_name"), page.client_ip)
            
            page.pubsub.send_all(
                Message(
                    user_name=f"{page.session.get('user_name')}",
                    data=f"{page.session.get('user_name')} has joined the chat.",
                    message_type="login_message"
                )
            )
        
        page.update()
    
    page.on_connect = on_join

    
    def verify_admin(user_name) -> bool:
        return True if user_name in [name for name, ip, admin, baned in DataBase.get_admin_users()] else False
    

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
        
        try: DataBase.add_user(join_user_name.value, page.client_ip)
        except sqlite3.IntegrityError:
            join_user_name.error_text = "This name or IP is already in use!"
            join_user_name.update()
            return
        
        page.session.set("user_name", join_user_name.value)
        
        welcome_dlg.open = False
        new_message.prefix = ft.Text(f"{join_user_name.value}: ")
        
        banned = page.client_ip in DataBase.get_banned_users()
        if banned:
            new_message.disabled = True
            send_message.disabled = True
            new_message.hint_text = "You have been banned from the chat"
        
        page.pubsub.send_all(
            Message(
                user_name=f"{join_user_name.value}",
                data=f"The ghost {join_user_name.value} has joined the chat." if banned
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
                    message_type="command" if "/" == new_message.value[0] and verify_admin(page.session.get("user_name")) else "chat_message"
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


    def on_message(message: Message) -> None:
        m = None
        
        if message.message_type == "login_message":
            m = ft.Text(message.data, italic=True, color=ft.Colors.BLUE_400, size=12)
            
        elif message.message_type == "command":
            command_args = message.data.split()
            match command_args[0]:
                case "/say":
                    m = ft.Text("God says: "+" ".join(command_args[1::1]) , size=24)
                
                case "/clear":
                    chat.controls.clear()
                    m = ft.Text("Chat cleared by god", italic=True, color=ft.Colors.RED, size=12)
                
                case "/clear-img":
                    for file in os.scandir("src/upload/images"):
                        os.remove(f"src/upload/images/{file.name}")
                    
                    if message.user_name == page.session.get("user_name"):
                        m = ft.Text("Images cleared by god", italic=True, color=ft.Colors.RED, size=12)
                        
                case "/users":
                    if page.session.get("user_name") == message.user_name:
                        users = [f"{user}, {ip}, {banned}" for user, ip, banned in DataBase.get_users()]
                        users_format = "\n"+"\n".join(users)
                        
                        m = ft.Text(f"Current users: {users_format}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                
                case "/kick":
                    if page.session.get("user_name") == command_args[1]:                
                        page.session.clear()
                        DataBase.remove_user(command_args[1])
                        
                        welcome_dlg.open = True
                        
                        page.update()
                        page.window.destroy()
                        
                    m = ft.Text(f"User {command_args[1]} has been kicked", italic=True, color=ft.Colors.RED, size=12)
                    
                case "/ban":
                    if command_args[1] in DataBase.get_name_by_ip(page.client_ip):
                        new_message.disabled = True
                        send_image.disabled = True
                        send_message.disabled = True
                        new_message.hint_text = "You have been banned from the chat"
                        
                        DataBase.add_banned_user(page.client_ip)
                        
                    m = ft.Text(f"User {command_args[1]} has been banned", italic=True, color=ft.Colors.RED, size=12)
                
                case "/unban":
                    if command_args[1] in DataBase.get_name_by_ip(page.client_ip):
                        new_message.disabled = False
                        send_image.disabled = False
                        send_message.disabled = False
                        new_message.hint_text = "Write a message..."
                        
                        DataBase.remove_banned_user(page.client_ip)
                        
                    m = ft.Text(f"User {command_args[1]} has been unbanned", italic=True, color=ft.Colors.BLUE_400, size=12)
                
                    
                case "/banned-users":
                    if page.session.get("user_name") == message.user_name:
                        users = [f"{user}, {ip}, {banned}" for user, ip, banned in DataBase.get_users() if banned == 1]
                        users_format = "\n"+"\n".join(users)
                        
                        m = ft.Text(f"Current banned users: {users_format}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                
                case "/is-banned":
                    if page.session.get("user_name") == message.user_name:
                        is_banned = "Yes" if bool([banned for user, ip, banned in DataBase.get_users() if user == command_args[1]][0]) else "No"
                        
                        m = ft.Text(f"Is user {command_args[1]} banned? {is_banned}", italic=True, color=ft.Colors.AMBER, size=12)
                
                case "/admin":
                    if command_args[1] == page.session.get("user_name"):
                        DataBase.add_admin_user(command_args[1])
                    
                    if verify_admin(page.session.get("user_name")):
                        m = ft.Text(f"User {command_args[1]} is now admin", italic=True, color=ft.Colors.AMBER, size=12)
                
                case "/unadmin":
                    if command_args[1] == page.session.get("user_name"):
                        DataBase.remove_admin_user(command_args[1])
                    
                    if verify_admin(page.session.get("user_name")):
                        m = ft.Text(f"User {command_args[1]} is not admin now", italic=True, color=ft.Colors.RED, size=12)
                    
                case "/admin-users":
                    if command_args[1] == page.session.get("user_name"):
                        users = [f"{user}, {ip}, {admin}, {banned}" for user, ip, admin, banned in DataBase.get_users() if admin == 1]
                        users_format = "\n"+"\n".join(users)
                        
                        m = ft.Text(f"Current banned users: {users_format}", italic=True, color=ft.Colors.AMBER, size=12, selectable=True)
                
                case "/is-admin":
                    if page.session.get("user_name") == message.user_name:
                        is_banned = "Yes" if bool([admin for user, ip, admin, banned in DataBase.get_users() if user == command_args[1]][0]) else "No"
                        
                        m = ft.Text(f"Is user {command_args[1]} admin? {is_banned}", italic=True, color=ft.Colors.AMBER, size=12)
                
                case _:
                    m = ft.Text(f"Unknown command: {message.data}", italic=True, color=ft.Colors.RED, size=12)
        else:
            m = message.send_message()
        
        if m != None:
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


if __name__ == "__main__":
    ft.app(target=main)
    DataBase.close_database()
from scripts.database_handeler import Database
from scripts.message_handeler import Message
from scripts.chat_handeler import ChatList

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
    page.title = "Teeny Chat"
    
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE_ACCENT)
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    def on_exit(event) -> None:
        DataBase.remove_user(page.session.get("user_name"))
        
        if page.session.get("user_name"):
            page.pubsub.send_all(
                Message(
                    user_name=f"{page.session.get('user_name')}",
                    data=f"{page.session.get('user_name')} has left the chat.",
                    message_type="login_message",
                    chat="General"
                )
            )

    page.on_disconnect = on_exit
    
    
    def on_join(event) -> None:
        if page.client_ip in DataBase.get_banned_users():
            new_message.disabled = True
            image_file_picker.disabled = True
            send_message.disabled = True
        
        page.session.set("current_chat", "General")
            
        if page.session.get("user_name"):
            DataBase.add_user(page.session.get("user_name"), page.client_ip)
            
            page.pubsub.send_all(
                Message(
                    user_name=f"{page.session.get('user_name')}",
                    data=f"{page.session.get('user_name')} has joined the chat.",
                    message_type="login_message",
                    chat="General"
                )
            )
        
        page.update()
    
    page.on_connect = on_join


    def chat_stop(event) -> None:
        DataBase.close_database()
        
    page.on_close = chat_stop
    

    def verify_admin(user_name: str) -> bool:
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
        
        try: DataBase.add_user(join_user_name.value, page.client_ip)
        except sqlite3.IntegrityError:
            join_user_name.error_text = "This name or IP is already in use!"
            join_user_name.update()
            return
        
        page.session.set("user_name", join_user_name.value)
        page.session.set("current_chat", "General")
        
        welcome_dlg.open = False
        new_message.prefix = ft.Text(f"{join_user_name.value}: ")
        
        banned = page.client_ip in DataBase.get_banned_users()
        if banned: bar_state(True)
        
        page.pubsub.send_all(
            Message(
                user_name=f"{join_user_name.value}",
                data=f"The ghost {join_user_name.value} has joined the chat." if banned
                    else f"{join_user_name.value} has joined the chat.",
                message_type="login_message",
                chat="General"
            )
        )
        page.update()


    def send_message_click(event) -> None:
        if new_message.value != "":
            page.pubsub.send_all(
                Message(
                    user_name=page.session.get("user_name"),
                    data=new_message.value,
                    message_type="command" if "/" == new_message.value[0] and verify_admin(page.session.get("user_name")) else "chat_message",
                    chat=page.session.get("current_chat")
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
                    message_type="image_message",
                    chat=page.session.get("current_chat")
                )
            )
            new_message.focus()
            page.update()

    def bar_state(unactive: bool) -> None:
        new_message.disabled = unactive
        send_image.disabled = unactive
        send_message.disabled = unactive
        new_message.hint_text = "You have been banned from the chat" if unactive else "Write a message..."

    def on_message(message: Message) -> None:
        m = None
        
        if message.message_type == "login_message":
            m = ft.Text(message.data, italic=True, color=ft.Colors.BLUE_400, size=12)
            
        elif message.message_type == "command":
            command_args = message.data.split()
            match command_args[0]:
                case "/say":
                    m = ft.Text("An admin says: "+" ".join(command_args[1::1]) , size=24)
                
                case "/clear":
                    chat_list.clear(message.chat)
                    m = ft.Text("Chat cleared by an admin", italic=True, color=ft.Colors.RED, size=12)
                
                case "/clear-img":
                    for file in os.scandir("src/upload/images"):
                        os.remove(f"src/upload/images/{file.name}")
                    
                    if message.user_name == page.session.get("user_name"):
                        m = ft.Text("Images cleared by an admin", italic=True, color=ft.Colors.RED, size=12)
                        
                case "/users":
                    if page.session.get("user_name") == message.user_name:
                        users = [f"User: {user}, IP: {ip}, Admin: {admin}, Banned: {banned}" for user, ip, admin, banned in DataBase.get_users()]
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
                        bar_state(True)
                        
                        DataBase.add_banned_user(page.client_ip)
                        
                    m = ft.Text(f"User {command_args[1]} has been banned", italic=True, color=ft.Colors.RED, size=12)
                
                case "/unban":
                    if command_args[1] in DataBase.get_name_by_ip(page.client_ip):
                        bar_state(False)
                        
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
            chat_list.send_message(message.chat, m)
        
        page.update()
    
    
    def on_chat_create(name: str) -> None:
        chat_list.create_chat(name)
        update_chat_list(True)
    
    
    def on_subscribe(message):
        if isinstance(message, Message):
            on_message(message)
        else:
            on_chat_create(message)
            
    
    page.pubsub.subscribe(on_subscribe)
    
    # A function to pick images
    def pick_image(event) -> None:
        image_file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "gif"]
        )
        
    # A function to upload the images on pick
    def upload_image(event) -> None:
        upload_file = ft.FilePickerUploadFile(
            name = image_file_picker.result.files[0].name,
            upload_url = page.get_upload_url(f"images/{image_file_picker.result.files[0].name}", 60)
        )
        
        image_file_picker.upload([upload_file])
    
    image_file_picker = ft.FilePicker(on_result=upload_image, on_upload=send_image_click)
    
    page.overlay.append(image_file_picker)
    
    # A dialog asking for a user display name
    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
        max_length=32
    )
    
    # A start page dialog
    welcome_dlg = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    page.overlay.append(welcome_dlg)
    
    # The list where all the chats are allocated
    chat_list = ChatList()
    
    def chat_box_change(event):
        chat_box.clean()
        chat_box.content = chat_list.get_chat_control(event.control.text)
        page.session.set("current_chat", event.control.text)
        page.update()
    
    def update_chat_list(event):
        new_chat_list = ft.ListView(expand=True)
        for name in chat_list.get_chats_list():
            new_chat_list.controls.append(ft.Button(name, on_click=chat_box_change))
        
        chat_list_container.content = new_chat_list
        
        if event:
            chat_list_container.clean()
            page.update()
    
    # A container for the chat list
    chat_list_container = ft.Container(
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True
    )
    
    update_chat_list(False)
    
    def add_chat_click(event):
            page.pubsub.send_all(chat_create_name.value)
            chat_create_dialog.open = False
            page.update()
    
    chat_create_name = ft.TextField(
        label="Enter the name of the chat",
        autofocus=True,
        on_submit=add_chat_click,
        max_length=32
    )
    
    def cancel_chat_create(event):
        chat_create_dialog.open = False
        page.update()
    
    chat_create_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Create chat"),
        content=ft.Column([chat_create_name], width=300, height=70),
        actions=[ft.ElevatedButton("Back", on_click=cancel_chat_create),
                 ft.ElevatedButton("Done", on_click=add_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    page.overlay.append(chat_create_dialog)
    
    def add_chat_dialog(event):
        chat_create_dialog.open = True
        page.update()
    
    add_chat_button = ft.IconButton(
        icon=ft.Icons.PLUS_ONE,
        on_click=add_chat_dialog
    )
    
    chat_list_control = ft.Row([
            add_chat_button
        ],
        width=page.width*0.2,
        height=50
    )
    
    # A row for the chat list
    chat_list_row = ft.Column([
            chat_list_control if page.client_ip == host_ip or page.client_ip == "127.0.0.1" else ft.Text("TeenyChat"),
            chat_list_container
        ],
        expand=True
    )
    
    # A card to show the chat list
    chat_list_card = ft.Card(
        chat_list_row,
        width=page.width*0.2,
        height=page.height*0.95
    )
    
    # Container of the current chat
    chat_box = ft.Container(
        content=chat_list.get_chat_control("General"),
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True
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
    
    # A new image message click and entry form
    send_image = ft.IconButton(
        icon=ft.Icons.IMAGE_ROUNDED,
        tooltip="Send image",
        on_click=pick_image
    )
    
    # A new message send form
    send_message = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        tooltip="Send message",
        on_click=send_message_click
    )
    
    # The row of the chat controls
    chat_entry_row = ft.Row([
            new_message,
            send_image,
            send_message
        ],
        width=page.width*0.75,
        height=50,
    )
    
    # The card where is the current chat and the controls
    chat_card = ft.Card(
        ft.Column([
            chat_box,
            chat_entry_row
            ],
            expand=True
        ),
        width=page.width*0.75,
        height=page.height*0.95,
        expand=True
    )
    
    # Add everything to the page
    page.add(
        ft.Row([
            chat_list_card,
            chat_card
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER)
    )
    
    # Resize elements on windows resize event
    def resize_elements(event):
        chat_list_card.width = event.width*0.2
        chat_list_card.height = event.height*0.95
        
        chat_entry_row.width = event.width*0.75,
        
        chat_card.width = event.width*0.75,
        chat_card.height = event.height*0.95
        
        page.update()
    
    page.on_resized = resize_elements
    
    page.update()


if __name__ == "__main__":
    ft.app(main)
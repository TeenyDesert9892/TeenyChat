import flet as ft

class Chat:
    def __init__(self) -> None:
        self.messages_list = ft.ListView(
            expand = True,
            spacing = 10,
            auto_scroll = True
        )
    
    def get_chat(self) -> ft.ListView:
        return self.messages_list
    
    def clean(self) -> None:
        self.messages_list.controls.clear()
    
    def new_message(self, message) -> None:
        self.messages_list.controls.append(message)


class ChatList:
    def __init__(self) -> None:
        self.chat_dict = {}
        self.chat_dict["General"] = Chat()
    
    def create_chat(self, name: str) -> None:
        self.chat_dict[name] = Chat()
    
    def remove_chat(self, name: str) -> None:
        self.chat_dict.pop(name)
        
    def send_message(self, chat: str, message) -> None:
        self.chat_dict[chat].new_message(message)
    
    def clear_chat(self, chat: str) -> None:
        self.chat_dict[chat].clean()
    
    def get_chat(self, name: str) -> Chat:
        return self.chat_dict[name]
    
    def get_chat_control(self, name: str) -> ft.ListView:
        return self.chat_dict[name].get_chat()
    
    def get_chats_list(self) -> list[str]:
        return [chat for chat in self.chat_dict.keys()] 
    
class Message:
    def __init__(self, user_name: str, data, message_type: str, chat: str) -> None:
        self.user_name = user_name
        self.data = data
        self.message_type = message_type
        self.chat = chat
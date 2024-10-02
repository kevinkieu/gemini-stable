from config import MAX_HISTORY

class ConversationManager:
    def __init__(self):
        self.conversations = {}

    def add_message(self, user_id, role, content):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        self.conversations[user_id].append({"role": role, "content": content})
        if len(self.conversations[user_id]) > MAX_HISTORY * 2:
            self.conversations[user_id] = self.conversations[user_id][-MAX_HISTORY * 2:]

    def get_history(self, user_id):
        return self.conversations.get(user_id, [])

    def clear_history(self, user_id):
        self.conversations[user_id] = []
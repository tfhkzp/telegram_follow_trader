from telethon import TelegramClient, events, utils
import telethon


class TelegramManager():
    client = None
    phone_number = None
    receive_new_message_handler = None

    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient(None, api_id, api_hash)

    def login(self, code_callback, password_callback):
        self.client.start(self.phone_number, code_callback=code_callback, password=password_callback, max_attempts=1)

    async def logout(self):
        try:
            await self.client.log_out()
            await self.client.disconnect()
        except:
            pass

    async def get_me(self):
        me = await self.client.get_me()
        return me

    async def get_telegram_dialogs(self):
        telegram_dialog_list = []
        async for dialog in self.client.iter_dialogs():
            if (type(dialog.entity) == telethon.tl.types.Channel and dialog.entity.broadcast is True) or \
                    (type(dialog.entity) == telethon.tl.types.User and dialog.entity.bot is True):
                telegram_dialog_list.append({'id': dialog.id, 'title': dialog.title})
        return telegram_dialog_list

    async def get_selected_dialog_recent_messages(self, selected_dialog_id, messages_count):
        message_list = []
        async for dialog in self.client.iter_dialogs():
            if dialog.id == selected_dialog_id:
                last_message_id = dialog.message.id
                min_id = last_message_id - messages_count if last_message_id - messages_count > 0 else 0
                async for message in self.client.iter_messages(dialog, min_id=min_id):
                    message_list.append(message)
        return message_list

    async def get_selected_dialog_messages_after_date(self, selected_dialog_id, local_start_date):
        message_list = []
        async for dialog in self.client.iter_dialogs():
            if dialog.id == selected_dialog_id:
                async for message in self.client.iter_messages(dialog, offset_date=local_start_date, reverse=True):
                    message_list.append(message)
        return message_list

    def start_monitor_dialog_messages(self, dialog_id, callback):
        async def receive_new_message_handler(event):
            try:
                sender = await event.get_sender()
                peer_id = utils.get_peer_id(sender)
                if peer_id == dialog_id:
                    await callback(event.text)
            except:
                pass

        self.receive_new_message_handler = receive_new_message_handler
        self.client.add_event_handler(receive_new_message_handler, events.NewMessage(pattern='(?i).*'))

    def stop_monitor_dialog_messages(self):
        self.client.remove_event_handler(self.receive_new_message_handler)

    async def run_until_disconnected(self, *args):
        await self.client.run_until_disconnected()

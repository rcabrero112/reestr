import discord
import requests
from discord.ext import commands

WEBHOOKS = {
    'Титан': {'id': 'id', 'token': 'token'},
    'Фобос': {'id': 'id', 'token': 'token'},
    'Фронтир': {'id': 'id', 'token': 'token'},
    'Деймос': {'id': 'id', 'token': 'token'},
    'Союз': {'id': 'id', 'token': 'token'},
}

GOOGLE_FORM_URL = 'formResponseURL'


class WebhookHandlerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Функция для редактирования сообщения через вебхук
    def edit_webhook_message(self, webhook_id, webhook_token, message_id, current_content):
        if "Пользователь занесен в реестр" not in current_content:
            new_content = current_content + "\nПользователь занесен в реестр"
            url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}"
            json_data = {
                "content": new_content
            }
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.patch(url, json=json_data, headers=headers)
            if response.status_code == 200:
                print(f"Сообщение {message_id} успешно отредактировано.")
            else:
                print(f"Ошибка при редактировании сообщения {message_id}: {response.status_code}, {response.text}")

    # Функция для определения вебхука по ключевому слову
    def get_webhook_for_message(self, title):
        for keyword, webhook in WEBHOOKS.items():
            if keyword.lower() in title.lower():
                return webhook['id'], webhook['token']
        return None, None

    # Функция для отправки данных в Google форму
    def send_to_google_form(self, login, reason, punishment_link):
        form_data = {
            'entry.id': 'DeadSpace',  # Проект - Заменить на DeadSpace
            'entry.id': login,  # Логин набегатора
            'entry.id': reason,  # Причина бана
            'entry.id': punishment_link  # Ссылка на выданное наказание
        }
        response = requests.post(GOOGLE_FORM_URL, data=form_data)
        if response.status_code == 200:
            print(f"Данные успешно отправлены для {punishment_link}.")
            return True
        else:
            print(f"Ошибка при отправке данных для {punishment_link}. Код: {response.status_code}")
            return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Проверяем, что сообщение пришло из нужного канала
        if message.webhook_id:
            webhook_name = message.author.name
            webhook_id, webhook_token = self.get_webhook_for_message(webhook_name)

            if webhook_id and webhook_token:
                if "Пользователь занесен в реестр" in message.content:
                    print(f"Сообщение {message.id} уже содержит 'Пользователь занесен в реестр'. Пропускаем.")
                    return

                # Извлечение эмбеда
                for embed in message.embeds:
                    embed_dict = embed.to_dict()
                    description = embed_dict.get('description', '')

                    if "Бан в реестр" in description:
                        try:
                            # Извлечение логина и причины
                            login_line = next(line for line in description.splitlines() if "Нарушитель:" in line)
                            login = login_line.split(":")[1].strip()

                            reason_line = next(line for line in description.splitlines() if "Причина:" in line)
                            reason = reason_line.split(":")[1].strip()

                            # Отправляем данные в Google форму
                            punishment_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                            if self.send_to_google_form(login, reason, punishment_link):
                                # Если данные успешно отправлены, только тогда редактируем сообщение
                                self.edit_webhook_message(webhook_id, webhook_token, message.id, message.content)
                            else:
                                print(f"Не удалось отправить данные для сообщения {message.id}")
                        except StopIteration:
                            print(f"Не удалось извлечь логин или причину из сообщения {message.id}")
from telethon import TelegramClient, errors
import os
from config import API_ID, API_HASH

client = None
session_phone = None

async def send_code(phone):
    global client, session_phone
    session_phone = phone
    
    session_file = f"session_{phone}.session"
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
        except:
            pass
    
    client = TelegramClient(session_file, API_ID, API_HASH)
    await client.connect()
    
    try:
        await client.send_code_request(phone)
        return True, "Код подтверждения отправлен на ваш номер. Введите его:"
    except errors.FloodWaitError as e:
        return False, f"Флуд-вейт {e.seconds} секунд. Подождите."
    except Exception as e:
        return False, f"Ошибка: {e}"

async def confirm_code(code):
    global client, session_phone
    try:
        await client.sign_in(session_phone, code)
        await client.disconnect()
        return True, "✅ Авторизация успешна! Сессия сохранена. Теперь можно парсить."
    except errors.SessionPasswordNeededError:
        return False, "❌ Включена двухфакторная аутентификация. Пока не поддерживается."
    except errors.PhoneCodeInvalidError:
        return False, "❌ Неверный код. Попробуйте снова."
    except errors.PhoneCodeExpiredError:
        return False, "❌ Код устарел. Запросите новый."
    except errors.FloodWaitError as e:
        return False, f"Флуд-вейт {e.seconds} секунд. Подождите."
    except Exception as e:
        return False, f"❌ Ошибка: {e}"

def is_authorized(phone):
    return os.path.exists(f"session_{phone}.session")
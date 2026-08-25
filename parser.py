from telethon import TelegramClient, functions, errors
import asyncio
from utils import save_user
from config import INVITE_DELAY

api_id = 25446655  # СВОЙ API ID
api_hash = "1b3072d11075e0a9ca9fbddd53b2cd28"  # СВОЙ API HASH

async def join_chat(chat_link):
    client = TelegramClient("session", api_id, api_hash)
    await client.start()
    
    try:
        entity = await client.get_entity(chat_link)
        
        try:
            await client.get_participants(entity, limit=1)
            await client.disconnect()
            return entity, True
        except errors.RPCError as e:
            if "USER_NOT_PARTICIPANT" in str(e) or "ChatAdminRequired" in str(e):
                try:
                    if hasattr(entity, "username") and entity.username:
                        await client.join_channel(entity)
                    else:
                        if "joinchat" in chat_link:
                            hash_part = chat_link.split("/")[-1]
                            await client(functions.messages.ImportChatInviteRequest(hash=hash_part))
                        else:
                            raise Exception("Не могу определить тип ссылки")
                    
                    await client.disconnect()
                    return await client.get_entity(chat_link), True
                except errors.InviteHashExpiredError:
                    raise Exception("Ссылка-приглашение просрочена")
                except errors.InviteHashInvalidError:
                    raise Exception("Неверная ссылка-приглашение")
                except errors.FloodWaitError as e:
                    raise Exception(f"Флуд-вейт: {e.seconds} секунд")
                except Exception as e:
                    raise Exception(f"Не удалось вступить: {e}")
            else:
                raise e
                
    except errors.UsernameNotOccupiedError:
        raise Exception("Такого юзернейма не существует")
    except errors.ChannelInvalidError:
        raise Exception("Неверный канал или ссылка")
    except Exception as e:
        await client.disconnect()
        raise Exception(f"Ошибка: {e}")

async def parse_chat(chat_link, progress_callback=None):
    client = TelegramClient("session", api_id, api_hash)
    await client.start()
    
    try:
        entity, is_member = await join_chat(chat_link)
        if not is_member:
            print("Успешно вступил в цель")
        
        count = 0
        async for user in client.iter_participants(entity):
            phone = user.phone if hasattr(user, "phone") else None
            save_user(user.username, user.id, user.first_name, phone)
            count += 1
            if progress_callback and count % 10 == 0:
                await progress_callback(count)
        
        await client.disconnect()
        return count
        
    except Exception as e:
        await client.disconnect()
        raise e

async def invite_users(target_link, progress_callback=None):
    client = TelegramClient("session", api_id, api_hash)
    await client.start()
    
    try:
        target, is_member = await join_chat(target_link)
        if not is_member:
            print("Успешно вступил в цель инвайта")
        
        invited = 0
        total = 0
        users = []
        
        with open("users.txt", "r", encoding="utf-8") as f:
            users = f.readlines()
            total = len(users)
        
        if total == 0:
            raise Exception("База пользователей пуста. Сначала выполни /parse")
        
        await client.disconnect()
        
        client2 = TelegramClient("session", api_id, api_hash)
        await client2.start()
        target2 = await client2.get_entity(target_link)
        
        for line in users:
            parts = line.split(" | ")
            if len(parts) >= 2:
                try:
                    tg_id = int(parts[1].strip())
                    
                    try:
                        await client2(functions.messages.AddChatUserRequest(
                            chat_id=target2.id,
                            user_id=tg_id,
                            fwd_limit=0
                        ))
                        invited += 1
                    except errors.UserPrivacyRestrictedError:
                        pass
                    except errors.UserNotMutualContactError:
                        pass
                    except errors.FloodWaitError as e:
                        print(f"Флуд-вейт {e.seconds} сек, ждём...")
                        await asyncio.sleep(e.seconds + 5)
                        try:
                            await client2(functions.messages.AddChatUserRequest(
                                chat_id=target2.id,
                                user_id=tg_id,
                                fwd_limit=0
                            ))
                            invited += 1
                        except:
                            pass
                    
                    if progress_callback:
                        await progress_callback(invited, total)
                    
                    await asyncio.sleep(INVITE_DELAY)
                    
                except Exception as e:
                    print(f"Ошибка при инвайте {tg_id}: {e}")
                    continue
        
        await client2.disconnect()
        return invited
        
    except Exception as e:
        await client.disconnect()
        raise e
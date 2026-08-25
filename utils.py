def save_user(username, tg_id, first_name, phone):
    phone = phone or "нет_номера"
    username = username or "нет_юзернейма"
    first_name = first_name or "нет_имени"
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(f"{username} | {tg_id} | {first_name} | {phone}\n")

def count_users():
    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            return len(f.readlines())
    except:
        return 0

def get_users():
    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []
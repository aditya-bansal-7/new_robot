import os
from pymongo import MongoClient

# Replace <password> with your actual password
password = '1Gwhiuum22x0hmqf'
cluster_url = 'mongodb+srv://adibnslboy:' + password + '@bnslboy.02zrow4.mongodb.net/'

# Create a MongoDB client
client = MongoClient(cluster_url)

# Access the desired database
db = client['main']

list_file = os.path.join(os.getcwd(), 'lists.json')

collection = db['invites']

try:
    with open(list_file, 'r') as f:
        persons = json.load(f)
except FileNotFoundError:
    pass
    
from pyrogram import Client , filters

API_ID = '1149607'
API_HASH = 'd11f615e85605ecc85329c94cf2403b5'

bot = Client("my_test", api_id=API_ID, api_hash=API_HASH, bot_token="6133256899:AAEdpzzSliAoYzXlGXeKMa7ixBBdMvju0HA")

@bot.on_message(filters.new_chat_members)
def chatmember(client,message):
    new_user = message.new_chat_members
    for user in new_user:
        new_member_id = user.id
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id != new_member_id:
            status = str(user.status)
            statuses = ["UserStatus.LAST_WEEK","UserStatus.ONLINE","UserStatus.OFFLINE","UserStatus.RECENTLY"]
            if status in [str(stat) for stat in statuses]:
                collection.update_one(
                    {'chat_id': chat_id, 'user_id': user_id},
                    {'$inc': {'total_count': 1, 'regular_count': 1,'left_count': 0,'fake_count': 0},
                    '$addToSet': {'new_members_ids': new_member_id}},
                    upsert=True
                )
            else:
                collection.update_one(
                    {'chat_id': chat_id, 'user_id': user_id},
                    {'$inc': {'total_count': 1, 'fake_count': 1,'regular_count': 0,'left_count': 0},
                    '$addToSet': {'fake_members_ids': new_member_id}},
                    upsert=True
                )

                
@bot.on_message(filters.left_chat_member)
def left_member(client,message):
    chat_id = message.chat.id
    left_member_id = message.left_chat_member.id
    inviter = collection.find_one(
        {'chat_id': chat_id, 'new_members_ids': left_member_id}
    )
    inviter2 = collection.find_one(
        {'chat_id': chat_id , 'fake_members_ids': left_member_id}
    )
    if inviter:
        inviter_id = inviter['user_id']

        # Decrement the invite count for the inviter
        collection.update_one(
            {'chat_id': chat_id, 'user_id': inviter_id},
            {'$inc': {'regular_count': -1 ,'left_count': 1}},
        )
    elif inviter2:
        inviter_id = inviter['user_id']
        collection.update_one(
            {'chat_id': chat_id, 'user_id': inviter_id},
            {'$inc': {'regular_count': 0 ,'left_count': 1}},
        )

@bot.on_message(filters.command(['invites']))
def invites_finder(client,message):
    chat_id = message.chat.id
    if len(message.text) == 8:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        inviter = collection.find_one(
        {'chat_id': chat_id, 'user_id': user_id})
        if inviter:
            t_count = inviter['total_count']
            r_count = inviter['regular_count']
            f_count = inviter['fake_count']
            l_count = inviter['left_count']
            text = f"User <a href='tg://user?id={user_id}'>{first_name}</a> currently have \n<b>{r_count}</b> invites. (<b>{t_count}</b> Regular,<b> {l_count}</b> left,<b> {f_count}</b> fake)"
        else:
            text = f"No data found for user <a href='tg://user?id={user_id}'>{first_name}</a>"
        bot.send_message(chat_id,text)
    else:
        args = message.text.split()[1:]
        text = "Here the requested Data\n\n"
        for user in args:
            member = bot.get_chat(user)
            user_id = member.id
            first_name = member.first_name
            inviter = collection.find_one(
        {'chat_id': chat_id, 'user_id': user_id})
            if inviter:
                t_count = inviter['total_count']
                r_count = inviter['regular_count']
                f_count = inviter['fake_count']
                l_count = inviter['left_count']
                text += f"User <a href='tg://user?id={user_id}'>{first_name}</a> currently have \n<b>{r_count}</b> invites. (<b>{t_count}</b> Regular,<b> {l_count}</b> left,<b> {f_count}</b> fake)\n\n"
            else:
                text += f"No data found for user <a href='tg://user?id={user_id}'>{first_name}</a>\n\n"
        bot.send_message(chat_id,text)

@bot.on_message(filters.command(['twisend']))
def twitter_send(client,message):
    try:
        chat_ids = persons['twitter']
        if message.reply_to_message :
            if message.reply_to_message.photo:
                file_id = message.reply_to_message.photo.file_id
                caption = message.reply_to_message.caption.html
                if message.reply_to_message.reply_markup:
                    markup = message.reply_to_message.reply_markup
                    for chat_id in chat_ids:
                        try:
                            send_photo = bot.send_photo(chat_id, file_id, caption=caption, reply_markup=markup)
                            bot.pin_chat_message(send_photo.chat.id, send_photo.id, True)
                            bot.delete_messages(send_photo.chat.id, send_photo.id+1)
                        except Exception as e:
                            continue
                else:
                    for chat_id in chat_ids:
                        try:
                            send_photo = bot.send_photo(chat_id, file_id, caption=caption)
                            bot.pin_chat_message(send_photo.chat.id, send_photo.id, True)
                            bot.delete_messages(send_photo.chat.id, send_photo.id+1)
                        except Exception as e:
                            continue
            elif message.reply_to_message.text:
                text = message.reply_to_message.text.html
                if message.reply_to_message.reply_markup:
                    markup = message.reply_to_message.reply_markup
                    for chat_id in chat_ids:
                        try:
                            send_message = bot.send_message(chat_id, text, disable_web_page_preview=True, reply_markup=markup)
                            bot.pin_chat_message(send_message.chat.id, send_message.id)
                            bot.delete_messages(send_message.chat.id, send_message.id+1)
                        except Exception as e:
                            continue
                else:
                    send_message = bot.send_message(chat_id, text, disable_web_page_preview=True, reply_markup=markup)
                    bot.pin_chat_message(send_message.chat.id, send_message.id)
                    bot.delete_messages(send_message.chat.id, send_message.id+1)

    except Exception as e :
        print(e)
        
@bot.on_message(filters.command(['topinvites']))
def top_invites(client,message):
    chat_id = message.chat.id

    top_invites = collection.find(
            {"chat_id": chat_id}
        ).sort("regular_count", -1).limit(10)
    response = "Top 10 Invites:\n\n"
    for index, invite in enumerate(top_invites):
        user_id = invite["user_id"]
        t_count = invite['total_count']
        r_count = invite['regular_count']
        f_count = invite['fake_count']
        l_count = invite['left_count']
        member = bot.get_chat(user_id)
        first_name = member.first_name
        last_name = member.last_name
        response += f"{index + 1}. <a href='tg://user?id={user_id}'>{first_name} {last_name}</a> , <b>{r_count}</b> Invites. (<b>{t_count}</b> Regular,<b> {l_count}</b> left,<b> {f_count}</b> fake)\n"
    bot.send_message(chat_id,response)

bot.run()

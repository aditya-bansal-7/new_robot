import os
import json
from pymongo import MongoClient
import time
import threading
import csv
# Replace <password> with your actual password
password = '1Gwhiuum22x0hmqf'
cluster_url = 'mongodb+srv://adibnslboy:' + password + '@bnslboy.02zrow4.mongodb.net/'

# Create a MongoDB client
client = MongoClient(cluster_url)

# Access the desired database
db = client['main']

list_file = os.path.join(os.getcwd(), 'lists.json')

collection = db['invites']

roles = db['roles']



try:
    with open(list_file, 'r') as f:
        persons = json.load(f)
except FileNotFoundError:
    pass
    
from pyrogram import Client , filters ,types , enums 

API_ID = '1149607'
API_HASH = 'd11f615e85605ecc85329c94cf2403b5'

bot = Client("my_test", api_id=API_ID, api_hash=API_HASH, bot_token="6133256899:AAFdu-7c_Sd8vZ886rW3p_GAgaXgQZKF7rk")

app = Client("assistant", api_id=API_ID, api_hash=API_HASH)

app.start()

app.send_message(1443989714, "I am alive2")
bot.start()
bot.send_message(1443989714, "I am alive2")
bot.stop()

def alive_check():
    time.sleep(10)
    while True:
        bot.send_message(1443989714, "I am alive2")
        time.sleep(600)


time_threa = threading.Thread(target=alive_check)
time_threa.start()

@bot.on_message(filters.new_chat_members)
def chatmember(client, message):
    new_user = message.new_chat_members
    for user in new_user:
        new_member_id = user.id
        new_member_username = user.username
        new_member_firstname = user.first_name
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id != new_member_id:
            status = str(user.status)
            statuses = ["UserStatus.LAST_WEEK", "UserStatus.ONLINE",
                        "UserStatus.OFFLINE", "UserStatus.RECENTLY"]
            if status in [str(stat) for stat in statuses]:
                collection.update_one(
                    {'chat_id': chat_id, 'user_id': user_id},
                    {'$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'g_count': 1},
                     '$addToSet': {'new_members_ids': new_member_id, 'new_member_username': new_member_username, 'new_member_firstname': new_member_firstname}},
                    upsert=True
                )
            else:
                collection.update_one(
                    {'chat_id': chat_id, 'user_id': user_id},
                    {'$inc': {'total_count': 1, 'fake_count': 1, 'regular_count': 0, 'left_count': 0, 'g_count': 0},
                     '$addToSet': {'fake_members_ids': new_member_id, 'fake_member_firstname': new_member_firstname, 'fake_member_username': new_member_username}},
                    upsert=True
                )
        else:
            links = collection.find(
                {'chat_id': chat_id}
            )
            for link in links:
                if 'invite_link' in link:
                    invite_link = link['invite_link']
                    user_id = link['user_id']
                    if 'invite_count' in link:
                        invi_count = link['invite_count']
                        try:
                            invi = app.get_chat_invite_link_joiners_count(
                                chat_id, invite_link)

                            if invi_count != invi:
                                users = app.get_chat_invite_link_joiners(
                                    chat_id, invite_link)
                                for user in users:
                                    if user.user.id == new_member_id:
                                        collection.update_one(
                                            {'chat_id': chat_id, 'user_id': user_id},
                                            {'$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'invite_count': 1, 'g_count': 1},
                                            '$addToSet': {'new_members_ids': new_member_id}},
                                            upsert=True
                                        )
                                        break
                        except Exception:
                            pass
                    else:
                        try:
                            if invi_count != invi:
                                users = app.get_chat_invite_link_joiners(
                                    chat_id, invite_link)
                                for user in users:
                                    if user.user.id == new_member_id:
                                        collection.update_one(
                                            {'chat_id': chat_id, 'user_id': user_id},
                                            {'$inc': {'total_count': 1, 'regular_count': 1, 'left_count': 0, 'fake_count': 0, 'invite_count': 1, 'g_count': 1},
                                            '$addToSet': {'new_members_ids': new_member_id}},
                                            upsert=True
                                        )
                                        break
                        except Exception:
                            pass

        

                
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
    if message.text == "/invites" or message.text == "/invites@Binaryx_robot":
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
            else:
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
        bot.send_message(1443989714,f"{e}")
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
    if response == "Top 10 Invites:\n\n":
        response = "No Data Found"
    bot.send_message(chat_id,response)

def delete_tracker():
    while True:
        data = collection.find()
        chats = []
        for dat in data:
            if 'chat_id' in dat:
                chat_id = dat['chat_id']
                if chat_id not in chats:
                    chats.append(chat_id)
        for chat_id in chats:
            try:
                members = bot.get_chat_members(chat_id)
                for member in members:
                    if member.user.is_deleted:
                        left_member_id = member.user.id
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
                                {'$pull': {'new_members_ids': left_member_id}}
                            )
                        elif inviter2:
                            inviter_id = inviter['user_id']
                            collection.update_one(
                                {'chat_id': chat_id, 'user_id': inviter_id},
                                {'$inc': {'regular_count': 0 ,'left_count': 1}},
                                {'$pull': {'fake_members_ids': left_member_id}}
                            )
            except Exception:
                continue
        time.sleep(86400)

@bot.on_message(filters.command(['get_data']) & filters.private)
def get_data(client,message):

    user_id = message.from_user.id
    data = collection.find()
    chats = []
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    for dat in data:
        if 'chat_id' in dat:
            chat_id = dat['chat_id']
            if chat_id not in chats:
                chats.append(chat_id)
    for chat_id in chats:
        try:
            admins = bot.get_chat_members(chat_id,filter=enums.ChatMembersFilter.ADMINISTRATORS)
            for admin in admins:
                if admin.user.id == user_id:
                    chat = bot.get_chat(chat_id)
                    markup.inline_keyboard.append([types.InlineKeyboardButton(f'{chat.title}', callback_data=f'data:{chat_id}:{user_id}')])
        except Exception :
            continue
    text = "👉🏻 <u>Select the group</u> whose invite data you want to get.\n\n"
    text += "If a group in which you are an administrator doesn't appear here:\n • Either their is not a single invite data\n • Bot is not admin in that group"
    if chats !=[]:
        bot.send_message(message.chat.id,text,reply_markup=markup)
    else:
        bot.send_message(message.chat.id,text)


time_threa = threading.Thread(target=delete_tracker)
time_threa.start()


@bot.on_callback_query()
def callback_handler(client, callback_query):
    call = callback_query
    if call.data.startswith(("data:")):
        chat_id = int(call.data.split(":")[1])
        user_id = int(call.data.split(":")[2])
        try:
            data = collection.find({'chat_id': chat_id}).sort("regular_count", -1)
            formatted_data = []
            serial_number = 1
            for da in data:
                # Extract the necessary data
                user_id = da['user_id']
                user = bot.get_chat_member(chat_id, user_id)
                total_invites_ = da['regular_count']
                regular_invites_ = da['total_count']
                left_invites_ = da['left_count']
                fake_invites_ = da['fake_count']
                username_ = user.user.username
                firstname_ = user.user.first_name

                # Format the data into a dictionary
                formatted_entry = {
                    'Serial No.': serial_number,
                    'Username': username_,
                    'First Name': firstname_,
                    'Total Invites': total_invites_,
                    'Regular Invites': regular_invites_,
                    'Fake Invites': fake_invites_,
                    'Left Invites': left_invites_
                }
                serial_number += 1
                # Append the formatted entry to the list
                formatted_data.append(formatted_entry)

            # Define the field names for the CSV file
            field_names = ['Serial No.', 'Username', 'First Name', 'Total Invites', 'Regular Invites', 'Fake Invites', 'Left Invites']
            chat = bot.get_chat(chat_id)
            # Generate the file name based on the chat title
            filename = os.path.join(os.getcwd(), 'invite-data.csv')

            # Write the formatted data to the CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                writer.writerows(formatted_data)

            # Send the CSV file to the user
            bot.send_document(user_id, filename)
            bot.send_message(user_id,f"Invite data for {chat.title}")
        except Exception as e:
            # Handle the exception
            error_message = str(e)
            # Log the error or take any other necessary actions
            # ...
            print(e)
            # Inform the user about the error
            bot.send_message(user_id, f"An error occurred while getting data \n\n\n\n\n {error_message}")

@bot.on_message(filters.command(['role']))
def roles_given(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    reply = message.reply_to_message
    if reply:
        user = reply.from_user.id
        user_name = reply.from_user.first_name
        role_name = message.text.split(" ")[1].lower()
        if role_name is None:
            bot.send_message(
                chat_id, "You did not provide me role name", reply_to_message_id=message.id)
            return

        find = roles.find_one(
            {'chat_id': chat_id, 'user_id': user, 'roles': role_name})
        if find:
            bot.send_message(
                chat_id, f"{user_name} already have {role_name} role", reply_to_message_id=message.id)
            return
        roles.update_one({'chat_id': chat_id, 'user_id': user},
                         {'$addToSet': {'roles': role_name},
                          '$set': {'first_name': user_name}},
                         upsert=True)
        bot.send_message(
            message.chat.id, f"{user_name} has been given the role of {role_name} in this chat")
    else:
        role_name = message.text.split(" ")[1].lower()
        if role_name is None:
            bot.send_message(
                chat_id, "You did not provide me role name", reply_to_message_id=message.id)
            return
        username = message.text.split(" ")[2:]
        if username is None:
            bot.send_message(chat_id, "You did not provide me users",
                             reply_to_message_id=message.id)
            return
        message_test = "User -  "
        for user in username:
            if not user.startswith("@"):
                bot.send_message(chat_id,f"Error : {user} does not have a username")
                continue
            usser = bot.get_chat(user)
            usser_id = usser.id
            usser_name = usser.first_name

            find = roles.find_one(
                {'chat_id': chat_id, 'user_id': usser_id, 'roles': role_name})
            if find:
                bot.send_message(
                    chat_id, f"{usser_name} already have {role_name} role", reply_to_message_id=message.id)
                continue

            message_test += f"{user}, "
            roles.update_one({'chat_id': chat_id, 'user_id': usser_id},
                             {'$addToSet': {'roles': role_name},
                              '$set': {'first_name': usser_name}}, upsert=True)
        message_test += f"\n have been given the role of {role_name} in this chat"
        if message_test == "User -  \n have been given the role of ids in this chat":
            pass
        else:
            bot.send_message(chat_id,message_test)


@bot.on_message(filters.command(['me']) & filters.group)
def me_check(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    data = roles.find_one({'user_id': user_id, 'chat_id': chat_id})

    if data:
        messagetext = "Current you have following Roles :-"
        rolees = data['roles']
        for role in rolees:
            messagetext += f"\n • {role}"
        bot.send_message(chat_id, messagetext)
    else:
        messagetext = "Current you have following Roles :-"
        bot.send_message(chat_id, messagetext)


@bot.on_message(filters.command(['invite_link']) & filters.group)
def create_invite_link(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        check = bot.get_chat_member(chat_id,5033228818)
        if not str(check.status) == "ChatMemberStatus.ADMINISTRATOR":
            bot.send_message(chat_id,"@Binaryx_robot_assistant is not admin in this group")
            return
    except Exception:
        app.join_chat(chat_id)
        # bot.send_message(chat_id,"@Binaryx_robot_assistant is not admin in this group")
    data = collection.find_one(
        {'chat_id': chat_id, 'user_id': user_id}
    )
    if data:
        if 'invite_link' in data:
            link = data['invite_link']
            try:
                bot.send_message(
                    user_id, f"Here is your link for group {message.chat.title} \n {link}")
                bot.send_message(
                    chat_id, "I have created your invite link. Message me to see it.")
            except Exception as e:
                bot.send_message(chat_id, f"Here is your link - {link}")

        else:
            link = app.create_chat_invite_link(
                chat_id, f"{message.from_user.first_name} by @Binaryx_Robot")
            invite_link = link.invite_link
            try:
                bot.send_message(
                    user_id, f"Here is your link for group {message.chat.title} \n {invite_link}")
                bot.send_message(
                    chat_id, "I have created your invite link. Message me to see it.")
            except Exception as e:
                pass
            collection.update_one(
                {'chat_id': chat_id, 'user_id': user_id},
                {'$set': {'invite_link': invite_link}},
                upsert=True
            )
    else:
        link = app.create_chat_invite_link(
            chat_id, f"{message.from_user.first_name} by @Binaryx_Robot")
        invite_link = link.invite_link
        try:
            bot.send_message(
                user_id, f"Here is your link for group {message.chat.title} \n {invite_link}")
            bot.send_message(chat_id, "I have created your invite link. Message me to see it.")
        except Exception as e:
            pass
        collection.update_one(
            {'chat_id': chat_id, 'user_id': user_id},
            {'$set': {'invite_link': invite_link},
             '$inc': {'total_count': 0, 'regular_count': 0, 'left_count': 0, 'fake_count': 0}},
            upsert=True
        )

@bot.on_message(filters.command(['invite_link']) & filters.private)
def invite_link(client, message):
    user_id = message.from_user.id
    data = collection.find({'user_id': user_id})
    message_text = "Here all invite link with group -"
    i = 1
    if data:
        for da in data:
            if 'invite_link' in da:
                chat_id = da['chat_id']
                try:
                    chat = bot.get_chat(chat_id)
                except Exception:
                    continue
                title = chat.title
                link = da['invite_link']
                message_text += f"\n\n {i}. {title}-\n {link}"
                i += 1
    bot.send_message(user_id,message_text)
    
bot.run()

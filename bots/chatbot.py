import random
import telebot
import pymongo
import traceback
import config

bot = telebot.TeleBot(config.environ['chatbot'])
client = pymongo.MongoClient(config.environ['database'])
db = client.test
col = db.chatting
admin = config.creator
# print(col.find_one({'group_id':{'$exists':True}})['msgs_to_index'])


def write_to_db(m):
    if m.reply_to_message and m.text and m.reply_to_message.text and not m.reply_to_message.from_user.is_bot and not m.reply_to_message.text.startswith(
            '@') and not m.reply_to_message.text.startswith('/'):
        col.update_one({'group_id': m.chat.id},
                       {'$push': {'msgs_to_index': m.reply_to_message.text.lower()}},
                       upsert=True)
        col.update_one({'group_id': m.chat.id},
                       {'$push': {m.reply_to_message.text.lower().replace('.', 'dot_replace'): m.text}},
                       upsert=True)


@bot.message_handler(content_types='text')
def chatting(m):
    try:
        if col.find_one({'group_id': m.chat.id}):
            msgs_to_index = col.find_one({'group_id': m.chat.id})['msgs_to_index']
            if True:
                if m.text.lower() in msgs_to_index and not m.reply_to_message or m.text in msgs_to_index and not m.reply_to_message.from_user.is_bot:
                    answer = col.find_one({'group_id': m.chat.id})[m.text.lower().replace('.', 'dot_replace')]
                    answer = random.choice(answer)
                    bot.send_message(m.chat.id, answer, reply_to_message_id=m.message_id)
                else:
                    return write_to_db(m)
        else:
            return write_to_db(m)

    except:
        bot.send_message(admin, traceback.format_exc())

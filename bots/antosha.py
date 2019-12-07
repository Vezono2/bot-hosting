import telebot
from manybotslib import BotsRunner
from telebot import types

import os

import time
import random
import threading

import traceback

from pymongo import MongoClient
bot_token = os.environ['antosha']
bot = telebot.TeleBot(bot_token)
client=MongoClient(os.environ['database'])
db=client.antosha
phrases=db.phrases

import io
import string # to process standard python strings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('popular', quiet=True) # for downloading packages
#nltk.download('punkt') # first-time use only
#nltk.download('wordnet') # first-time use only

pasukid = 214670864
creator = 792414733

timings = '''
1. Персонажи, все, включая закадровых - 11-12 декабря.
Нужна характеристика.
2. Сюжет - с 12 по 18-19 декабря. Важно каждое предложение.
3. Изображения локаций, персонажей - с 19 по 24-25 декабря.
На изображении требуются: персонаж в полнорост, без сложной позы, палитра, краткое описание персонажа, макет.
4. Оформление - с 25 по 31 декабря.

ДЕДЛАЙН РЕЛИЗА ФАНФИКА - 3 ЯНВАРЯ.
'''
lophrase = []
x = phrases.find_one({})
for ids in x:
    if x[ids]:
        lophrase.append(x[ids])
lophrase.remove(lophrase[0])

sent_tokens = lophrase# converts to list of sentences 


word_tokens = []
for sent in lophrase:
    for word in sent.split(' '):
        word_tokens.append(word)

# Preprocessing
lemmer = WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))    

GREETING_INPUTS = ["Привет"]
GREETING_RESPONSES = ["Пока"]

def getresponse(user_response):
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if not req_tfidf:
        return "Жизненно"
    else: 
        return sent_tokens[idx]
@bot.message_handler(commands=['status'])
def status(m):
    bot.reply_to(m, runner.get_status())
@bot.message_handler(commands=['getm'])
def status(m):
    if m.from_user.id == creator:
        bot.reply_to(m, str(m))
@bot.message_handler(commands=['timings'])
def status(m):
    bot.reply_to(m, timings)        
@bot.message_handler(commands=['tea'])
def ftea(m):
    print('Завариваем чай...')
    if m.reply_to_message:
        from_user = m.from_user.first_name
        if m.text.count(' ') == 0:
            tea = 'обычный'
        else:
            tea = m.text.split(' ', 1)[1]
        touser = m.reply_to_message.from_user.first_name
        ahref = '<a href="tg://user?id={}">{}</a>'.format(m.reply_to_message.from_user.id, touser)
        kb = types.InlineKeyboardMarkup()
        btns = []
        btns2 = []
        for i in ['drink', 'reject']:
            btns.append(types.InlineKeyboardButton(rus(i), callback_data='{} {}'.format(i, touser)))
        for i in ['throw']:
            btns2.append(types.InlineKeyboardButton(rus(i), callback_data='{} {}'.format(i, touser)))
        kb.add(*btns)
        kb.add(*btns2)
        if touser == bot.get_me().first_name:
            tts = 'Н-но это я должен готовить чай вам, ' + from_user + '!!'
            kb = None
        else:
            tts = '{} приготовил чай "{}" для вас, {}!'.format(from_user, tea, ahref)
        bot.delete_message(m.chat.id, m.message_id)
        bot.send_message(m.chat.id, tts, reply_markup=kb, parse_mode='HTML')
    else:
        if m.text.count(' ') == 0:
            tea = 'обычный'
        else:
            tea = m.text.split(' ', 1)[1]
        tts = '{} заварил себе чай "{}"!'.format(m.from_user.first_name, tea)
        bot.delete_message(m.chat.id, m.message_id)
        bot.send_message(m.chat.id, tts)

        
@bot.message_handler()
def texthandler(m):
    if m.forward_from:
        if m.forward_from.id == pasukid:
            phrases.update_one({}, {'$set': {m.text.replace('.', ''):m.text}})
    else:
        if m.from_user.id == pasukid:
            phrases.update_one({}, {'$set': {m.text.replace('.', ''):m.text}})
    if not pinloshadkin(m):# or not random.randint(1, 100) > 99:
        return
    response = random.choice(lophrase)
    sended = 0
    mem = lophrase
    random.shuffle(mem)
    alpha = random.choice([True, False])
    if not alpha:
        for phrase in mem:
            if phrase:
                for word in phrase.split(' '):
                    text = m.text.lower()
                    text = text.replace('я', 'ты').replace('ты', 'я')
                    if word.lower() in text.split(' ') and not sended:
                        bot.reply_to(m, phrase)
                        sended +=1
                        break
                        break
    else:
        user_response = m.text.lower()
        tts = getresponse(user_response).capitalize()
        bot.reply_to(m, tts)        
r = {'drink': 'Выпить',
     'reject': 'Отказаться',
     'throw': 'Вылить'}
@bot.callback_query_handler(lambda c: True)
def callback_handler(c):
    print(c)
    action = c.data.split(' ')[0]
    touser = c.data.split(' ', 1)[1]
    tea = c.message.text.split('"')[1]
    if touser == c.from_user.first_name:
        if action == 'drink':
            tts = 'Вы выпили чай "{}", {}!'.format(tea, touser)
        elif action == 'reject':
            tts = 'Вы отказались от чая "{}", {}!'.format(tea, touser)
        elif action == 'throw':
            tts = 'Вы вылили в унитаз чай "{}", {}!!'.format(tea, touser)
        elif action == 'Да':
            tts = 'Вы выпили чай "{}", {}!! Спасибо!!!'.format(tea, touser)
        elif action == 'Нет':
            tts = 'Простите, {}.'.format(touser)
    else:
        return
    bot.edit_message_text(tts, c.message.chat.id, c.message.message_id)
def rus(name):
    try:
        return r[name]
    except:
        return name
def pinloshadkin(m):
    if m.reply_to_message:
        if m.reply_to_message.from_user.id == bot.get_me().id:
            return True
    if random.randint(1, 50) == 1:
        return True
    for i in ['бот', 'антон']:
        if i in m.text.lower():
            return True    
runner = BotsRunner([792414733]) # pass empty list if you don't want to receive error messages on fail
runner.add_bot("Antosha", bot)
runner.set_main_bot(bot)
print('Antosha works!')
runner.run()

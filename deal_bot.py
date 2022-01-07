import telebot
from telebot import types
import pandas as pd
import traceback
import re

#TODO нужно сделать базу даннызх с делами

token_path = r"credentials.txt"
bot_token = open(token_path).readlines()[0].replace('\n', '')

top_users = ['dampall']

message_dict = {'welcome': 'Hello! Type here your deals with command /deals',
                'preparing': 'Parsing deals...',
                'exception': 'Get exception: ',
                'parsed': 'Deals are parsed',
                'show_deals': 'Choose priority type:',
                'no_deals': 'Deals are not filled, please fill with command /deals'}
deals_df = None

try:
    bot = telebot.TeleBot(bot_token)


    @bot.message_handler(commands=['start'])
    def start_handler(message):
        username = message.from_user.username
        chat_id = message.chat.id
        if username in top_users:
            bot.send_message(chat_id, message_dict['welcome'], parse_mode='HTML')


    @bot.message_handler(commands=['deals'])
    def get_deals(message):
        username = message.from_user.username
        chat_id = message.chat.id
        if username in top_users:
            bot.send_message(chat_id, message_dict['preparing'], parse_mode='HTML')
            try:
                deals_df = parse_deals(message.text.replace('/deals', ''))
                bot.send_message(chat_id, message_dict['parsed'], reply_markup=welcoming_buttons(), parse_mode='HTML')
            except Exception as e:
                bot.send_message(chat_id, message_dict['exception'] + e, parse_mode='HTML')


    @bot.message_handler(commands=['show_deals'])
    def show_deals(message):
        username = message.from_user.username
        chat_id = message.chat.id
        if username in top_users:
            if deals_df:
                bot.send_message(chat_id, message_dict['show_deals'], reply_markup=welcoming_buttons(),
                                 parse_mode='HTML')
            else:
                bot.send_message(chat_id, message_dict['no_deals'], parse_mode='HTML')


    @bot.callback_query_handler(func=lambda call: True)
    def handle_buttons(call):
        print('Handle buttons')
        msg = str(call.data)
        chat_id = call.message.chat.id
        if msg == '/sv_cb':
            print('sv_cb')
            reply_str = 'СВ deals:\n'
            sample_df = deals_df.loc[deals_df['priority'] == 'СВ', 'task'].to_frame()
            for index, row in sample_df.iterrows():
                reply_str += row['task']
            reply_str = reply_str.replace('\n', '\n\n')
            bot.send_message(chat_id, reply_str, reply_markup=welcoming_buttons(), parse_mode='HTML')
        elif msg == '/sn_cb':
            reply_str = 'СН deals:\n'
            sample_df = deals_df.loc[deals_df['priority'] == 'СН', 'task'].to_frame()
            for index, row in sample_df.iterrows():
                reply_str += row['task']
            reply_str = reply_str.replace('\n', '\n\n')
            bot.send_message(chat_id, reply_str, reply_markup=welcoming_buttons(), parse_mode='HTML')
        elif msg == '/nv_cb':
            reply_str = 'СН deals:\n'
            sample_df = deals_df.loc[deals_df['priority'] == 'НВ', 'task'].to_frame()
            for index, row in sample_df.iterrows():
                reply_str += row['task']
            reply_str = reply_str.replace('\n', '\n\n')
            bot.send_message(chat_id, reply_str, reply_markup=welcoming_buttons(), parse_mode='HTML')
        elif msg == '/nn_cb':
            reply_str = 'НН deals:\n'
            sample_df = deals_df.loc[deals_df['priority'] == 'НН', 'task'].to_frame()
            for index, row in sample_df.iterrows():
                reply_str += row['task']
            reply_str = reply_str.replace('\n', '\n\n')
            bot.send_message(chat_id, reply_str, reply_markup=welcoming_buttons(), parse_mode='HTML')
        else:
            bot.send_message(chat_id, 'some error', reply_markup=welcoming_buttons(), parse_mode='HTML')


    def welcoming_buttons():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='СВ', callback_data='/sv_cb'),
                   types.InlineKeyboardButton(text='СН', callback_data='/sn_cb'),
                   types.InlineKeyboardButton(text='НВ', callback_data='/nv_cb'),
                   types.InlineKeyboardButton(text='нн', callback_data='/nn_cb'))
        return markup


    def parse_deals(total_str):
        deal_keys = 'СВ|НВ|СН|НН'
        deal_list = re.split(deal_keys, total_str)
        deals_df = pd.DataFrame(columns=['priority', 'task'])
        for i in range(len(deal_list)-1):
            if i % 2 == 0:
                priority_key = deal_list[i+1]
                deals_df = deals_df.append({'priority': priority_key, 'task': deal_list[i]}, ignore_index=True)
        return deals_df

    while 1:
        try:
            print('start housebot')
            bot.polling()
        except Exception as e:
            print(f'Exception:\n{e}\n\nTraceback:\n{traceback.format_exc()}')

except Exception as e:
    print(f'Exception:\n{e}\n\nTraceback:\n{traceback.format_exc()}')

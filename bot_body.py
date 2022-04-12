import telebot
from telebot import types
import time
from receiving_api import get_api
import logging
import os
import zipfile
import shutil


logging.basicConfig(filename="log.txt", level=logging.INFO)
API_KEY = get_api()
bot = telebot.TeleBot(API_KEY)


# Keyboard buttons
def creating_a_keyboard(num_of_que=99):
    greet_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, num_of_que, 20):
        greet_menu.row(f'{i}-{i + 9}', f'{i + 10}-{i+19}')

    greet_menu.row('Список вопросов')
    greet_menu.row('Какие вопросы уже есть?')
    greet_menu.row('Добавьте меня!')
    return greet_menu


if os.path.exists('list.txt'):
    with open('list.txt', 'r', errors='ignore') as opened_file:
        num_of_q = len(opened_file.readlines())
else:
    num_of_q = 0

greet_menu = creating_a_keyboard(num_of_q)

# global variables
msg_info_from_bot = telebot.types.Message
msg_info_from_user = telebot.types.Message


def debug_write(msg):
    print(msg)
    bot.send_message(449808966, msg)
    logging.error(f'{msg}\n')


def get_user_list():
    if 'users.txt' not in os.listdir():
        with open('users.txt', 'w'):
            pass
    with open('users.txt', 'r') as opened_file:
        user_list_native = opened_file.readlines()
        user_list = []
        for elem in user_list_native:
            user_list.append(int(elem[:-1]))
    return user_list


def remove_old_dump():
    try:
        bot.send_message(449808966, 'Old dump:')
        bot.send_document(449808966, open('questions.zip', 'rb'))
        os.remove('questions.zip')
    except Exception as exc:
        bot.send_message(449808966, 'No old dumps!')
        print(f'\n{type(exc)}\n{exc}')


def make_dir():
    try:
        os.mkdir('questions')
    except Exception as exc:
        print(f'\n{type(exc)}\n{exc}')
        pass


def get_new_dump():
    remove_old_dump()
    with zipfile.ZipFile('questions.zip', "w") as zf:
        files = os.listdir('questions')
        for file in files:
            zf.write(f'questions/{file}')
    bot.send_message(449808966, 'New dump:')
    bot.send_document(449808966, open('questions.zip', 'rb'))


def get_que_list(file_name: str, ran='1-100') -> list:
    import codecs
    with codecs.open(file_name, 'r', encoding='utf-8') as opened_file:
        ans_list = []
        lines = opened_file.readlines()
        for line in lines:
            if int(line.split('.')[0]) in range(int(ran.split('-')[0]), int(ran.split('-')[1]) + 1):
                ans_list.append(line)
    return ans_list


def send_long_msg(user_id: int, message: str, reply: bool, msg_len_limit=50):
    message_list = message.split('\n')
    if len(message_list) < msg_len_limit:
        if reply:
            bot.send_message(user_id, message, reply_markup=greet_menu)
        else:
            bot.send_message(user_id, message)
    else:
        while True:
            if len(message_list) > msg_len_limit - 1:
                ans = message_list[:msg_len_limit - 1]
                if reply:
                    bot.send_message(user_id, '\n'.join(ans), reply_markup=greet_menu)
                else:
                    bot.send_message(user_id, '\n'.join(ans))
                message_list = message_list[msg_len_limit - 1:]
            else:
                ans = message_list[:msg_len_limit - 1]
                bot.send_message(user_id, '\n'.join(ans))
                break


def send_long_msg_len(user_id: int, message: str, reply: bool, msg_len_limit=4000):
    if len(message) < msg_len_limit:
        if reply:
            bot.send_message(user_id, message, reply_markup=greet_menu)
        else:
            bot.send_message(user_id, message)
    else:
        while True:
            if len(message) > msg_len_limit - 1:
                ans = message[:msg_len_limit - 1]
                if reply:
                    bot.send_message(user_id, ans, reply_markup=greet_menu)
                else:
                    bot.send_message(user_id, ans)
                message = message[msg_len_limit - 1:]
            else:
                ans = message[:msg_len_limit - 1]
                bot.send_message(user_id, ans)
                break


def get_lists_of_ranges(input_list: list) -> str:
    """Collapses list into string with its ranges"""
    range_list_native = [input_list[0]]
    result_list = []
    input_list.sort()

    for elem_ind in range(1, len(input_list)):

        if input_list[elem_ind] - 1 == input_list[elem_ind - 1]:
            range_list_native.append(input_list[elem_ind])
        else:
            result_list.append(range_list_native)
            range_list_native = [input_list[elem_ind]]
    result_list.append(range_list_native)

    range_list = []

    for elem in result_list:

        if len(elem) == 1:
            range_list.append(str(elem[0]))
        else:
            range_list.append(f'{elem[0]}-{elem[-1]}')

    result = ', '.join(range_list)

    return result


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_list = get_user_list()
    if message.text == '/start':
        welcome_msg = f'Привет! Тут любят только хороших мальчиков и девочек. Если ты такой(ая),' \
                      f' нажимай "Добавьте меня!"\n\nХочешь посмотреть ответ? Используй' \
                      f' клавиатуру!\n\nХочешь добавить текст вопроса? Пиши "07 Текст..." :)'
        bot.send_message(message.chat.id, welcome_msg, reply_markup=greet_menu)

    elif message.text == 'Добавьте меня!':
        if message.from_user.id in user_list:
            answer_text = f'Ты уже в списке :)'
        else:
            answer_text = f'Сейчас попрошу @Jenderlion тебя добавить  :)'
            bot.send_message(449808966, f'User @{message.from_user.username} asks you to be added.'
                                        f'\nHis id is: {message.from_user.id}')
        bot.send_message(message.chat.id, answer_text)

    elif message.from_user.id == 449808966 and message.text[0] == '/':
        if message.text[0:8] == '/message':
            global_msg = message.text[9:]
            for user_id in user_list:
                try:
                    bot.send_message(user_id, global_msg, reply_markup=greet_menu)
                    time.sleep(1)
                except Exception as exc:
                    bot.send_message(449808966, f'{user_id} not allowed.\n{type(exc)}\n{exc}')
            debug_text = f'Message: {global_msg}\nStatus: delivered!'
            debug_write(debug_text)

        elif message.text[0:7] == '/remove':
            with open('users.txt', 'w'):
                pass
            bot.send_message(449808966, 'All users removed!')
        elif message.text[0:4] == '/log':
            bot.send_document(449808966, open('log.txt', 'r'))
        elif message.text[0:4] == '/add':
            if len(str(message.text)) > 6:
                user_id_to_add = message.text[5:]
                if 'users.txt' not in os.listdir():
                    with open('users.txt', 'w'):
                        pass
                with open('users.txt', 'a') as opened_file:
                    opened_file.write(f'{user_id_to_add}\n')
                answer_text = f'Done'
                debug_text = f'User with id {user_id_to_add} added successfully'
                try:
                    bot.send_message(user_id_to_add, 'Тебя добавили. Можешь мной пользоваться :)')
                except Exception as exc:
                    bot.send_message(449808966, f'Exception!\n{type(exc)}\n{exc}')
            else:
                answer_text = f'False'
                debug_text = f'ID is too short'

            bot.send_message(message.chat.id, answer_text)
            debug_write(debug_text)
        elif message.text[0:5] == '/dump':
            get_new_dump()
        elif message.text[0:7] == '/delete':
            get_new_dump()
            shutil.rmtree('questions')
            bot.send_message(449808966, '"questions/" is now clear!')
        elif message.text[0:6] == '/chat':
            ans = bot.get_chat_members_count(message.chat.id)
            print(ans)
        elif message.text[0:6] == '/users':
            bot.send_document(449808966, open('users.txt', 'r'))
        else:
            bot.send_message(449808966, 'Use the following commands:\n\n'
                                        '/message - to send global message\n'
                                        '/log - to get log.txt\n'
                                        '/add - to add user\n'
                                        '/dump - to download archive\n'
                                        '/delete - to delete all questions\n'
                                        '/users - to get users.txt\n'
                                        '/remove - to remove all users')

    elif message.from_user.id in user_list or message.from_user.id == 449808966:

        if message.text in ('Выбрать другой вопрос', 'Список вопросов'):

            que_list = get_que_list('list.txt')

            send_long_msg(message.chat.id, f'Выбирай:\n{"".join(que_list)}', reply=True)

        elif message.text == 'Какие вопросы уже есть?':
            que_list = (os.listdir('questions'))
            if len(que_list) > 0:
                msg_text = 'Сейчас есть ответы на эти вопросы:'
                que_num_list = []
                for que in que_list:
                    que_num_list.append(int(que[:-4]))
                msg_text += f'\n{get_lists_of_ranges(que_num_list)}'
            else:
                msg_text = 'Пока ответов на вопросы нет :('

            bot.send_message(message.chat.id, msg_text, reply_markup=greet_menu)

        elif len(message.text.split()[0].split('-')) == 2:
            msg_txt = message.text.split()[0]
            que_greet = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for but in range(int(msg_txt.split('-')[0]), int(msg_txt.split('-')[1]), 2):
                que_greet.row(str(but), str(but + 1))
            que_greet.row('Выбрать другой вопрос')

            que_list = get_que_list('list.txt', ran=msg_txt)

            bot.send_message(message.chat.id, f'Выбирай:\n{"".join(que_list)}',
                             reply_markup=que_greet)

        elif message.text.split()[0].isdigit():
            file_name = str(int(str(message.text).split()[0]))
            if len(message.text) in [1, 2]:
                # print(f'Хочу посмотреть на: {file_name}')
                try:
                    make_dir()
                    with open(f'questions/{file_name}.txt', 'r', encoding='UTF-8') as opened_file:
                        answer_text = opened_file.read()
                        debug_msg = f'User @{message.from_user.username} read answer {file_name}.'
                except Exception as exc:
                    answer_text = f'Что-то пошло не так :(\nВозможно, вопрос {file_name} ещё не ' \
                                  f'добавили.'
                    debug_msg = f'User @{message.from_user.username} try to read answer' \
                                f' {file_name} but failed.\n{type(exc)}\n{exc}'

            elif len(message.text) > 50:
                # print(f'Хочу записать: {file_name}')
                try:
                    make_dir()
                    with open(f'questions/{file_name}.txt', 'w', encoding='utf-8') as opened_file:
                        opened_file.write(f'{str(message.text)[2:].strip()}\n\nЭтот вопрос'
                                          f' обновлялся пользователем'
                                          f' @{message.from_user.username}')
                    answer_text = f'Вопрос {file_name} успешно записан!\n' \
                                  f'Не забудь проверить, корректно ли он записался :)'
                    debug_msg = f'User @{message.from_user.username} recorded answer {file_name}.'
                except Exception as exc:
                    debug_msg = f'{type(exc)}\n{exc}\nExcept from @{message.from_user.username}\n' \
                                f'{type(exc)}\n{exc}'
                    answer_text = f'Что-то пошло не так :(\n' \
                                  f'Возможно, ты указал(а) недопустимые символы.'
            else:
                answer_text = f'Что-то пошло не так :('
                debug_msg = f'Message: {message.text}\nFrom user: @{message.from_user.username}\n' \
                            f'Some troubles with that.'

            try:
                bot.send_message(message.chat.id, answer_text)
            except telebot.apihelper.ApiTelegramException:
                send_long_msg_len(user_id=message.chat.id, message=answer_text, reply=False)
                debug_msg += '\nLong message :('
                print('Detected')

            debug_write(debug_msg)

        else:
            answer_text = f'Что-то пошло не так :(\n' \
                          f'Если ты записывал(а) вопрос, то он, должно быть, не вместился в одно' \
                          f' сообщение. Отправь мне файл НОМЕР_ВОПРОСА.txt в кодировке UTF-8 и я' \
                          f' запишу ответ полностью)'
            debug_text = f'Message: {message.text}\nFrom user: @{message.from_user.username}\n' \
                         f'Some troubles with that - maybe message is too long.'
            debug_write(debug_text)
            bot.send_message(message.chat.id, answer_text)

    else:
        answer_text = f'Кажется, тебя всё ещё нет в списке 😎'
        debug_text = f'User @{message.from_user.username} / {message.from_user.id} is trying to' \
                     f' use without access!'
        debug_write(debug_text)
        bot.send_message(message.chat.id, answer_text)


@bot.message_handler(content_types=['document'])
def send_text(message):
    print(message.document.file_name)

    msg_doc_name_list = message.document.file_name.split('.')

    if msg_doc_name_list[1] == 'txt' and msg_doc_name_list[0].isdigit():
        file_name = message.document.file_name
        file_id_info = bot.get_file(message.document.file_id)

        make_dir()

        try:

            downloaded_file = bot.download_file(file_id_info.file_path)
            # print(downloaded_file)
            with open(f'questions/{file_name}', 'w', encoding='utf-8', errors='ignore') as new_file:
                text_to_write = downloaded_file.decode()
                text_to_write = text_to_write.replace('\r', '')
                new_file.write(f'{text_to_write}\n\nЭтот вопрос обновлялся '
                               f'пользователем @{message.from_user.username}')
            answer_text = f'Вопрос {file_name.split(".")[0]} успешно записан!\n' \
                          f'Не забудь проверить, корректно ли он записался :)'
            debug_msg = f'User @{message.from_user.username} recorded' \
                        f' answer {file_name.split(".")[0]}.'

            debug_write(debug_msg)
            bot.send_message(message.chat.id, answer_text)

        except UnicodeDecodeError:

            bot.send_message(message.chat.id, 'Измени кодировку на UTF-8 и попробуй ещё раз :)')

        except Exception as exc:

            debug_text = f'{type(exc)}\n{exc}\nAHTUNG!'

            debug_write(debug_text)
            bot.send_message(message.chat.id, 'У меня не получилось :(')

    elif message.from_user.id == 449808966:

        if message.document.file_name.split('.')[1] == 'zip':
            file_name = message.document.file_name
            file_id_info = bot.get_file(message.document.file_id)
            if file_name == 'questions.zip':
                try:
                    downloaded_file = bot.download_file(file_id_info.file_path)
                    with open(file_name, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    bot.send_message(449808966, 'File uploaded successfully!')
                    time.sleep(2)
                    with zipfile.ZipFile('questions.zip', 'r') as zip_file:
                        zip_file.extractall()
                    bot.send_message(449808966, 'File has been unzipped successfully!')
                except Exception as exc:
                    bot.send_message(449808966, f'Something is wrong. Maybe the old questions '
                                                f'are not deleted?\n{type(exc)}\n{exc}')

        elif message.document.file_name.split('.')[0] == 'list':
            file_id_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
            try:
                downloaded_file = bot.download_file(file_id_info.file_path)
                with open(file_name, 'wb') as new_file:
                    new_file.write(downloaded_file)
                bot.send_message(449808966, 'List-file uploaded successfully!')
                ans_list = get_que_list(file_name)
                ans = 'New list is:\n' + ''.join(ans_list)
                global greet_menu
                greet_menu = creating_a_keyboard(num_of_que=len(ans_list))
                send_long_msg(449808966, ans, reply=True)
            except Exception as exc:
                bot.send_message(449808966, f'Exception!\n{type(exc)}\n{exc}')

        elif message.document.file_name.split('.')[0] == 'users':
            file_id_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
            try:
                downloaded_file = bot.download_file(file_id_info.file_path)
                with open(file_name, 'wb') as new_file:
                    new_file.write(downloaded_file)
                ans = 'New user-list successfully uploaded!'
                send_long_msg(449808966, ans, reply=False)
            except Exception as exc:
                bot.send_message(449808966, f'Exception!\n{type(exc)}\n{exc}')

        else:
            bot.send_message(449808966, 'Unknown document type.')


while True:
    try:
        bot.polling(none_stop=True, interval=1)

    except Exception as Exc_txt:
        logging.error(str(Exc_txt))
        print('________________________EXCEPTION________________________')
        print(str(Exc_txt))
        bot.send_message(449808966, 'Exception detected!')
        bot.send_message(449808966, str(Exc_txt))
        time.sleep(5)

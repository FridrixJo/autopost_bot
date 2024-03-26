import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
import random
import string
from config import *
from key_boards import *
from FSMClasses import *
from aiogram import types
import re


from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from data_base.db_users import UsersDB
from data_base.db_stores import ShopsDB
from data_base.db_contacts import ContactsDB
from data_base.db_chats import ChatsDB


storage = MemoryStorage()

bot = Bot(TOKEN)

dispatcher = Dispatcher(bot=bot, storage=storage)

ADMIN_IDS = [int(ADMIN_ID)]


users_db = UsersDB('data_base/autopost.db')
shops_db = ShopsDB('data_base/autopost.db')
contacts_db = ContactsDB('data_base/autopost.db')
chats_db = ChatsDB('data_base/autopost.db')


BACK_BTN = types.InlineKeyboardButton('Назад ↩️', callback_data='back')


async def clear_state(state: FSMContext):
    try:
        current_state = state.get_state()
        if current_state is not None:
            await state.finish()
    except Exception as error:
        print(error)


def check(url):
    reg = r'http'
    x = re.match(pattern=reg, string=url)
    if x is not None:
        return True
    else:
        return False


def get_name(message: types.Message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    name = ''
    if first_name is not None:
        name += first_name
        name += ' '
    if last_name is not None:
        name += last_name
        name += ' '
    if username is not None:
        name += '@'
        name += username

    return name


async def send_menu(message: types.Message):
    text = 'Главное меню'
    await bot.send_message(message.chat.id, text=text, reply_markup=inline_markup_menu())


async def edit_to_menu(message: types.Message):
    text = 'Главное меню'
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=inline_markup_menu())


async def send_moderator_menu(message: types.Message):
    text = 'Главное меню модератора'
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=inline_markup_moderator_menu())


async def edit_to_moderator_menu(message: types.Message):
    text = 'Главное меню модератора'
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, reply_markup=inline_markup_moderator_menu())


@dispatcher.message_handler(Text(equals='отмена', ignore_case=True), state=[FSMUser.add_shop, FSMUser.picture, FSMUser.edit_shop_param, FSMUser.edit_contact_param, FSMUser.add_contact, FSMUser.minutes])
async def cancel_handler(message: types.Message, state: FSMContext):
    await clear_state(state)
    await bot.send_message(message.chat.id, 'Действие отменено', reply_markup=types.ReplyKeyboardRemove())
    await send_menu(message)


def get_text(user_id: int):
    text = 'Выберите магазины для автопостинга (нужно просто нажать на магазин и он будет добавлен ✅ либо убран ❌ из списка автопостинга)' + '\n\n'
    text += 'После того, как выбрали магазины для атопостинга, нажмите на "Начать размещение"' + '\n\n'
    text += f'Количество выбранных магазинов на данный момент {len(shops_db.get_all_tagged_shops_by(user_id, "user_id"))}' + '\n\n'

    return text


@dispatcher.message_handler(commands=['start'], state=["*"])
async def start(message: types.Message, state: FSMContext):
    if not users_db.user_exists(message.chat.id):
        message_text = "Введите пароль, чтобы использовать бота"
        await bot.send_message(message.chat.id, text=message_text, reply_markup=reply_markup_call_off("Отмена"))
        await FSMUser.input_password.set()
    else:
        await send_menu(message)


@dispatcher.message_handler(content_types=['text'], state=FSMUser.input_password)
async def input_password(message: types.Message, state: FSMContext):
    if message.text == PASSWORD:
        users_db.add_user(message.chat.id, get_name(message))
        users_db.set_minutes(message.chat.id, minutes=15)
        users_db.set_active(message.chat.id, active=0)

        text = f'Пользователь {str(users_db.get_name(message.chat.id))} перешел в бота'
        for i in ADMIN_IDS:
            await bot.send_message(chat_id=i, text=text)

        await bot.send_message(message.chat.id, 'Вы авторизованы', reply_markup=types.ReplyKeyboardRemove())
        await send_menu(message)
        await clear_state(state)
    else:
        message_text = "Неверный пароль, введите еще раз"
        await bot.send_message(message.chat.id, text=message_text, reply_markup=reply_markup_call_off("Отмена"))


@dispatcher.message_handler(commands=['moderator'], state=['*'])
async def start_moderator(message: types.Message, state: FSMContext):
    for i in ADMIN_IDS:
        if message.chat.id == i:
            await clear_state(state)
            await send_moderator_menu(message)
            await FSMAdmin.moderator_opps.set()


@dispatcher.callback_query_handler(state=FSMAdmin.moderator_opps)
async def start_moderator(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'main_menu':
        await clear_state(state)
        await edit_to_menu(call.message)
    elif call.data == 'back':
        await edit_to_moderator_menu(call.message)
        await FSMAdmin.moderator_opps.set()
    elif call.data == 'active_status':
        text = 'Choose active status'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_active_status().add(BACK_BTN))
        await FSMAdmin.active.set()
    elif call.data == 'statistics':
        text = '<b>Users statistics:</b>' + '\n\n'
        text += f'Users: <b>{len(users_db.get_users())}</b>' + '\n'
        text += f'Active: <b>{len(users_db.get_active_status_all(active=1))}</b>'

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_back('Back'), parse_mode='HTML')


@dispatcher.callback_query_handler(state=FSMAdmin.active)
async def get_status(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await clear_state(state)
        await edit_to_moderator_menu(call.message)
        await FSMAdmin.moderator_opps.set()
    elif call.data == 'true':
        users_db.set_active_all(1)
        await clear_state(state)
        await edit_to_moderator_menu(call.message)
        await FSMAdmin.moderator_opps.set()
    elif call.data == 'false':
        users_db.set_active_all(0)
        await clear_state(state)
        await edit_to_moderator_menu(call.message)
        await FSMAdmin.moderator_opps.set()


@dispatcher.message_handler(content_types=[ContentType.NEW_CHAT_MEMBERS])
async def get_chat(message: types.Message):
    print("start")
    print(message.__dict__)
    if users_db.user_exists(message.chat.id):
        print("here")
        user_id = message.from_user.id
        chat_id = message.chat.id
        print("HELLO")
        print(f"add new chat {users_db.get_name(user_id=user_id)}, {chat_id}")
        if not chats_db.chat_exists(user_id, chat_id):
            chats_db.add_chat(user_id, str(chat_id))


@dispatcher.message_handler(content_types=[ContentType.LEFT_CHAT_MEMBER])
async def get_chat(message: types.Message):
    print(message.__dict__)
    if users_db.user_exists(message.chat.id):
        user_id = message.from_user.id
        chat_id = message.chat.id
        print(f"remove chat {users_db.get_name(user_id=user_id)}, {chat_id}")
        if chats_db.chat_exists(user_id=user_id, chat_id=chat_id):
            chats_db.delete_chat(user_id=user_id, chat_id=str(chat_id))


@dispatcher.callback_query_handler()
async def get_callback_menu(call: types.CallbackQuery):
    if call.data == 'shops':
        shops = shops_db.get_all_shops_by(param=call.message.chat.id, sql_param='user_id')
        text: str = 'Магазины'
        if len(shops):
            text = 'Выберите любой магазин для его редактирования либо добавьте новый'
        else:
            text = 'Добавьте новый магазин'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_shop_list(call.message.chat.id, shops_db).add(BACK_BTN))
        await FSMUser.shop.set()
    elif call.data == 'auto_post':
        text = f'Ваш интервал: {users_db.get_minutes(user_id=call.message.chat.id)}' + '\n'
        print(users_db.get_minutes(user_id=call.message.chat.id))
        text += 'Для изменения введите количесто минут между постами (от 15 до 180)'
        await bot.send_message(call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.minutes.set()
    elif call.data == 'shows':
        text = get_text(call.message.chat.id)
        if users_db.get_active(call.message.chat.id) == 1:
            text += '<i>Показы на данный момент запущены</i>'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_tagged_shops_suspend(call.message.chat.id, shops_db).add(BACK_BTN), parse_mode='HTML')
        else:
            text += '<i>Показы на данный момент остановлены</i>'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_tagged_shops(call.message.chat.id, shops_db).add(BACK_BTN), parse_mode='HTML')
        await FSMUser.shows.set()


@dispatcher.callback_query_handler(state=FSMUser.shop)
async def choose_shop(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await clear_state(state)
        await edit_to_menu(call.message)
    else:
        if call.data == 'add_shop':
            async with state.proxy() as file:
                file['status'] = 'name'
            text = 'Введите имя магазина'
            await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_shop.set()
        else:
            for i in shops_db.get_all_shops_by(param=call.message.chat.id, sql_param='user_id'):
                if call.data == i[0]:

                    shop_id = shops_db.get_shop_id(user_id=call.message.chat.id, name=call.data)

                    async with state.proxy() as file:
                        file['shop_id'] = shop_id

                    text = f'Название магазина: <b>{shops_db.get_shop_name(shop_id)}</b>' + '\n\n'
                    text += f'Описание магазина: <i>{shops_db.get_shop_description(shop_id)}</i>' + '\n\n'
                    text += 'Выберите из предложенного'
                    photo = shops_db.get_shop_picture(shop_id)

                    pic_type = shops_db.get_shop_pic_type(shop_id)

                    if pic_type == 'gif':
                        await bot.send_animation(chat_id=call.message.chat.id, animation=photo, caption=text, reply_markup=inline_markup_shop_opportunities(), parse_mode='HTML')
                    elif pic_type == 'photo':
                        await bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption=text, reply_markup=inline_markup_shop_opportunities(), parse_mode='HTML')

                    await FSMUser.shop_opps.set()


@dispatcher.message_handler(content_types=['text'], state=FSMUser.add_shop)
async def add_shop(message: types.Message, state: FSMContext):
    async with state.proxy() as file:
        status = file['status']

    if status == 'name':
        if len(message.text) <= 25:
            async with state.proxy() as file:
                file['name'] = message.text
                file['status'] = 'description'

            text = 'Введите описание магазина'
            await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_shop.set()
        else:
            text = 'Максимальная длинна имени составляет 25 символов, введите имя магазина еще раз'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_shop.set()
    elif status == 'description':
        async with state.proxy() as file:
            file['description'] = message.text
            file['status'] = 'pic_type'
            file['step'] = 'creating'

        await bot.send_message(message.chat.id, text='Принято', reply_markup=types.ReplyKeyboardRemove())

        text = 'Выберите тип картинки для магазина'
        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=inline_markup_pic_type())
        await FSMUser.pic_type.set()


@dispatcher.callback_query_handler(state=FSMUser.pic_type)
async def get_pic_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as file:
        file['pic_type'] = call.data

    text: str = ''
    if call.data == 'gif':
        text = 'Отправьте GIF' + '\n\n'
    elif call.data == 'photo':
        text = 'Отправьте фото' + '\n\n'

    await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
    await FSMUser.picture.set()


@dispatcher.message_handler(content_types=['photo', 'animation'], state=FSMUser.picture)
async def get_picture(message: types.Message, state: FSMContext):
    async with state.proxy() as file:
        pic_type = file['pic_type']

    if (pic_type == 'gif' and message.content_type == 'animation') or (pic_type == 'photo' and message.content_type == 'photo'):
        async with state.proxy() as file:
            step = file['step']

        file_id: str = ''

        if pic_type == 'gif':
            file_id += message.animation.file_id
        elif pic_type == 'photo':
            file_id += message.photo[-1].file_id

        text = ''

        if step == 'creating':
            async with state.proxy() as file:
                name = file['name']
                description = file['description']
            if not shops_db.shop_exists(message.chat.id, name):
                shop_id = ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(random.randrange(12, 16)))
                shops_db.add_shop(
                    user_id=message.chat.id,
                    shop_id=shop_id,
                    name=name,
                    description=description,
                    pic_type=pic_type,
                    picture=file_id
                )
                shops_db.edit_shop_tagged(shop_id, 0)
                text += 'Магазин успешно добавлен ✅' + '\n\n'
                text += 'Для добавления контактов к магазину нажми на кнопку "Магазины" ниже ⬇' + '\n'
                text += 'Вам откроется список всех ваших магазинов. И после нажатия на любой созданный магазин вы сможете добавить / отредактировать его контакты'
            else:
                text += 'Магазин с таким названием у вас уже существует'
        elif step == 'editing':
            async with state.proxy() as file:
                shop_id = file['shop_id']

            shops_db.edit_shop_pic_type(shop_id, pic_type)
            shops_db.edit_shop_picture(shop_id, file_id)

            text = 'Картинка магазина успешно отредактирована'

        await clear_state(state)
        await bot.send_message(message.chat.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        await send_menu(message)
    else:
        text: str = ''
        if pic_type == 'gif':
            text = 'Вы отправили обычное фото. Отправьте GIF'
        else:
            text = 'Вы отправили GIF. Отправьте обычное фото'

        await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.picture.set()


@dispatcher.callback_query_handler(state=FSMUser.shop_opps)
async def get_shop_opp(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await clear_state(state)
        await send_menu(call.message)
    elif call.data == 'edit_shop':
        text = 'Выберите, что хотите отредактировать ...'
        await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=inline_markup_edit_shop())
        await FSMUser.edit_shop.set()
    elif call.data == 'delete':
        async with state.proxy() as file:
            file['delete'] = 'shop'
        text = 'Вы действительно хотите удалить данный магазин?'
        await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=inline_markup_yes_no())
        await FSMUser.delete.set()
    elif call.data == 'contacts':
        async with state.proxy() as file:
            shop_id = file['shop_id']

        pic_type = shops_db.get_shop_pic_type(shop_id)
        photo = shops_db.get_shop_picture(shop_id)
        shop_name = shops_db.get_shop_name(shop_id)
        description = shops_db.get_shop_description(shop_id)

        text = f'<b>{shop_name}</b>' + '\n\n'
        text += f'{description}' + '\n\n'
        text += 'Контакты:'

        try:
            if pic_type == 'gif':
                await bot.send_animation(chat_id=call.message.chat.id, animation=photo, caption=text, reply_markup=inline_markup_contacts_list_urls(shop_id, contacts_db), parse_mode='HTML')
            elif pic_type == 'photo':
                await bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption=text, reply_markup=inline_markup_contacts_list_urls(shop_id, contacts_db), parse_mode='HTML')

            text = '⬆Выше представлен пример, как будут отображаться контакты магазина вместе с картинкой и описанием' + '\n\n'
        except Exception as e:
            print(e)
            text = ''

        text += 'Выберите любой контакт для его редактирования либо добавьте новый'
        await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=inline_markup_contacts_list(shop_id=shop_id, db=contacts_db).add(BACK_BTN))
        await FSMUser.contact.set()


@dispatcher.callback_query_handler(state=FSMUser.delete)
async def delete_shop_opps(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        async with state.proxy() as file:
            shop_id = file['shop_id']
            delete = file['delete']

        if delete == 'shop':
            shops_db.delete_shop(shop_id)
        elif delete == 'contact':
            async with state.proxy() as file:
                name = file['name']
            print(shop_id, name)

            contacts_db.delete_contact(shop_id, name)

        await clear_state(state)
        await edit_to_menu(call.message)
    elif call.data == 'no':
        await clear_state(state)
        await edit_to_menu(call.message)


@dispatcher.callback_query_handler(state=FSMUser.contact)
async def get_contact(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        shops = shops_db.get_all_shops_by(param=call.message.chat.id, sql_param='user_id')
        text: str = ''
        if len(shops):
            text += 'Выберите любой магазин для его редактирования либо добавьте новый'
        else:
            text += 'Добавьте новый магазин'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_shop_list(call.message.chat.id, shops_db).add(BACK_BTN))
        await clear_state(state)
        await FSMUser.shop.set()
    else:
        if call.data == 'add_contact':
            async with state.proxy() as file:
                file['status'] = 'name'

            text = 'Введите имя контакта'
            await bot.send_message(call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_contact.set()
        else:
            async with state.proxy() as file:
                shop_id = file['shop_id']

            for i in contacts_db.get_contacts_by(param=shop_id, sql_param='shop_id'):
                if call.data == i[0]:

                    async with state.proxy() as file:
                        file['name'] = call.data

                    text = f'Название данного контакта: <b>{contacts_db.get_contact_name(shop_id, call.data)}</b>' + '\n\n'
                    text += f'Ссылка контакта: <i>{contacts_db.get_contact_link(shop_id, call.data)}</i>' + '\n\n'

                    text += 'Выберите, что хотите сделать с данным контактом'
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_contact_opportunities(), parse_mode='HTML')
                    await FSMUser.contact_opps.set()


@dispatcher.callback_query_handler(state=FSMUser.contact_opps)
async def get_contact_opp(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        async with state.proxy() as file:
            shop_id = file['shop_id']

        text = 'Выберите любой контакт для его редактирования либо добавьте новый'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_contacts_list(shop_id=shop_id, db=contacts_db).add(BACK_BTN))
        await FSMUser.contact.set()
    elif call.data == 'edit_contact':
        text = 'Выберите, что хотите отредактировать ...'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_edit_contact())
        await FSMUser.edit_contact.set()
    elif call.data == 'delete':
        async with state.proxy() as file:
            file['delete'] = 'contact'

        text = 'Вы действительно хотите удалить данный контакт?'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_yes_no())
        await FSMUser.delete.set()


@dispatcher.callback_query_handler(state=FSMUser.edit_shop)
async def edit_shop(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await clear_state(state)
        await edit_to_menu(call.message)
    elif call.data == 'edit_shop_name':
        async with state.proxy() as file:
            file['shop_edit'] = 'name'
        text = 'Введите новое название для магазина'
        await bot.send_message(call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.edit_shop_param.set()
    elif call.data == 'edit_shop_description':
        async with state.proxy() as file:
            file['shop_edit'] = 'description'
        text = 'Введите новое описание для магазина'
        await bot.send_message(call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.edit_shop_param.set()
    elif call.data == 'edit_shop_photo':
        async with state.proxy() as file:
            file['step'] = 'editing'

        text = 'Выберите тип картинки для магазина'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_pic_type())
        await FSMUser.pic_type.set()


@dispatcher.message_handler(content_types=['text'], state=FSMUser.edit_shop_param)
async def edit_shop_param(message: types.Message, state: FSMContext):
    async with state.proxy() as file:
        shop_edit = file['shop_edit']
        shop_id = file['shop_id']

    print(shop_id, shop_edit)

    if shop_edit == 'name':
        if len(message.text) <= 25:
            shops_db.edit_shop_name(shop_id=shop_id, shop_name=message.text)
            text = 'Успешно изменено'
            await bot.send_message(message.chat.id, text=text, reply_markup=types.ReplyKeyboardRemove())
            await clear_state(state)
            await send_menu(message)
        else:
            text = 'Максимальная длинна имени составляет 25 символов, введите название магазина еще раз'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.edit_shop_param.set()
    elif shop_edit == 'description':
        shops_db.edit_shop_description(shop_id, message.text)
        text = 'Успешно изменено'
        await bot.send_message(message.chat.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        await clear_state(state)
        await send_menu(message)




@dispatcher.callback_query_handler(state=FSMUser.edit_contact)
async def edit_contact(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        shops = shops_db.get_all_shops_by(param=call.message.chat.id, sql_param='user_id')
        text: str = ''
        if len(shops):
            text += 'Выберите любой магазин для его редактирования либо добавьте новый'
        else:
            text += 'Добавьте новый магазин'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_shop_list(call.message.chat.id, shops_db).add(BACK_BTN))
        await clear_state(state)
        await FSMUser.shop.set()
    elif call.data == 'edit_contact_name':
        async with state.proxy() as file:
            file['contact_edit'] = 'name'
        text = 'Введите новое название контакта'
        await bot.send_message(call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.edit_contact_param.set()
    elif call.data == 'edit_contact_link':
        async with state.proxy() as file:
            file['contact_edit'] = 'link'
        text = 'Введите новую ссылку контакта'
        await bot.send_message(call.message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.edit_contact_param.set()


@dispatcher.message_handler(content_types=['text'], state=FSMUser.edit_contact_param)
async def edit_shop_param(message: types.Message, state: FSMContext):
    async with state.proxy() as file:
        contact_edit = file['contact_edit']
        shop_id = file['shop_id']
        name = file['name']

    if contact_edit == 'name':
        if len(message.text) <= 25:
            contacts_db.edit_contact_name(shop_id=shop_id, name=name, new_name=message.text)
            text = 'Успешно изменено'
            await bot.send_message(message.chat.id, text=text, reply_markup=types.ReplyKeyboardRemove())
            await clear_state(state)
            await send_menu(message)
        else:
            text = 'Максимальная длинна имени составляет 25 символов, введите имя контакта еще раз'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.edit_contact_param.set()
    elif contact_edit == 'link':
        if check(message.text) is True:
            contacts_db.edit_contact_link(shop_id=shop_id, name=name, link=message.text)
            text = 'Успешно изменено'
            await bot.send_message(message.chat.id, text=text, reply_markup=types.ReplyKeyboardRemove())
            await clear_state(state)
            await send_menu(message)
        else:
            text = 'Cсылка некорректна. Введите новую ссылку контакта еще раз'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.edit_contact_param.set()


@dispatcher.message_handler(state=FSMUser.minutes)
async def get_minutes(message: types.Message, state: FSMContext):
    try:
        a = int(message.text)
        if a < 15 or a > 180:
            text = 'Введите число от 15 до 180'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.minutes.set()
        else:
            users_db.set_minutes(message.chat.id, a)
            text = 'Успешно установлено'
            await bot.send_message(message.chat.id, text=text, reply_markup=types.ReplyKeyboardRemove())
            await clear_state(state)
            await send_menu(message)
    except Exception as e:
        text = 'Введите число от 15 до 180'
        await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
        await FSMUser.minutes.set()


@dispatcher.callback_query_handler(state=FSMUser.shows)
async def get_shows(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await clear_state(state)
        await edit_to_menu(call.message)
    elif call.data == 'suspend':
        if users_db.get_active(call.message.chat.id) == 1:
            users_db.set_active(call.message.chat.id, 0)
            text = get_text(call.message.chat.id)
            text += '<i>Показы на данный момент остановлены</i>'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_tagged_shops(call.message.chat.id, shops_db).add(BACK_BTN), parse_mode='HTML')

    elif call.data == 'run':
        if users_db.get_active(call.message.chat.id) == 0:

            text = get_text(call.message.chat.id)
            text += '<i>Показы на данный момент запущены</i>'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_tagged_shops_suspend(call.message.chat.id, shops_db).add(BACK_BTN), parse_mode='HTML')

            users_db.set_active(user_id=call.message.chat.id, active=1)

            print("hello")

            while True:
                if users_db.get_active(call.message.chat.id) == 1:
                    for j in shops_db.get_all_shops_by(call.message.chat.id, 'user_id'):
                        print(j)
                        print("suck")
                        shop_id = shops_db.get_shop_id(call.message.chat.id, name=j[0])
                        if shops_db.get_shop_tagged(shop_id) == 1:
                            if users_db.get_active(call.message.chat.id) == 1:
                                for i in chats_db.get_chats_by_user(call.message.chat.id):
                                    if users_db.get_active(call.message.chat.id) == 1:
                                        print(i)
                                        pic_type = shops_db.get_shop_pic_type(shop_id)
                                        photo = shops_db.get_shop_picture(shop_id)
                                        shop_name = shops_db.get_shop_name(shop_id)
                                        description = shops_db.get_shop_description(shop_id)

                                        text = f'<b>{shop_name}</b>' + '\n\n'
                                        text += f'{description}' + '\n\n'
                                        text += 'Контакты:'

                                        print("send message aye")
                                        try:
                                            if pic_type == 'gif':
                                                message = await bot.send_animation(chat_id=int(i[0]), animation=photo, caption=text, reply_markup=inline_markup_contacts_list_urls(shop_id, contacts_db), parse_mode='HTML')
                                                print("cooool")
                                                try:
                                                    pin_message = await bot.pin_chat_message(chat_id=int(i[0]), message_id=message.message_id, disable_notification=True)
                                                except Exception as e:
                                                   print(e)

                                            elif pic_type == 'photo':
                                                message = await bot.send_photo(chat_id=int(i[0]), photo=photo, caption=text, reply_markup=inline_markup_contacts_list_urls(shop_id, contacts_db), parse_mode='HTML')
                                                print("cooool")
                                                try:
                                                    await bot.pin_chat_message(chat_id=int(i[0]), message_id=message.message_id, disable_notification=True)
                                                except Exception as e:
                                                    print(e)
                                        except Exception as e:
                                            print(e)
                                    else:
                                        print("break1")
                                        break
                                print("sleep")
                                await asyncio.sleep(int(users_db.get_minutes(call.message.chat.id)) * 60)
                            else:
                                print("break2")

                                break
                        else:
                            print("break do not have active shops")
                            break
                else:
                    print("break3")

                    break
    else:
        print("break3")

        for i in shops_db.get_all_shops_by(call.message.chat.id, 'user_id'):
            if call.data == str(i[0]):
                shop_id = shops_db.get_shop_id(call.message.chat.id, str(i[0]))
                tagged = shops_db.get_shop_tagged(shop_id)
                if tagged == 1:
                    shops_db.edit_shop_tagged(shop_id, 0)
                elif tagged == 0:
                    shops_db.edit_shop_tagged(shop_id, 1)

                text = get_text(call.message.chat.id)

                if users_db.get_active(call.message.chat.id) == 1:
                    text += '<i>Показы на данный момент запущены</i>'
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_tagged_shops_suspend(call.message.chat.id, shops_db).add(BACK_BTN), parse_mode='HTML')
                else:
                    text += '<i>Показы на данный момент остановлены</i>'
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup_tagged_shops(call.message.chat.id, shops_db).add(BACK_BTN), parse_mode='HTML')


@dispatcher.message_handler(content_types=['text'], state=FSMUser.add_contact)
async def add_shop(message: types.Message, state: FSMContext):
    async with state.proxy() as file:
        status = file['status']

    if status == 'name':
        if len(message.text) <= 25:
            async with state.proxy() as file:
                file['contact_name'] = message.text
                file['status'] = 'link'

            text = 'Введите ссылку контакта'
            await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_contact.set()
        else:
            text = 'Максимальная длинна имени составляет 25 символов, введите имя контакта еще раз'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_contact.set()
    elif status == 'link':
        async with state.proxy() as file:
            contact_name = file['contact_name']
            shop_id = file['shop_id']

        if check(message.text) is True:
            contacts_db.add_contact(
                shop_id=shop_id,
                name=contact_name,
                link=message.text
            )

            await bot.send_message(message.chat.id, text='Контакт успешно добавлен', reply_markup=types.ReplyKeyboardRemove())

            await clear_state(state)
            await send_menu(message)
        else:
            text = 'Ссылка некорректна. Введите ссылку контакта еще раз'
            await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup_call_off('Отмена'))
            await FSMUser.add_contact.set()


try:
    asyncio.run(executor.start_polling(dispatcher=dispatcher, skip_updates=False))
except Exception as error:
    print(error)




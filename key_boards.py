from aiogram import types
from data_base.db_stores import ShopsDB
from data_base.db_contacts import ContactsDB


def inline_markup_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('Магазины', callback_data='shops')
    btn2 = types.InlineKeyboardButton('Настроить автопостинг рекламы', callback_data='auto_post')
    btn3 = types.InlineKeyboardButton('Показы в чате', callback_data='shows')

    kb.add(btn1, btn2, btn3)

    return kb


def reply_markup_call_off(text):
    kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton(text=text)

    kb.add(btn1)

    return kb


def inline_markup_back(text):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text + ' ↩️', callback_data='back')

    kb.add(btn1)

    return kb


def inline_markup_shop_list(user_id, db: ShopsDB):
    kb = types.InlineKeyboardMarkup(row_width=1)

    for i in db.get_all_shops_by(param=user_id, sql_param='user_id'):
        btn = types.InlineKeyboardButton(text=str(i[0]), callback_data=str(i[0]))
        kb.add(btn)

    btn = types.InlineKeyboardButton(text='Добавить магазин', callback_data='add_shop')
    kb.add(btn)

    return kb


def inline_markup_contacts_list(shop_id, db: ContactsDB):
    kb = types.InlineKeyboardMarkup(row_width=1)

    for i in db.get_contacts_by(param=shop_id, sql_param='shop_id'):
        btn = types.InlineKeyboardButton(text=str(i[0]), callback_data=str(i[0]))
        kb.add(btn)

    btn = types.InlineKeyboardButton(text='Добавить контакт', callback_data='add_contact')
    kb.add(btn)

    return kb


def inline_markup_contacts_list_urls(shop_id, db: ContactsDB):
    kb = types.InlineKeyboardMarkup(row_width=1)

    for i in db.get_contacts_by(param=shop_id, sql_param='shop_id'):
        try:
            url = db.get_contact_link(shop_id, name=str(i[0]))
            btn = types.InlineKeyboardButton(text=str(i[0]), url=url)
            kb.add(btn)
        except Exception as e:
            print(e)

    return kb


def inline_markup_pic_type():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('GIF', callback_data='gif')
    btn2 = types.InlineKeyboardButton('Фото', callback_data='photo')

    kb.add(btn1, btn2)

    return kb


def inline_markup_shop_opportunities():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('Редактировать магазин', callback_data='edit_shop')
    btn2 = types.InlineKeyboardButton('Контакты 👥', callback_data='contacts')
    btn3 = types.InlineKeyboardButton('Удалить магазин', callback_data='delete')
    btn4 = types.InlineKeyboardButton('Назад ↩️', callback_data='back')

    kb.add(btn1, btn2, btn3, btn4)

    return kb


def inline_markup_edit_shop():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('Редактировать название', callback_data='edit_shop_name')
    btn2 = types.InlineKeyboardButton('Редактировать описание', callback_data='edit_shop_description')
    btn3 = types.InlineKeyboardButton('Редактировать картинку', callback_data='edit_shop_photo')
    btn4 = types.InlineKeyboardButton('Назад ↩️', callback_data='back')

    kb.add(btn1, btn2, btn3, btn4)

    return kb


def inline_markup_contact_opportunities():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('Редактировать контакт', callback_data='edit_contact')
    btn2 = types.InlineKeyboardButton('Удалить', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Назад ↩️', callback_data='back')

    kb.add(btn1, btn2, btn3)

    return kb


def inline_markup_edit_contact():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('Редактировать название', callback_data='edit_contact_name')
    btn2 = types.InlineKeyboardButton('Редактировать ссылку', callback_data='edit_contact_link')
    btn3 = types.InlineKeyboardButton('Назад ↩️', callback_data='back')

    kb.add(btn1, btn2, btn3)

    return kb


def inline_markup_yes_no():
    kb = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton('Да, убрать ❌', callback_data='yes')
    btn2 = types.InlineKeyboardButton('Нет, оставить 😉', callback_data='no')

    kb.add(btn1, btn2)

    return kb


def inline_markup_main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn1 = types.InlineKeyboardButton('На главное меню', callback_data='main_menu')

    kb.add(btn1)

    return kb




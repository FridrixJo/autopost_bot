from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMUser(StatesGroup):
    input_password = State()
    add_shop = State()
    add_contact = State()
    pic_type = State()
    picture = State()

    shop = State()
    shop_opps = State()
    edit_shop = State()
    edit_shop_param = State()

    contact = State()
    contact_opps = State()
    edit_contact = State()
    edit_contact_param = State()

    delete = State()
    minutes = State()
    chat = State()

    shows = State()


class FSMAdmin(StatesGroup):
    moderator_opps = State()
    active = State()


class FSMReply(StatesGroup):
    pass

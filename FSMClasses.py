from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMUser(StatesGroup):
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
    pass


class FSMReply(StatesGroup):
    pass

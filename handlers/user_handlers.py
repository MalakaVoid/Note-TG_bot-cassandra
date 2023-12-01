from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart, Command
from mongo_db_op import database_operations
from keyboards import user_keyboards
import datetime


router = Router()


class AddNote(StatesGroup):
    get_title = State()
    get_text = State()


class EditNote(StatesGroup):
    get_edit_text = State()
    get_edit_title = State()


class SearchNote(StatesGroup):
    get_search_text = State()


class AddUser(StatesGroup):
    get_username = State()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    status_code_auth = database_operations.authorize_user(message.from_user.username)
    if status_code_auth == 404:
        database_operations.registrate_user(message.from_user.username,
                                            message.from_user.first_name,
                                            message.from_user.last_name)
    await message.answer(text="Hi. Choose your note or add one.",
                         reply_markup=user_keyboards.get_notes_kb(message.from_user.username))


@router.callback_query(F.data == 'add_note_btn')
async def add_note_cb(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Enter note title.")
    await state.set_state(AddNote.get_title)


@router.message(AddNote.get_title)
async def get_title_add_note(message: Message, state: FSMContext) -> None:
    await state.set_state(AddNote.get_text)
    await state.set_data({"title": message.text})
    await message.answer(text="Enter note text.")


@router.message(AddNote.get_text)
async def add_note_completion(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    database_operations.add_note(message.from_user.username,
                                 data['title'],
                                 message.text)
    await state.clear()
    await message.answer("Note successfully added\nChoose your note or add one.",
                         reply_markup=user_keyboards.get_notes_kb(message.from_user.username))


@router.callback_query(F.data.startswith("note:"))
async def go_to_note(callback: CallbackQuery, state: FSMContext):
    note = database_operations.get_note_by_id(callback.data.split(" ")[1])
    message_text = (f"<b>{note.title}</b>\n"
                    f"{note.text}")
    await callback.message.edit_text(message_text,
                                     reply_markup=user_keyboards.get_note_operations_kb(note.note_id),
                                     parse_mode="HTML")


@router.callback_query(F.data == "back_from_note")
async def back_to_notes_btn(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text="Choose your note or add one.",
                                     reply_markup=user_keyboards.get_notes_kb(callback.message.chat.username))


@router.callback_query(F.data.startswith("edit_note:"))
async def edit_note_btn(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=user_keyboards.get_edit_note_kb(callback.data.split(" ")[1]))


@router.callback_query(F.data.startswith('back_from_note_edit:'))
async def back_from_note_edit_btn(callback: CallbackQuery):
    note = database_operations.get_note_by_id(callback.data.split(" ")[1])
    message_text = (f"<b>{note.title}</b>\n"
                    f"{note.text}")
    await callback.message.edit_text(message_text,
                                     reply_markup=user_keyboards.get_note_operations_kb(note.note_id),
                                     parse_mode="HTML")


@router.callback_query(F.data.startswith("edit_note_title:"))
async def edit_note_title_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditNote.get_edit_title)
    await state.set_data({"note_id": callback.data.split(" ")[1]})
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="Enter a new title.")


@router.message(EditNote.get_edit_title)
async def get_edited_title(message: Message, state: FSMContext):
    note_data = await state.get_data()
    database_operations.update_note(note_data['note_id'], message.text, message.from_user.username, True)

    note = database_operations.get_note_by_id(note_data['note_id'])
    message_text = (f"<b>{note.title}</b>\n"
                    f"{note.text}")
    await message.answer(message_text,
                         reply_markup=user_keyboards.get_note_operations_kb(note.note_id),
                         parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data.startswith("edit_note_text:"))
async def edit_note_text_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditNote.get_edit_text)
    await state.set_data({"note_id": callback.data.split(" ")[1]})
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="Enter a new text.")


@router.message(EditNote.get_edit_text)
async def get_edited_text(message: Message, state: FSMContext):
    note_data = await state.get_data()
    database_operations.update_note_text(note_data['note_id'], message.text, message.from_user.username)

    note = database_operations.get_note_by_id(note_data['note_id'])
    message_text = (f"<b>{note.title}</b>\n"
                    f"{note.text}")
    await message.answer(message_text,
                         reply_markup=user_keyboards.get_note_operations_kb(note.note_id),
                         parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data.startswith("delete_note:"))
async def delete_note_btn(callback: CallbackQuery):
    database_operations.delete_note(callback.data.split(" ")[1])
    await callback.message.edit_text(text="Choose your note or add one.",
                                     reply_markup=user_keyboards.get_notes_kb(callback.message.chat.username))


@router.callback_query(F.data == 'search_note_btn')
async def search_btn(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Enter text to search.",
                                     reply_markup=None)
    await state.set_state(SearchNote.get_search_text)


@router.message(SearchNote.get_search_text)
async def search_results(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Results",
                         reply_markup=user_keyboards.get_searched_notes_kb(message.from_user.username, message.text))


@router.callback_query(F.data == 'back_from_search')
async def back_form_search_btn(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Choose your note or add one.",
                                     reply_markup=user_keyboards.get_notes_kb(callback.message.chat.username))


@router.callback_query(F.data.startswith("last_edit:"))
async def get_last_edit_note(callback: CallbackQuery):
    note_id = callback.data.split(" ")[1]
    last_edit_note = database_operations.get_notes_last_edit(note_id)
    message_text = ""
    if last_edit_note is not None:
        message_text = (f"<b>{last_edit_note.title}</b>\n"
                        f"{last_edit_note.text}\n"
                        f"\n"
                        f"by {database_operations.get_username_by_id(last_edit_note.updated_by)}\n"
                        f"at {last_edit_note.update_date.strftime('%m/%d/%Y, %H:%M:%S')}")
    else:
        message_text = "No updates was made!"
    await callback.message.edit_text(text=message_text,
                                     reply_markup=user_keyboards.get_back_btn_to_lastedit_kb(note_id),
                                     parse_mode="HTML")


@router.callback_query(F.data.startswith("back_from_last_edit:"))
async def go_back_from_last_edit(callback: CallbackQuery):
    note = database_operations.get_note_by_id(callback.data.split(" ")[1])
    message_text = (f"<b>{note.title}</b>\n"
                    f"{note.text}")
    await callback.message.edit_text(message_text,
                                     reply_markup=user_keyboards.get_note_operations_kb(note.note_id),
                                     parse_mode="HTML")


@router.callback_query(F.data.startswith("add_user:"))
async def add_user_to_note_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddUser.get_username)
    await state.set_data({"note_id": callback.data.split(" ")[1]})
    await callback.message.edit_text(text="Enter username of person to add.",
                                     reply_markup=None)


@router.message(AddUser.get_username)
async def add_user_to_note_completion(message: Message, state: FSMContext):
    data = await state.get_data()
    note_id = data['note_id']
    note = database_operations.get_note_by_id(note_id)
    status_code = database_operations.add_user_to_note(message.text, note_id)
    if status_code == 200:
        await message.answer(text="New user successfully added!")
    else:
        await message.answer(text="No such user is using our bot!")

    message_text = (f"<b>{note.title}</b>\n"
                    f"{note.text}")
    await message.answer(message_text,
                         reply_markup=user_keyboards.get_note_operations_kb(note.note_id),
                         parse_mode="HTML",
                         show_alert=True)


@router.callback_query(F.data == "refresh_btn")
async def refresh_notes(callback: CallbackQuery):
    try:
        await callback.message.edit_text(text="Choose your note or add one.",
                                         reply_markup=user_keyboards.get_notes_kb(callback.message.chat.username))
    except Exception as ex:
        print(ex)
    await callback.answer(text="REFRESHED",
                          show_alert=True)
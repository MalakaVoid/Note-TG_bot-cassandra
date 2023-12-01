from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder
from db_op import database_operations


def get_notes_kb(username: str) -> InlineKeyboardMarkup:
    notes = database_operations.get_notes(username)
    builder = InlineKeyboardBuilder()
    for note in notes:
        builder.button(text=f"📔{note.title}",
                       callback_data=f"note: {note.note_id}")

    builder.button(text='➕',
                   callback_data='add_note_btn')
    builder.button(text='refresh',
                   callback_data='refresh_btn')
    builder.adjust(1, True)
    markup = InlineKeyboardMarkup(inline_keyboard=builder.export())
    return markup


def get_note_operations_kb(note_id):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="edit", callback_data=f'edit_note: {note_id}'),
         InlineKeyboardButton(text="delete", callback_data=f'delete_note: {note_id}')],
        [InlineKeyboardButton(text="last edit", callback_data=f'last_edit: {note_id}')],
        # [InlineKeyboardButton(text="add user", callback_data=f'add_user: {note_id}')],
        [InlineKeyboardButton(text="🔙", callback_data='back_from_note')]
    ])
    return ikb


def get_edit_note_kb(note_id):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="edit title", callback_data=f'edit_note_title: {note_id}'),
         InlineKeyboardButton(text="edit text", callback_data=f'edit_note_text: {note_id}')],
        [InlineKeyboardButton(text="🔙", callback_data=f'back_from_note_edit: {note_id}')]
    ])
    return ikb


def get_searched_notes_kb(username: str, text: str) -> InlineKeyboardMarkup:
    notes = database_operations.search_note(username, text)

    builder = InlineKeyboardBuilder()

    for note in notes:
        builder.button(text=f"📔{note['title']}",
                       callback_data=f"note: {note['_id']}")

    builder.button(text='🔙',
                   callback_data='back_from_search')
    builder.adjust(1, True)
    markup = InlineKeyboardMarkup(inline_keyboard=builder.export())
    return markup


def get_back_btn_to_lastedit_kb(note_id: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙", callback_data=f'back_from_last_edit: {note_id}')]
    ])
    return ikb
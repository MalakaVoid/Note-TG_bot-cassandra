from cassandra.cluster import Cluster
import datetime

cluster = Cluster()
session = cluster.connect('db1')



def test():
    # print(get_new_lastedit_id())
    # print(get_new_note_id())
    # print(add_note('malaka', 'Note 1', 'asdkaskdmaksdladsad\n sdjalskdsak'))
    # print(get_notes('malaka'))
    # print(get_note_by_id('1'))
    # print(delete_note(2))
    # update_note(3, "TITLE", 'malaka', False)
    # print(get_notes_last_edit(3))
    # print(get_username_by_id(1))
    pass

def get_username_by_id(id):
    username = session.execute(f"SELECT username FROM users WHERE user_id = {id}").one().username
    return username


def get_notes_last_edit(note_id):
    rows = session.execute(f"SELECT * from lastedit where note = {note_id}")
    return rows.one()


def update_note(note_id: str, text: str, username: str, is_title_update: bool) -> int:
    res = session.execute(f"SELECT lastedit_id from lastedit where note = {note_id}").one()
    note = get_note_by_id(note_id)
    if is_title_update:
        tmp = 'title'
    else:
        tmp = 'text'
    try:
        if res is not None:
            session.execute(f"UPDATE lastedit SET text = '{note.text}', update_date = '{note.updation_date}', "
                            f"updated_by = {get_user_id_by_username(username)} WHERE lastedit_id = {res.lastedit_id}")
        else:
            session.execute(f"INSERT INTO lastedit (lastedit_id, note, text, title, update_date, updated_by) "
                            f"VALUES ({get_new_lastedit_id()}, {note_id}, '{note.text}', '{note.title}', "
                            f"'{note.updation_date}', {note.updated_by});")

        session.execute(f"UPDATE notes SET {tmp}='{text}', updated_by = {get_user_id_by_username(username)}, "
                        f"updation_date = '{datetime.datetime.now()}' WHERE note_id = {note_id}")
    except Exception as ex:
        print(ex)
        return 404
    return 200


def delete_note(note_id: str) -> int:
    res = session.execute(f"SELECT lastedit_id from lastedit where note = {note_id}").one()
    try:
        session.execute(f"delete from notes where note_id={note_id}")
        if res is not None:
            session.execute(f"delete from lastedit where note={res.lastedit_id}")
    except Exception as ex:
        print(ex)
        return 404
    return 200


def get_note_by_id(id):
    res = session.execute(f"SELECT * from notes where note_id = {id}")
    return res.one()


def get_notes(username: str):
    user_id = get_user_id_by_username(username)
    rows = session.execute(f"SELECT * from notes where user contains {user_id}")
    return rows.all()


def get_user_id_by_username(username):
    user_id = session.execute(f"SELECT user_id from users where username = '{username}'").one().user_id
    return user_id


def add_note(username: str, title: str, text: str) -> int:
    user_id = get_user_id_by_username(username)
    query = (f"INSERT INTO notes (note_id, creation_date, text, title, updated_by, updation_date, user) "
                          f"VALUES ({get_new_note_id()}, '{datetime.datetime.now()}', '{text}', '{title}', "
                          f"{user_id}, '{datetime.datetime.now()}', [{user_id}]);")
    try:
        res = session.execute(query)
    except Exception as ex:
        return 404
    return 200


def get_new_user_id():
    rows = session.execute("SELECT user_id from users;")
    res = rows.all()
    mas = [0]
    for each in res:
        mas.append(each.user_id)
    return max(mas) + 1


def get_new_note_id():
    rows = session.execute("SELECT note_id from notes;")
    res = rows.all()
    mas = [0]
    for each in res:
        mas.append(each.note_id)
    return max(mas) + 1


def get_new_lastedit_id():
    rows = session.execute("SELECT lastedit_id from lastedit;")
    res = rows.all()
    mas = [0]
    for each in res:
        mas.append(each.lastedit_id)
    return max(mas) + 1


def registrate_user(username: str, first_name: str, last_name="") -> int:
    try:
        res = session.execute(f"INSERT INTO users (user_id, first_name, last_name, username) "
                              f"VALUES ({get_new_user_id()}, '{first_name}', '{last_name}', '{username}');")
    except Exception as ex:
        return 404
    return 200


def authorize_user(username: str) -> int:
    res = session.execute(f"SELECT user_id, username from users where username = '{username}';")
    if res.one() is not None:
        return 200
    return 404
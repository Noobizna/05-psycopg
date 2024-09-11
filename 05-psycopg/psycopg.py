import psycopg2

def create_db(conn):
    """
    Создаёт таблицы client и phone в базе данных.
    :param conn: Объект соединения с базой данных.
    """
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS phone; DROP TABLE IF EXISTS client;""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) CHECK (email LIKE '%@%.%')
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phone (
        id SERIAL PRIMARY KEY,
        client_id INTEGER NOT NULL REFERENCES client(id) ON DELETE CASCADE,
        telephone VARCHAR(20)
    );
    """)
    conn.commit()

def add_client(conn, first_name, last_name, email, telephone=None):
    """
    Добавляет нового клиента в таблицу client. Если указан телефон, добавляет его в таблицу phone.
    :param conn: Объект соединения с базой данных.
    :param first_name: Имя клиента.
    :param last_name: Фамилия клиента.
    :param email: Электронная почта клиента.
    :param telephone: Телефон клиента (опционально).
    """
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO client(first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id;
    """, (first_name, last_name, email))
    client_id = cur.fetchone()[0]
    if telephone:
        add_phone(conn, client_id, telephone)
    conn.commit()

def add_phone(conn, client_id, telephone):
    """
    Добавляет телефон клиента в таблицу phone.
    :param conn: Объект соединения с базой данных.
    :param client_id: ID клиента.
    :param telephone: Телефон клиента.
    """
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO phone(client_id, telephone) VALUES (%s, %s) RETURNING id;
    """, (client_id, telephone))
    conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    """
    Изменяет информацию о клиенте в таблице client.
    :param conn: Объект соединения с базой данных.
    :param client_id: ID клиента.
    :param first_name: Новое имя клиента.
    :param last_name: Новая фамилия клиента.
    :param email: Новая электронная почта клиента.
    """
    cur = conn.cursor()
    cur.execute("""
    UPDATE client
    SET first_name = COALESCE(%s, first_name),
        last_name = COALESCE(%s, last_name),
        email = COALESCE(%s, email)
    WHERE id = %s;
    """, (first_name, last_name, email, client_id))
    conn.commit()

def delete_phone(conn, telephone):
    """
    Удаляет телефон клиента из таблицы phone.
    :param conn: Объект соединения с базой данных.
    :param telephone: Телефон клиента, который нужно удалить.
    """
    cur = conn.cursor()
    cur.execute("""
    DELETE FROM phone
    WHERE telephone = %s;
    """, (telephone,))
    conn.commit()

def delete_client(conn, client_id):
    """
    Удаляет клиента из таблицы client и все его телефоны из таблицы phone.
    :param conn: Объект соединения с базой данных.
    :param client_id: ID клиента, которого нужно удалить.
    """
    cur = conn.cursor()
    cur.execute("""
    DELETE FROM client
    WHERE id = %s RETURNING id, first_name, last_name, email;
    """, (client_id,))
    conn.commit()

    print(f"Клиент с id {client_id} удалён.")

def find_client(conn, first_name=None, last_name=None, email=None, telephone=None):
    """
    Находит клиента по одному из параметров и выводит его информацию.
    :param conn: Объект соединения с базой данных.
    :param first_name: Имя клиента.
    :param last_name: Фамилия клиента.
    :param email: Электронная почта клиента.
    :param telephone: Телефон клиента.
    """
    cur = conn.cursor()
    cur.execute("""
    SELECT client.id, first_name, last_name, email, telephone FROM client
    LEFT JOIN phone ON client.id = phone.client_id
    WHERE first_name = %s OR last_name = %s OR email = %s OR telephone = %s;
    """, (first_name, last_name, email, telephone))

    result = cur.fetchall()
    if result:
        for row in result:
            print(row)
    else:
        print("Клиент не найден.")


with psycopg2.connect(database="clients_db", user="postgres", password="051198") as conn:
    cur = conn.cursor()
    cur.execute("SET client_encoding TO 'UTF8';")
    create_db(conn)

    add_client(conn, 'Andrey', 'Sokolov', 'andrey_sokolov@mail.ru', '89031234568')
    add_client(conn, 'Olga', 'Petrova', 'olga_petrova@gmail.com', '89037778880')
    add_client(conn, 'Sergey', 'Frolov', 'sergey@gmail.com', '89164579871')
    add_client(conn, 'Natalia', 'Kuznetsova', 'natalia@bk.ru')
    add_client(conn, 'Mikhail', 'Lermontov', 'mikhail_l@yahoo.com', '89051112233')
    add_client(conn, 'Dmitry', 'Popov', 'dmitry@mail.ru', '89174445566')
    add_client(conn, 'Anastasia', 'Smirnova', 'anastasia@gmail.com', '89167778823')
    add_client(conn, 'Yuliya', 'Nikolaeva', 'yuliya_nik@mail.ru')
    add_client(conn, 'Aleksei', 'Groshev', 'aleksei@gmail.com', '89569876543')
    add_client(conn, 'Marina', 'Titova', 'marina@list.ru', '89051199776')

    change_client(conn, 1, last_name='Sokolova')
    change_client(conn, 5, email='mikhail_updated@yahoo.com')

    delete_phone(conn, '89167778823')
    delete_client(conn, 3)

    find_client(conn, first_name='Natalia')

conn.close()

import psycopg2


# Функция, создающая структуру БД (таблицы)
def create_db(co):
    cur.execute("""
    DROP TABLE phones;
    DROP TABLE clients;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id  SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        surname VARCHAR(40) NOT NULL,
        email VARCHAR(40) NOT NULL UNIQUE
    );
  
  
    CREATE TABLE IF NOT EXISTS phones(
        id SERIAL PRIMARY KEY,
        phone_ VARCHAR(40) UNIQUE,
        client_id INTEGER REFERENCES clients(id)
    );
    """)
    print("Таблицы созданы")
    co.commit()


# Функция, позволяющая добавить нового клиента
def add_client(co, first_name, last_name, email, phone=None):
    cur.execute("""
    INSERT INTO clients(name, surname,email) VALUES (%s, %s, %s) RETURNING id;    
    """, (first_name, last_name, email))
    id_ = cur.fetchone()[0]
    if phone:
        cur.execute("""
        INSERT INTO phones(phone_,client_id) VALUES (%s, %s);
        """, (phone, id_))
        co.commit()
    print('Данные добавлены')


# Функция, позволяющая добавить телефон для существующего клиента
def add_phone(co, client_id, phone):
    cur.execute("""
    INSERT INTO phones(phone_, client_id) VALUES(%s,%s);
    """, (phone, client_id))
    co.commit()
    print('Телефон для существующего клиента добавлен')


# Функция, позволяющая изменить данные о клиенте
def change_client(co, id, first_name=None, last_name=None, email=None, old_phone=None, phones=None):
    if first_name:
        cur.execute('''UPDATE clients SET name=%s  WHERE id =%s;''',
                    (first_name, id))
    elif last_name:
        cur.execute('''UPDATE clients SET surname=%s WHERE id =%s;''',
                    (last_name, id))
    elif email:
        cur.execute('''UPDATE clients SET email=%s WHERE id =%s;''',
                    (email, id))
    elif old_phone:
        cur.execute('''UPDATE phones Set phone_=%s WHERE phone_=%s;''', (phones, old_phone))
    elif old_phone is None:
        old_phone = input('Какой номер телефона нужно заменить?: ')
        cur.execute('''UPDATE phones Set phone_=%s WHERE phone_=%s;''', (phones, old_phone))
    co.commit()
    print('Данные клиента изменены')


# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(co, client_id, phone):
    cur.execute("""
    DELETE FROM phones WHERE client_id=%s AND phone_=%s;
    """, (client_id, phone))
    co.commit()
    print('Телефон клиента удален')


# Функция, позволяющая удалить существующего клиента
def delete_client(co, client_id):
    cur.execute("""
    DELETE FROM phones WHERE client_id=%s;
    DELETE FROM clients WHERE id=%s;   
    """, (client_id, client_id))
    co.commit()
    print('Запись клиента удалена')


# Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
def find_client(co, first_name=None, last_name=None, email=None, phone=None):
    cur.execute("""
    SELECT name, surname, email, phone_  FROM clients
    LEFT JOIN phones p ON clients.id = p.client_id
    WHERE name=%s OR surname=%s OR email=%s OR phone_=%s;""", (first_name, last_name, email, phone))
    print(cur.fetchall())
    co.commit()
    print(cur.fetchall())


with psycopg2.connect(database="home_work", user="postgres", password="") as conn:
    with conn.cursor() as cur:
        create_db(conn)
        add_client(conn, 'Vasya', 'Pupkin', '111@mail.ru', '+79781111111')
        add_client(conn, 'Valya', 'Gudkina', '545454@ya.ru', '+79782222222')
        add_phone(conn, 2, '+79783333333')
        change_client(conn, id=2, first_name=None, last_name="Pupkina", email=None,
                      phones=None, old_phone=None)
        delete_phone(conn, 2, '+79782222222')
        delete_client(conn, '2')
        find_client(conn, phone='+79781111111')

conn.close()

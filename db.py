import utils

def connect_to_database(name="database.db"):
    import sqlite3
    return sqlite3.connect(name , check_same_thread=False)


def init_db(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            username TEXT NOT NULL ,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE ,
            balance REAL NOT NULL DEFAULT 0.0,
            Student BOOLEAN NOT NULL,
            Instructor BOOLEAN NOT NULL
        )
    ''') 

    connection.commit()   


def add_user(connection,username , password , email,Student,Instructor):
    cursor = connection.cursor()
    hashed_password = utils.hash_password(password)
    query = f''' INSERT INTO users (username,password,email,Student,Instructor) VALUES ( ? , ?  , ?,?,?)'''
    cursor.execute(query , (username ,hashed_password ,email,Student,Instructor)) 
    connection.commit()    



def get_user(connection,email):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE email = ?'''
    cursor.execute(query, (email,))
    return cursor.fetchone()    

def get_user_id(connection,email):
    cursor = connection.cursor()
    query = '''SELECT id FROM users WHERE email = ?'''
    cursor.execute(query, (email,))
    return cursor.fetchone()  


def get_all_users(connection):
    cursor = connection.cursor()

    query = '''SELECT * FROM users'''

    cursor.execute(query)
    return cursor.fetchall()

def seed_admin_user(connection):
     admin_username = 'admin'
     admin_password = '@Dmin2023'
     admin_email = "admin1@gmail.com"
     student = False
     instructor = False
     admin_user = get_user(connection,admin_email)

     if not admin_user :
        add_user(connection,admin_username,admin_password,admin_email,student,instructor)
        print("Admin user seeded Successfully")

def update_user_balance(connection , email):
    cursor = connection.cursor()

    query = '''UPDATE users SET balance = 0 WHERE email = ?'''
    connection.execute(query , (email,))
    connection.commit()


def init_courses_table(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            user_id INTEGER NOT NULL ,
            title TEXT NOT NULL ,
            description TEXT ,
            price REAL NOT NULL,
            img_url TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''') 

    connection.commit()


def add_course(connection,user_id , title ,description,price,img_url=None):
    cursor = connection.cursor()

    query = ''' INSERT INTO courses (user_id , title ,description,price,img_url) VALUES (?,?,?,?,?) '''

    cursor.execute(query , (user_id , title ,description,price,img_url))

    connection.commit()

def get_course(connection,course_id):
    cursor = connection.cursor()

    query = ''' SELECT * FROM courses WHERE id = ?'''
    cursor.execute(query,(course_id,))
    return cursor.fetchone()

def get_user_courses(connection,user_id):
    cursor = connection.cursor()

    query = ''' SELECT * FROM courses WHERE user_id = ?'''

    cursor.execute(query,(user_id,))
    return cursor.fetchall()


def get_all_courses(connection):
    cursor = connection.cursor()

    query = '''SELECT * FROM courses'''

    cursor.execute(query)
    return cursor.fetchall()

def update_balance(connection,course_id):
    cursor = connection.cursor()
    course_query = '''SELECT price , user_id FROM courses WHERE id = ?'''
    cursor.execute(course_query,(course_id,))
    course_data = cursor.fetchone()

    if course_data:
        course_price , user_id = course_data

        update_balance_query = '''UPDATE users SET balance = balance + ? WHERE id = ?'''
        cursor.execute(update_balance_query,(course_price , user_id))
        connection.commit()


def init_comments_table (connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    connection.commit()


def add_comment(connection,course_id,user_id,text):
    cursor = connection.cursor()

    query = ''' INSERT INTO comments (course_id,user_id,text) VALUES (?,?,?)'''

    cursor.execute(query ,(course_id,user_id,text))
    connection.commit()



def get_comments_for_course(connection,course_id):
    cursor = connection.cursor()

    query = '''
        SELECT users.username , comments.text , comments.timestamp
        FROM comments 
        JOIN users ON comments.user_id = users.id
        WHERE comments.course_id = ?
    '''         
    cursor.execute(query , (course_id,))
    return cursor.fetchall()

def init_purchase_history(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_history (
            buyer_id INT NOT NULL,
            target_course_id INT NOT NULL,
            FOREIGN KEY (target_course_id) REFERENCES courses (id),
            FOREIGN KEY (buyer_id) REFERENCES users (id) , 
            PRIMARY KEY  (buyer_id,target_course_id) 
        )
    ''') 

    connection.commit()  

def add_to_history(connection,buyer_id , target_course_id):
    cursor = connection.cursor()

    query = ''' INSERT INTO purchase_history (buyer_id ,target_course_id) VALUES (?,?) '''

    cursor.execute(query , (buyer_id ,target_course_id))

    connection.commit()




def cheak_history(connection,buyer_id,target_course_id):
    cursor = connection.cursor()

    query = '''SELECT * FROM purchase_history WHERE buyer_id = ? AND target_course_id = ? '''
    cursor.execute(query,(buyer_id,target_course_id))
    return cursor.fetchone()
    

def get_courses_for_user(connection,buyer_id):
    cursor = connection.cursor()

    query = '''
        SELECT * FROM courses  
        JOIN purchase_history ON courses.id = purchase_history.target_course_id
        WHERE buyer_id = ?
    '''         
    cursor.execute(query , (buyer_id,))
    return cursor.fetchall()
import psycopg2
from config import host_c,user_c,password_c,db_name_c,port_c,token

# def connect_to_db(self):
#     self.conn = psycopg2.connect(host=host_c,
#     user=user_c,
#     password=password_c,
#     database=db_name_c,
#     port=port_c)
#     self.cursor = self.conn.cursor()

def add_seller(seller_uuid, seller_name, seller_email, seller_password):
    # Подключение к базе данных
    conn = psycopg2.connect(host=host_c,
    user=user_c,
    password=password_c,
    database=db_name_c,
    port=port_c)
    cursor = conn.cursor()

    query = """INSERT INTO sellers (seller_uuid, seller_name, seller_email, seller_password)
               VALUES (%s, %s, %s, %s)"""
    
    params = (seller_uuid, seller_name, seller_email, seller_password)
    
    try:
        cursor.execute(query, params)
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
    finally:
        cursor.close()
        conn.close()

def remove_seller(seller_uuid):
    # Подключение к базе данных
    conn = psycopg2.connect(host=host_c,
    user=user_c,
    password=password_c,
    database=db_name_c,
    port=port_c)

    cursor = conn.cursor()
    query = """DELETE FROM sellers
               WHERE seller_uuid = %s"""
    
    params = (seller_uuid,)
    
    try:
        cursor.execute(query, params)
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
    finally:
        cursor.close()
        conn.close()

# примеры использования функций
# add_seller('12345678-1234-1234-1234-1234567890AB', 'John Doe', 'johndoe@example.com', 'password123')
# remove_seller('12345678-1234-1234-1234-1234567890AB')
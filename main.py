import uuid
from flask import Flask, jsonify, request, session
from config import host_c,user_c,password_c,db_name_c,port_c
import psycopg2

import jwt
from datetime import datetime, timedelta
from functools import wraps

from model.product import Product
from model.user import User

# CREATE - создание сущности на сервере - POST (параметры в теле запроса)
# RETRIEVE - чтение сущности с сервера - GET (параметры в URL ""….?id=123"")
# UPDATE - обновление/изменение сущности - PUT
# DELETE - удаление сущности - DELETE (параметры в теле запроса)

sellers = []
products = []

app = Flask(__name__)
# >>> uuid.uuid4 () .hex
# '4645e2a1c11448c7a20a972b88897c9e'

app.config['SECRET_KEY'] = '4645e2a1c11448c7a20a972b88897c9e' # секретный ключ
# app.config['SECRET_KEY'] = str(uuid.uuid4()) # секретный ключ

conn = psycopg2.connect(
    host=host_c,
    database=db_name_c,
    user=user_c,
    password=password_c,
    port=port_c
)


def token_required(func):#декоратор - если для выполнения действия нужен токен.
    @wraps(func)
    def decorated(*args, **kwargs):
        # получаем токен из сессии
        try:
            if request.method == 'POST' or request.method == 'PUT':
                data = request.get_json()
                token = data['token']
            if request.method == 'GET' or request.method == 'DELETE':
                token = request.args.get('token')
        except:
            return jsonify({'status': 'unknown error'})
        if not token:
            return jsonify({'status': 'token is missing'})
        
        # проверяем токен
        try:
            #добавляем payload в аргументы функции
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            kwargs['payload'] = payload
        except jwt.exceptions.InvalidTokenError:
            return jsonify({'status': 'invalid token'})
        except:
            return jsonify({'status': 'unknown error'})
        return func(*args, **kwargs)
    
    return decorated

# пути:

# /sign_in                  войти в аккаунт
# /sign_up                  создать аккаунт и сразу войти в него
# /check_token              проверка токена (функция для отладки JWT)

# с проверкой JWT:
# user/change_username      изменение имени пользователя
# user/change_password      изменение пароля пользователя
# /products/add             добавление одного товара
# /products/add_many        добавление нескольких товаров
# /products/edit            изменение одного товара
# /products/delete          удаление одного товара

# без JWT:
# /products/get             получение одного товара
# /products/get_many        получение нескольких товаров + фильтры


# delete this
# # начальная страница
# @app.route('/')
# def home():
#     # return jsonify({'status':'work in progress'})
#     if not session.get('logged_in'):
#         return render_template('login.html')
#     else:
#         return 'logged in currently'



# войти в аккаунт
@app.route('/sign_in', methods=['POST'])
def sign_in():

# {"username": "user_1", "password": "qwerty123"}

    data = request.get_json()
    username = data['username']
    password = data['password']

    query = "SELECT * FROM public.users WHERE user_name = '{}'  AND user_password = '{}'".format(username, password)

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    if rows.__len__ == 0:
        return jsonify({'status':'failed to login'})
    uuid = rows[0][0]
    cur.close()

    session['logged_in'] = True
    token = jwt.encode({
                            'uuid': uuid,
                            'username': username, 
                            'expiration': str(datetime.utcnow() + timedelta(seconds=120))
                        }, 
                            app.config['SECRET_KEY'], 
                            algorithm='HS256')
    return jsonify({'token': token})
    # return jsonify({'status':'work in progress'})


# создать аккаунт и сразу войти в него
@app.route('/sign_up', methods=['POST'])
def sign_up():
    return jsonify({'status':'work in progress'})


# создать аккаунт и сразу войти в него
@app.route('/check_token', methods=['POST'])
@token_required
def check_token(payload):
    return jsonify({'status':'success','payload': payload})





# добавление одного товара
@app.route('/products/add', methods=['POST'])
@token_required
def products_add(payload):
    page_json = request.get_json()
    uuid = page_json['uuid']
    name = page_json['name']
    description = page_json['description']

    query = "INSERT INTO public.products VALUES ('{}', '{}', '{}')".format(uuid, name, description)
    cur = conn.cursor()
    cur.execute(query)
    cur.close()

    return jsonify({'status':'success'})


# добавление нескольких товаров
@app.route('/products/add_many', methods=['POST'])
def products_add_many():
    return jsonify({'status':'work in progress'})


# изменение товара
@app.route('/products/edit', methods=['PUT'])
def products_edit():
    return jsonify({'status':'work in progress'})


# удаление товара
@app.route('/products/delete', methods=['DELETE'])
@token_required
def products_delete(payload):
    uuid = request.args.get('uuid')
    query = "DELETE FROM public.products WHERE product_uuid = '{}'".format(uuid)
    cur = conn.cursor()
    cur.execute(query)
    cur.close()
    return jsonify({'status':'success'})


# получение одного товара
@app.route('/products/get', methods=['GET'])
def products_get():

    uuid = request.args.get('uuid')
    query = "SELECT * FROM public.products WHERE product_uuid = '{}'".format(uuid)

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    data = []
    for row in rows:
        data.append({
            'uuid': row[0],
            'name': row[1],
            'description': row[2]
        })

    return jsonify(data)

# получение нескольких страниц с товарами + фильтры
@app.route('/products/get_many', methods=['GET']) #hellscheck путь - проверка на ответ
def products_get_many():
    query = "SELECT * FROM pus ORDER BY product_name ASC "
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    data = []
    for row in rows:
        data.append({
            'uuid': row[0],
            'name': row[1],
            'description': row[2]
        })
    return jsonify(data)






@app.route('/ping', methods=['GET']) #hellscheck путь - проверка на ответ
def ping():
    return jsonify({'response':'pong'})






if __name__ == '__main__':
    app.run(debug=True)



# авторизация, работа с пользователями, фильтрация через query (добавить категории продуктов, цены) возрастание, убывание
# реализовать добавление нескольких продуктов сразу
# показать в postman что всё работает
# регистрация через cookie или JWT
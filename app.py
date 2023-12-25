import uuid
from flask import Flask, jsonify, request, session
from utilities.config import host_c,user_c,password_c,db_name_c,port_c
import psycopg2

import jwt
from datetime import datetime, timedelta
from functools import wraps

from model.product import Product
from model.user import User
from utilities.config import host_c,user_c,password_c,db_name_c,port_c
from utilities.decorators import token_required

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
# - вместо psycopg2 истользовать SQL алхимию (более удобная работа с данными) 
# + pycache убрать 
# + добавить gitignore 
# добавить readme (описание части проекта + как запустить)
# + декаратор для токенов и approad убрать в отдельные файлы (например routers)
# + убрать pycache
# добавить документацию (+5 баллов) = word файл. Что писать есть в требованиях. Ссылку в readme
# 
# доки + бэк = зачёт



# 7 посещения
# 2 галочки
# 6 баллов за код
# 
# ещё 10 надо
# 

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
    
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        # return jsonify({'token': rows})
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
    except:
        return jsonify({'status':'failed to login'})


# создать аккаунт и сразу войти в него
@app.route('/sign_up', methods=['POST'])
def sign_up():

    data = request.get_json()
    user_uuid = data['user_uuid']
    user_name = data['user_name']
    password = data['password']

    query = "SELECT COUNT(*) FROM public.users WHERE user_name = '{}'".format(user_name)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    if (rows[0][0] == 1):
        return jsonify({'status':'username occupied'})

    query = "INSERT INTO public.users VALUES ('{}', '{}', '{}')".format(user_uuid, user_name, password)
    cur = conn.cursor()
    cur.execute(query)
    cur.close()

    session['logged_in'] = True
    token = jwt.encode({
                            'uuid': user_uuid,
                            'username': user_name, 
                            'expiration': str(datetime.utcnow() + timedelta(seconds=120))
                        }, 
                            app.config['SECRET_KEY'], 
                            algorithm='HS256')
    return jsonify({'token': token})



# проверить токен
@app.route('/check_token', methods=['POST'])
@token_required(request, app)
def check_token(payload):
    return jsonify({'status':'success','payload': payload})





# добавление одного товара
@app.route('/products', methods=['POST'])
@token_required(request, app)
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


# изменение товара
@app.route('/products', methods=['PUT'])
@token_required(request, app)
def products_edit(payload):
    data = request.get_json()
    product_uuid = data['uuid']
    new_description = data['text']
    query = "UPDATE public.products SET product_description = '{}' WHERE products.product_uuid = '{}'".format(new_description, product_uuid)
    cur = conn.cursor()
    cur.execute(query)
    return jsonify({'status':'success'})


# удаление товара (проверить пользователя)
@app.route('/products', methods=['DELETE'])
@token_required(request, app)
def products_delete(payload):
    uuid = request.args.get('uuid')
    query = "SELECT COUNT(*) FROM public.products WHERE product_uuid = '{}'".format(uuid)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    if (rows[0][0] == 0):
        return jsonify({'status':'no such page'})

    query = "DELETE FROM public.products WHERE product_uuid = '{}'".format(uuid)
    cur = conn.cursor()
    cur.execute(query)
    cur.close()
    return jsonify({'status':'success'})


# получение одного товара
@app.route('/products', methods=['GET'])
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
@app.route('/products/all', methods=['GET']) #hellscheck путь - проверка на ответ
def products_get_many():
    query = "SELECT * FROM public.products ORDER BY product_name ASC "
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

# получение данных владельца объявления
@app.route('/users/by_product', methods=['GET'])
def users_by_products():

    data = request.get_json()
    product_uuid = data['product_uuid']
    query = "SELECT u.user_name, u.user_uuid FROM public.products p \
            LEFT JOIN public.users u ON p.user_uuid = u.user_uuid \
            WHERE p.product_uuid = '{}'".format(product_uuid)

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    data = []
    for row in rows:
        data.append({
            'user_name': row[0],
            'user_uuid': row[1],
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
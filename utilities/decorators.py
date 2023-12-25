from functools import wraps
from flask import app, jsonify, request
import jwt

def token_required(request, app):#декоратор - если для выполнения действия нужен токен.
    def decorator(func):
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
    return decorator
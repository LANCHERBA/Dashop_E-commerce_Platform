import hashlib
import json
import time
from django.conf import settings
import jwt
from carts.views import CartsView

from django.http import JsonResponse
from django.shortcuts import render
#10200-10299: error status code

# Create your views here.
from user.models import UserProfile
#创建实体类
newCartsView = CartsView()

def tokens(request):
    #登录
    if request.method != 'POST':
        result = {'code':10200,'error':'Please use POST'}
        return JsonResponse(result)

    data = request.body
    json_obj = json.loads(data)
    username = json_obj['username']
    password = json_obj['password']
    carts_info = json_obj['carts']
    if not username or not password:
        result = {'code':10201,'error':'Please insert correct username or password.'}
        return JsonResponse(result)
    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'code':10202,'error':'Please insert correct username or password.'}
        return JsonResponse(result)
    user = users[0]
    m = hashlib.md5()
    m.update(password.encode())
    if m.hexdigest() != user.password:
        result = {'code':10203,'error':'Please insert correct username or password.'}
        return JsonResponse(result)
    #send token
    token = make_token(username)
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}, 'carts_count': newCartsView.merge_carts(user.id,carts_info)}
    return JsonResponse(result)

def make_token(username,expire=3600*24):# default expire time: 1 day

    now = time.time()
    key = settings.SHOP_TOKEN_KEY
    payload = {'username':username,'exp':int(now+expire)}
    return jwt.encode(payload,key,algorithm='HS256')

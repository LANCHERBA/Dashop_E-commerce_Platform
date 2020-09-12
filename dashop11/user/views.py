import hashlib
import json
import random
import base64
from django.core.cache import cache,caches
from django.core import mail
from django.http import JsonResponse
from dtoken.views import make_token
from user.models import *
from django.conf import settings #use this way!!!
from .tasks import send_active_email_celery
from django.views import View
from tools.login_dec import login_check
from urllib.parse import urlencode
import requests
from django.db import transaction

#10100-10199 error status(异常状态码)
EMAIL_CACHE = caches['user_email']

# Create your views here.

def users(request):
    if request.method == 'POST':
        #User registration(注册用户)
        data = request.body
        json_obj = json.loads(data)
        username = json_obj['uname']
        password = json_obj['password']
        email = json_obj['email']
        phone = json_obj['phone']
        if len(password) < 6:
            result = {'code':10100,'error':'Password length is not in range.'}
            # JsonResponse: Convert parameter to json format and change 'content-Type' in response header to 'application/json'
            # JsonResponse: 将参数转成json串　且将响应头中的CT值改成application/json
            return JsonResponse(result)

        #username already exist?
        #用户名是否可用？已注册的话给个错误返回
        old_users = UserProfile.objects.filter(username = username)
        if old_users:
            result = {'code':10101,'error':'User already exists.'}
            return JsonResponse(result)

        #create user (password encrypted by md5)
        #创建用户　密码用md5
        m = hashlib.md5()
        m.update(password.encode())
        try: #username有唯一约束，如果同时有相同的请求进入，会出现无法注册的情况。
            user = UserProfile.objects.create(
                username=username,password=m.hexdigest(),email=email,phone=phone)
        except Exception as e:
            return JsonResponse({'code':10102,'error':'Your username is used.'})

        #use Jwt send token: exp:1 day, username:xxx included in token
        #用jwt签发token　有效期1天，token里面存放 username:xxxx
        token = make_token(username)
        #if success return:
        #{'code':200,'username':username,'data':{'token':xxx},'carts_count':0}

        #generate 4 digits random number　生成四位随机数
        code = "%s"%(random.randint(1000,9999))
        #username+random_number to a new string
        code_str = code+'_'+username
        #b64(new string)
        code_bs = base64.urlsafe_b64encode(code_str.encode())
        #store the b64
        EMAIL_CACHE.set('email_active_%s'%(username),code,3600*24*3)
        #generate account activation link
        verify_url = 'http://127.0.0.1:7000/dadashop/templates/active.html?code=%s'%(code_bs.decode())#send the link to user email address
        #send_active_email(email,verify_url)
        send_active_email_celery.delay(email,verify_url)

        return JsonResponse({'code':200,'username':username,'data':{'token':token.decode()},'carts_count':0})

def send_active_email(email_address, v_url):
    #发激活邮件
    subject = '达达商城激活邮件'
    html_message = '''
    <p>尊敬的用户您好</p>
    <p>请点击此链接激活您的账户(3天内有效):</p>
    <p><a href='%s' target='_blank'>点击激活</a></p>
    '''%(v_url)
    mail.send_mail(subject,'',from_email=settings.EMAIL_HOST_USER,recipient_list=[email_address],html_message=html_message)

def user_active(request):
    # activate user:激活用户
    if request.method != 'GET':
        result = {'code': 10103, 'error': 'Request method is wrong.'}
        return JsonResponse(result)
    code  = request.GET.get('code')
    if not code:
        return JsonResponse({'code':10104,'error':'Please send the correct code'})
    code_str = base64.urlsafe_b64decode(code.encode()).decode()
    # code_str:'code_username'
    random_code,username = code_str.split('_')
    old_code = EMAIL_CACHE.get('email_active_%s'%(username))
    if not old_code:
        return JsonResponse({'code':10105,'error':'Link is wrong.'})
    if random_code != old_code:
        return JsonResponse({'code':10106,'error':'Link is wrong.'})
    try:
        user = UserProfile.objects.get(username = username)
    except Exception as e:
        return JsonResponse({'code':10107,'error':'User not exist.'})
    user.is_active = True
    user.save()
    #删除缓存
    EMAIL_CACHE.delete('email_active_%s'%(username))
    return JsonResponse({'code':200,'data':'OK'})

#CBV - 类视图(适配RESTFUL API)
class AddressView(View):
    @login_check
    def dispatch(self, request, *args, **kwargs):
        #check if 2 users are the same
        #登陆的用户只能改自己的地址
        if request.myuser.username != kwargs['username']:
            return JsonResponse({'code':10108,'error':"Wrong user."})
        json_str = request.body
        request.json_obj = {}
        if json_str:
            json_obj = json.loads(json_str)
            request.json_obj = json_obj
        return super().dispatch(request,*args,**kwargs)

    #405响应　如果视图类没定义该http请求动作的方法,则报405错误。
    def get(self,request,username):
        user = request.myuser
        all_addr = user.address_set.filter(is_active = True)
        res = []
        for addr in all_addr:
            addr_data = {}
            addr_data['id'] = addr.id
            addr_data['address'] = addr.address
            addr_data['receiver'] = addr.receiver
            addr_data['tag'] = addr.tag
            addr_data['receiver_mobile'] = addr.receiver_mobile
            addr_data['is_default'] = addr.is_default
            res.append(addr_data)
        return JsonResponse({'code':200,'addresslist':res})

    def post(self,request,username):
        data = request.json_obj
        #could check if data is {}
        receiver = data['receiver']
        receiver_phone = data['receiver_phone']
        address = data['address']
        postcode = data['postcode']
        tag = data['tag']

        # if request.myuser.username != username:
        #     raise
        user = request.myuser
        #反向查询　user.address_set.all()
        #判断一下　默认地址问题
        old_addr = Address.objects.filter(user_profile = user)
        default_status = False
        if not old_addr:
            default_status = True
        Address.objects.create(user_profile = user,
                               receiver=receiver,
                               address = address,
                               receiver_mobile=receiver_phone,
                               postcode=postcode,
                               tag=tag,is_default=default_status)
        return JsonResponse({'code':200,'data':'添加成功'})

    def put(self,request,username,addressid):
        user = request.myuser
        #登陆者只能更改自己的邮箱
        addresses = Address.objects.filter(id = addressid,is_active=True,user_profile=user)
        if not addresses:
            return JsonResponse({'code':10109,'error':'Address not exist.'})
        address = addresses[0]
        data = request.json_obj
        address.receiver = data['receiver']
        address.receiver_mobile = data['receiver_mobile']
        address.tag = data['tag']
        address.address = data['address']
        address.save()
        return JsonResponse({'code':200,'data':'地址修改成功！'})

    def delete(self,request,username,addressid):
        user = request.myuser
        # 登陆者只能删除自己的邮箱
        addresses = Address.objects.filter(id=addressid, is_active=True, user_profile=user)
        if not addresses:
            return JsonResponse({'code': 10109, 'error': 'Address not exist.'})
        address = addresses[0]
        address.is_active = False
        address.save()
        return JsonResponse({'code': 200, 'data': '地址删除成功！'})

def oauth_url(request):
    #获取微博授权地址
    params = {
        'response_type':'code',
        'client_id':settings.WEIBO_CLIENT_ID,
        #用户授权后跳转到哪个页面
        'redirect_uri':settings.WEIBO_REDIRECT_URI
    }

    weibo_url = 'https://api.weibo.com/oauth2/authorize?'
    url = weibo_url + urlencode(params)
    #请求不合法 - 检查params key和参数
    #重定向地址不一致
    return JsonResponse({'code':200,'oauth_url':url})

def oauth_token(request):
    if request.method == 'GET':
        #获取code
        code = request.GET.get('code')
        #给微博服务器发请求　用授权码交换用户token
        token_url = 'https://api.weibo.com/oauth2/access_token'
        req_data = {
            'client_id':settings.WEIBO_CLIENT_ID,
            'client_secret':settings.WEIBO_CLIENT_SECRET,
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri':settings.WEIBO_REDIRECT_URI
        }
        response = requests.post(token_url,data=req_data)
        if response.status_code == 200:
            res_data = json.loads(response.text)
        else:
            print('change code error %s'%(response.status_code))
            return  JsonResponse({'code':10110,'error':'weibo error'})

        if res_data.get('error'):
            print('change error')
            print(res_data.get('error'))
            return JsonResponse({
                'code':10111,
                'error':'weibo error'
            })
        print('---weibo token is---')
        print(res_data)

        weibo_uid = res_data['uid']
        access_token = res_data['access_token']

        #先检查　该微博用户是否第一次进入到网站
        try:
            weibo_user = WeiboProfile.objects.get(wuid=weibo_uid)
        except Exception as e:
            #该用户第一次进入本站
            WeiboProfile.objects.create(access_token=access_token,wuid = weibo_uid)
            # 如果是第一次来，存储token,可能没有内部用户进行绑定－外键可以为空。
            # 给前端非200响应: 用户第一次进入本站。
            return JsonResponse({'code':201,'uid':weibo_uid})
        else:
            # 这个微博账号之前来过
            user = weibo_user.user_profile
            if user:
                # 1.执行过完整流程，完成了绑定注册
                token = make_token(user.username)
                return JsonResponse({'code':200,'username':user.username,'token':token.decode()})
            else:
                # 2.token来过但无绑定账号
                return JsonResponse({'code':201,'uid':weibo_uid})

    elif request.method == 'POST':
        #绑定注册
        data = json.loads(request.body)
        uid = data['uid']
        username=data['username']
        password = data['password']
        phone=data['phone']
        email = data['email']
        #检查用户名是否已存在
        users = UserProfile.objects.filter(username=username,is_active=True)
        if users:
            return JsonResponse({'code':10112,'error':'User already exists.'})
        m = hashlib.md5()
        m.update(password.encode())
        #创建内部用户&绑定微博用户(要用mysql的事务保证同时执行。)
        try:
            with transaction.atomic():
                user = UserProfile.objects.create(
                    username=username,
                    password=m.hexdigest(),
                    email=email,
                    phone=phone
                )
                weibo_user = WeiboProfile.objects.get(wuid=uid)
                weibo_user.user_profile = user
                weibo_user.save()
        except Exception as e:
            return JsonResponse({'code':10113,'error':'account bind/registration error'})
        #自动登录
        token = make_token(username)
        return JsonResponse({'code':200,'username':username,'token':token.decode()})

    return JsonResponse({'code':200})
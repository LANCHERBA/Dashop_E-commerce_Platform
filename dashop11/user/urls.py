from django.conf.urls import url

from . import views

urlpatterns = [
    #http://127.0.0.1:8000/v1/users
    url(r'^$',views.users),
    #http://127.0.0.1:8000/v1/users/activation
    url(r'^/activation$',views.user_active),
    #http://127.0.0.1:8000/v1/users/<username>/address
    url(r'^/(?P<username>\w{1,11})/address$',views.AddressView.as_view()),
    #http://127.0.0.1:8000/v1/users/<username>/address/<id>
    url(r'^/(?P<username>\w{1,11})/address/(?P<addressid>\d+)$',views.AddressView.as_view()),

    #微博相关(weibo authorization)
    #http://127.0.0.1:8000/v1/users/weibo/authorization
    url(r'^/weibo/authorization$',views.oauth_url),
    #http://127.0.0.1:8000/v1/users/weibo/users?xxxxx
    url(r'^/weibo/users$',views.oauth_token)
]
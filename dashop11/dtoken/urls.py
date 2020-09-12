from django.conf.urls import url

from dtoken import views

urlpatterns = [
    #http://127.0.0.1/v1/tokens
    url(r'^$',views.tokens)
]
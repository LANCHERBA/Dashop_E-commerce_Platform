"""dashop11 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test_cors$',views.test_cors),
    #分布式路由
    #http://127.0.0.1/v1/users
    url(r'^v1/users',include('user.urls')),
    #http://127.0.0.1/v1/tokens
    url(r'^v1/tokens',include('dtoken.urls')),
    #http://127.0.0.1/v1/goods
    url(r'^v1/goods',include('goods.urls')),
    url(r'^v1/carts',include('carts.urls')),
    url(r'^v1/orders',include('order.urls'))
]
#设置static方法，绑定MEDIA_URL和MEDIA_ROOT,
# 实现了127.0.0.1:8000/media/a.jpg请求到达django后，
# django去MEDIA_ROOT下找寻相应资源文件
# !!!只有在debug=True时生效，debug=False时需要在nginx中配置.
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

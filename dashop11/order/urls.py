from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/(?P<username>\w{1,11})/advance$',views.AdvanceView.as_view()),
    url(r'^/(?P<username>\w{1,11})$',views.OrderInfoView.as_view())
]
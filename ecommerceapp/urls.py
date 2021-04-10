
from django.urls import path,include
from ecommerceapp import views

urlpatterns = [
    path('',views.index,name='index')
]
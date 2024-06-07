
from django.contrib import admin
from django.urls import path
from bot.views import *

urlpatterns = [
    path('', chatbot, name = 'chatbot'),
    path('login', login, name = 'login'),
    path('register', register, name = 'register'),
    path('logout', logout , name = 'logout'),

]

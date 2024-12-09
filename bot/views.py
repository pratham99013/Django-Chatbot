from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
import os
from django.http import JsonResponse
from .models import Chat
import google.generativeai as genai
from django.utils import timezone
GOOGLE_API_KEY = 'AIzaSyDl1UJ0tCP7RBbz1rBWraQRiLyyJPP8kJM'

genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "hello\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Hello! How can I help you today? \n",
      ],
    },
  ]
)
def hello(message):
    response = chat_session.send_message(message)
    print(response.text)
    return response.text
 


# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel



  
def chatbot(request):
    if request.user.is_authenticated:
     chats = Chat.objects.filter(user=request.user)
    else:
     chats = None
     
    if request.method == 'POST':
        message = request.POST.get('message')
        response = hello(message)
        if request.user.is_authenticated:
         chat = Chat(user = request.user, message=message, response = response, created_at = timezone.now())
         chat.save()
         return JsonResponse({'message': message, 'response' : response })
        else:
          return JsonResponse({'message': message, 'response' : response })
    return render(request, 'chatbot.html', {'chats' : chats}) 


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
def register(request):
    if request.method == 'POST':
          username = request.POST['username']
          email = request.POST['email']
          password1 = request.POST['password1']
          password2 = request.POST['password2']
          if password1 == password2:
              try:
                  user = User.objects.create_user(username, email, password1)
                  user.save()
                  auth.login(request, user)
                  return redirect('login')
              except:
                      error_message = 'Error creating account'
                      return render(request, 'register.html', {'error_message': error_message})
          else:
              error_msg = 'Password did not match'
              messages.error(request, 'Please correct the errors below.')
              return render(request, 'register.html',{'error_msg' : error_msg} )
       
    return render(request, 'register.html')

def logout(request):
     auth.logout(request)
     return redirect('chatbot')
  

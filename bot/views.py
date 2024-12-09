import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Chat
import google.generativeai as genai


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyDl1UJ0tCP7RBbz1rBWraQRiLyyJPP8kJM') 
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
)

chat_session = model.start_chat(history=[])


def hello(message):
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Sorry, I couldn't process your request."


def chatbot(request):
    if request.user.is_authenticated:
        chats = Chat.objects.filter(user=request.user)
    else:
        chats = None

    if request.method == 'POST':
        message = request.POST.get('message', '')
        response = hello(message)
        if request.user.is_authenticated:
            Chat.objects.create(
                user=request.user, message=message, response=response, created_at=timezone.now()
            )
        return JsonResponse({'message': message, 'response': response})

    return render(request, 'chatbot.html', {'chats': chats})


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
                return redirect('chatbot')
            except Exception as e:
                error_message = 'Error creating account. Please try again.'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('chatbot')

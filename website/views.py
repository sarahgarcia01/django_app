from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm


from django.contrib.auth.decorators import login_required











def index(request):
    return render(request, 'website/index.html')



def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'website/register.html', {'form': form})


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return redirect('homepage')
    else:
        error = 'Invalid username or password'
        return render(request, 'website/login.html', {'error': error})
    
def logout(request):
    auth_logout(request)
    return redirect('index')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import connection
from django.db.utils import ProgrammingError


def register_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        return redirect('/login')
    context = {'form': form}
    return render(request, 'tenants/register.html', context=context)


def login_view(request):
    # is user already authenticated? check if already logged in and don't allow re-login.
    # add this to this function or add to template
    # future -> ?next=/articles/create
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm(request)
    return render(request, 'tenants/login.html', {'form': form })


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/login')
    return render(request, 'tenants/logout.html')


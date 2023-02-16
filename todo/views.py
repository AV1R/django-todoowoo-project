from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    return render(request, 'todo/home.html')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username or password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        # Create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                err = "The username has already been taken. Please choose a new username"
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': err})

        else:
            # Tell the user the passwords didn't match
            err = "Passwords didn't match"
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': err})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        # Manage errors
        try:
            # Create a todo object from TodoForm Data
            form = TodoForm(request.POST)
            # Commit makes a object who is assigned to newtodo
            newtodo = form.save(commit=False)
            # Make a todoobject linked with each user
            newtodo.user = request.user
            # Save the new TodoObject into database
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Bad data passed in. Try again.'})


@login_required
def currenttodos(request):
    # Get all todoObjects by current user and task isnt completed. (__isnull:To say isnt completed)
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(request):
    # Get all tdo object who is completed with __isnull=false
    todos = Todo.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos': todos})


@login_required
def viewtodo(request, todo_pk):
    # Get object by primary key, and belongs an user
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        # Get and instance a todo form
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            # Create a todo object and instance to todo current object
            form = TodoForm(request.POST, instance=todo)
            # Save the updated TodoObject into database
            form.save()
            return redirect('currenttodos')

        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad data passed in. Try again.'})


@login_required
def completetodo(request, todo_pk):
    # Get object by primary key, and belongs an user
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        # Modify todo object datecompleted
        todo.datecompleted = timezone.now()
        # Save modifications
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    # Get object by primary key, and belongs an user
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        # Delete object
        todo.delete()
        return redirect('currenttodos')

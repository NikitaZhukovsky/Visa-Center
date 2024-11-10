from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from app.forms import ApplicantForm, DocumentForm


def home(request):
    return render(request, template_name='home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'signup_user.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'signup_user.html',
                              {'form': UserCreationForm(), 'error': 'That username has already been taken.'})
        else:
            return render(request, 'signup_user.html', {'form': UserCreationForm(),
                                                        'error': 'Passwords did not match'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login_user.html', {'form': AuthenticationForm(),
                                                       'error': 'Username and password did not match'})
        else:
            login(request, user)
            return redirect('home')


def create_application(request):
    if request.method == 'GET':
        return render(request, 'create_applicant.html', {
            'form': ApplicantForm(),
            'document_form': DocumentForm()
        })
    else:
        form = ApplicantForm(request.POST)
        document_form = DocumentForm(request.POST, request.FILES)

        if form.is_valid() and document_form.is_valid():
            new_applicant = form.save(commit=False)
            new_applicant.user_id = request.user.id
            new_applicant.save()

            document = document_form.save(commit=False)
            document.save()

            return redirect('home')
        else:
            return render(request, 'create_applicant.html', {
                'form': form,
                'document_form': document_form,
                'error': 'Bad data passed in'
            })

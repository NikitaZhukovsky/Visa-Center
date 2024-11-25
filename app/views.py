from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from app.forms import ApplicantForm, DocumentForm, DocumentFormSet, PaymentForm
from app.models import Application, DocumentApplication, Document, Payment


def home(request):
    return render(request, 'home.html')


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


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login_user')


def create_application(request):
    if request.method == 'GET':
        return render(request, 'create_applicant.html', {
            'form': ApplicantForm(),
        })
    else:
        form = ApplicantForm(request.POST)

        if form.is_valid():
            new_applicant = form.save()
            new_application = Application(
                applicant=new_applicant,
                status='In processing',
                user=request.user
            )
            new_application.save()

            new_applicant.application_status_id = new_application.id
            new_applicant.save()

            document_count = 0
            while f'doc_type_{document_count}' in request.POST:
                doc_type = request.POST.get(f'doc_type_{document_count}')
                file = request.FILES.get(f'file_{document_count}')

                if doc_type and file:
                    document = Document(doc_type=doc_type, file=file)
                    document.save()
                    DocumentApplication.objects.create(
                        application=new_application,
                        document=document
                    )
                document_count += 1

            return redirect('all_applications')
        else:

            return render(request, 'create_applicant.html', {
                'form': form,
                'error': 'Bad data passed in',
                'form_errors': form.errors
            })


def all_applications(request):
    applications = Application.objects.filter(user=request.user).prefetch_related('documentapplication_set').select_related('payment_details')

    for application in applications:
        application.documents = application.documentapplication_set.all()

    return render(request, 'all_applications.html', {'applications': applications})


def payment_view(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if application.payment:
        messages.error(request, "Payment has already been made for this application.")
        return redirect('all_applications')

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.application = application
            payment.status = "Pending"
            payment.save()

            #
            application.payment = payment
            application.save()

            messages.success(request, "Payment successful!")
            return redirect('all_applications')
    else:
        form = PaymentForm()

    return render(request, 'payment.html', {'form': form, 'application': application})


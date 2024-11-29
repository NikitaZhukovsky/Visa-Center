import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from app.models import Applicant, Application, Document, DocumentApplication, Payment
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_create_application_post_valid(client):
    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    uploaded_file = SimpleUploadedFile("document.pdf", b"file_content", content_type="application/pdf")

    response = client.post(reverse('application'), {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'doc_type': 'Passport',
        'file': uploaded_file,
    }, follow=True)

    if hasattr(response, 'context') and 'form' in response.context:
        if response.context['form'].errors:
            print("Form errors:", response.context['form'].errors)

    assert response.status_code == 200

    assert Application.objects.count() == 1


@pytest.mark.django_db
def test_create_application_post_invalid(client):

    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    data = {
        'name': '',
        'email': 'john@example.com',
    }

    response = client.post(reverse('application'), data)

    assert response.status_code == 200
    assert Application.objects.count() == 0
    assert 'form' in response.context
    assert not response.context['form'].is_valid()
    assert 'Bad data passed in' in response.context['error']


@pytest.mark.django_db
def test_signup_user_success(client):
    response = client.post(reverse('signup_user'), {
        'username': 'testuser',
        'password1': 'password123',
        'password2': 'password123'
    })
    assert response.status_code == 302
    assert User.objects.filter(username='testuser').exists()
    assert response.url == reverse('home')


@pytest.mark.django_db
def test_signup_user_passwords_dont_match(client):
    response = client.post(reverse('signup_user'), {
        'username': 'testuser',
        'password1': 'password123',
        'password2': 'differentpassword'
    })
    assert response.status_code == 200
    assert 'Passwords did not match' in response.content.decode()


@pytest.mark.django_db
def test_login_user_success(client):
    User.objects.create_user(username='testuser', password='password123')
    response = client.post(reverse('login_user'), {
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 302
    assert response.url == reverse('home')


@pytest.mark.django_db
def test_login_user_invalid_credentials(client):
    User.objects.create_user(username='testuser', password='password123')
    response = client.post(reverse('login_user'), {
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    assert 'Username and password did not match' in response.content.decode()


@pytest.mark.django_db
def test_logout_user(client):
    user = User.objects.create_user(username='testuser', password='password123')
    client.login(username='testuser', password='password123')
    response = client.post(reverse('logout_user'))
    assert response.status_code == 302
    assert response.url == reverse('login_user')
    assert '_auth_user_id' not in client.session


@pytest.mark.django_db
def test_all_applications_view(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')

    applicant = Applicant.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='+1234567890'
    )

    application = Application.objects.create(
        applicant=applicant,
        status='In processing',
        user=user
    )

    Payment.objects.create(
        amount=100.00,
        status='Completed',
        application=application
    )

    document = Document.objects.create(
        doc_type='Passport',
        file='documents/passport.pdf'
    )

    DocumentApplication.objects.create(
        application=application,
        document=document
    )

    response = client.get(reverse('all_applications'))

    assert response.status_code == 200

    assert len(response.context['applications']) == 1


@pytest.mark.django_db
def test_payment_view_success(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')

    applicant = Applicant.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='1234567890'
    )
    application = Application.objects.create(
        applicant=applicant,
        status='In processing',
        user=user
    )

    response = client.post(reverse('payment', args=[application.id]), data={
        'amount': 100.00,
        'status': 'Pending'
    })

    payment = Payment.objects.get(application=application)
    assert payment.status == 'Pending'
    assert payment.amount == 100.00

    assert response.status_code == 302
    assert response.url == reverse('all_applications')

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].message == "Payment successful!"


@pytest.mark.django_db
def test_payment_view_already_paid(client):

    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')

    applicant = Applicant.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='1234567890'
    )
    application = Application.objects.create(
        applicant=applicant,
        status='In processing',
        user=user
    )

    Payment.objects.create(
        application=application,
        amount=100.00,
        status='Completed'
    )

    response = client.post(reverse('payment', args=[application.id]))

    assert response.status_code == 200



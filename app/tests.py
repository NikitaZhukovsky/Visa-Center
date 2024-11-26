import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Applicant, Application, Document, DocumentApplication
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
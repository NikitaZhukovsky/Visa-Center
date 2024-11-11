from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Applicant(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    application_status = models.OneToOneField('Application', on_delete=models.SET_NULL, null=True, blank=True,
                                              default=None,
                                              related_name='applicant_status')


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    doc_type = models.CharField(max_length=100, blank=False, null=False)
    file = models.FileField(upload_to='documents/')
    # application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='related_documents', default=None)

    def __str__(self):
        return f"Document {self.id} - Type: {self.doc_type}"


class Application(models.Model):
    id = models.AutoField(primary_key=True)
    STATUSES = (
        ('In processing', 'In processing'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )
    submission_date = models.DateTimeField(blank=False, null=False, default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUSES, blank=False, null=False)
    documents = models.ForeignKey(Document, blank=True, on_delete=models.CASCADE, related_name='applications',
                                  default=None)
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, related_name='application')
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='application_payment')
    operator = models.OneToOneField('Operator', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='application_operator')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant', null=True, blank=True)

    def __str__(self):
        return f"Application {self.id} - Status: {self.status}"





class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, blank=False, null=False)
    application = models.OneToOneField(Application, on_delete=models.CASCADE,
                                       related_name='payment_details')

    def __str__(self):
        return f"Payment {self.id} - Amount: {self.amount}"


class Operator(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False)
    access_level = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return f"Operator {self.id} - {self.first_name} {self.last_name}"


class Administrator(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False)
    access_level = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return f"Administrator {self.id} - {self.first_name} {self.last_name}"

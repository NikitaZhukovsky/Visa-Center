from django.contrib import admin
from app.models import Application, Applicant, Document, Payment, Operator, Administrator


class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'application_status']
    search_fields = ['first_name', 'last_name', 'phone']


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission_date', 'status', 'applicant', 'payment', 'operator']
    search_fields = ['status']


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'doc_type', 'file',]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'payment_date', 'status', 'application']


class OperatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'access_level']
    search_fields = ['fist_name', 'last_name']


class AdministratorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'access_level']
    search_fields = ['first_name', 'last_name']


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(Administrator, AdministratorAdmin)

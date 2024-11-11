from django.forms import ModelForm
from app.models import Applicant, Document


class ApplicantForm(ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'last_name', 'email', 'phone']


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'file']


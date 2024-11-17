from django.forms import ModelForm
from app.models import Applicant, Document, Payment
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory


class ApplicantForm(ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.istitle():
            raise ValidationError("First name must start with a capital letter.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.istitle():
            raise ValidationError("Last name must start with a capital letter.")
        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+'):
            raise ValidationError("Phone number must start with a '+' sign.")
        return phone


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'file']


DocumentFormSet = modelformset_factory(Document, form=DocumentForm, extra=1, can_delete=True)


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['amount']

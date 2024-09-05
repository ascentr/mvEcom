from django import forms
from .models import Vendor , OpeningHour
from accounts.validators import allow_only_images_validator

class VendorForm(forms.ModelForm):
    vendor_logo = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_logo']

    '''
    +++ NOTES ++++
    vendor_logo = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    when using ImageField custom validation does not work, django uses default validation for images use FileField when applying custom validator
    '''

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day' , 'from_hour' , 'to_hour' , 'is_closed']
from django import forms
from .models import Municipality

from django.contrib.auth.forms import UserCreationForm
from .models import customUser

class MunicipalityForm(forms.ModelForm):
    class Meta:
        model = Municipality
        fields = [
            "organization_name",
            "designation",
            "official_email",
            "phone",
            
            "state",
            "district",
            "city",
        
            "address",
            "verification_document",
        ]

        widgets = {
            "organization_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Enter organization name"
            }),

            "designation": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Example: Health Officer"
            }),

            "official_email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "official@example.gov.in"
            }),

            "phone": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Enter official phone number"
            }),
            
            
           "state": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Enter State"
            }),

            "district": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Enter District"
            }),

            "city": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Enter Municipality / City"
            }),

            "address": forms.Textarea(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-400 focus:border-green-400 outline-none transition",
                "placeholder": "Enter office address",
                "rows": 4
            }),

            "verification_document": forms.ClearableFileInput(attrs={
                "class": "block w-full text-sm text-gray-600 file:mr-4 file:py-3 file:px-5 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
            }),
        }




class OfficerRegistrationForm(UserCreationForm):

    class Meta:

        model = customUser

        fields = (
            "full_name",
            "username",
            "email",
            "phone",
            "password1",
            "password2",
        )       
        
        
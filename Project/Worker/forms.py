from django import forms
from UserAuth.models import customUser


class WorkerForm(forms.ModelForm):
    password = forms.CharField(
    widget=forms.PasswordInput(
        attrs={
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500",
            "placeholder": "Enter password"
        }
    )
)

    confirm_password = forms.CharField(
    widget=forms.PasswordInput(
        attrs={
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500",
            "placeholder": "Confirm password"
        }
    )
)

    

    ward = forms.CharField(
    widget=forms.TextInput(
        attrs={
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500",
            "placeholder": "Ward No."
        }
    )
)

    class Meta:
        model = customUser

        fields = [
            "full_name",
            "email",
            "phone",
            "address",
            "profile_picture",
        ]
        
        widgets = {
        "full_name": forms.TextInput(attrs={
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition",
            "placeholder": "Enter full name"
        }),

        "email": forms.EmailInput(attrs={
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition",
            "placeholder": "Enter email address"
        }),

        "phone": forms.TextInput(attrs={
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition",
            "placeholder": "Enter phone number"
        }),

        "address": forms.Textarea(attrs={
            "rows": 4,
            "class": "w-full border border-gray-300 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none transition",
            "placeholder": "Enter address"
        }),

        "profile_picture": forms.ClearableFileInput(attrs={
            "class": "hidden",
            "id": "id_profile_picture"
        }),
    }
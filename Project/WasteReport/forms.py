from django import forms 
from .models import WasteReport

class wasteReportForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = [
        "title",
        "waste_type",
        "description",
        "image",
        "urgency_level",
        "landmark",

        "latitude",
        "longitude",

        "state",
        "district",
        "city",
        "full_address",
    ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["state"].widget.attrs.update({
            "readonly": True
        })

        self.fields["district"].widget.attrs.update({
            "readonly": True
        })

        self.fields["city"].widget.attrs.update({
            "readonly": True
        })

        self.fields["full_address"].widget.attrs.update({
            "readonly": True
        })    
        
class wasteReportUpdateForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = [
            'status'
        ]       
                 
        
        
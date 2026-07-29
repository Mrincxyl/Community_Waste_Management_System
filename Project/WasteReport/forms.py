from django import forms 
from .models import WasteReport

class wasteReportForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = [
            'title',
            'waste_type',   
            'description',
            'image',
            'urgency_level',
            'landmark',
            'latitude',
            'longitude',
            ]
        
class wasteReportUpdateForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = [
            'status'
        ]       
                 
        
        
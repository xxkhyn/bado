# core/forms.py
from django import forms
from .models import MagazineIssue

class MagazineUploadForm(forms.ModelForm):
    class Meta:
        model = MagazineIssue
        fields = ["title", "issue_month", "pdf", "is_public"]
        widgets = {
            "issue_month": forms.DateInput(attrs={"type": "date"}),
        }

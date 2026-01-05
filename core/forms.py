from django import forms
from django.conf import settings
from .models import MagazineIssue, User

class MagazineUploadForm(forms.ModelForm):
    class Meta:
        model = MagazineIssue
        fields = ["title", "issue_month", "pdf", "is_public"]
        widgets = {
            "issue_month": forms.DateInput(attrs={"type": "date"}),
        }

class ProfileForm(forms.ModelForm):
    secret_code = forms.CharField(
        label="運営用合言葉",
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "運営になる場合のみ入力"}),
        help_text="運営(Officer)を選択する場合は合言葉が必要です。"
    )

    class Meta:
        model = User
        fields = ["role"]
        widgets = {
            "role": forms.RadioSelect(choices=[
                (User.Role.MEMBER, "一般"),
                (User.Role.OFFICER, "運営"),
            ]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].label = "役職を選択してください"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        secret_code = cleaned_data.get("secret_code")

        if role == User.Role.OFFICER:
            if secret_code != settings.OFFICER_SECRET_CODE:
                self.add_error('secret_code', "合言葉が間違っています。")
        
        return cleaned_data

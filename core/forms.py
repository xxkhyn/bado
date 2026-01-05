from django import forms
from .models import MagazineIssue, User

class MagazineUploadForm(forms.ModelForm):
    class Meta:
        model = MagazineIssue
        fields = ["title", "issue_month", "pdf", "is_public"]
        widgets = {
            "issue_month": forms.DateInput(attrs={"type": "date"}),
        }

class ProfileForm(forms.ModelForm):
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
        # フォーム上の表示ラベルを分かりやすく調整
        self.fields['role'].label = "役職を選択してください"

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
        label="運営用の合言葉",
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "運営になる場合のみ入力"}),
        help_text="運営を選ぶ場合は合言葉が必要です。",
    )

    class Meta:
        model = User
        fields = ["grade", "experience_years", "faculty", "role"]
        labels = {
            "grade": "学年",
            "experience_years": "経験年数",
            "faculty": "所属学部",
            "role": "役職",
        }
        widgets = {
            "grade": forms.Select(attrs={"class": "form-control"}),
            "experience_years": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 99}),
            "faculty": forms.Select(attrs={"class": "form-control"}),
            "role": forms.RadioSelect(choices=[
                (User.Role.MEMBER, "一般"),
                (User.Role.OFFICER, "運営"),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["grade"].choices = [("", "未設定")] + list(User.Grade.choices)
        self.fields["faculty"].choices = [("", "未設定")] + list(User.Faculty.choices)
        self.fields["grade"].required = True
        self.fields["faculty"].required = True
        self.fields["experience_years"].required = True
        self.fields["role"].label = "役職を選択してください"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        secret_code = cleaned_data.get("secret_code")
        experience_years = cleaned_data.get("experience_years")

        if experience_years is not None and experience_years > 99:
            self.add_error("experience_years", "経験年数は99年以下で入力してください。")

        if role == User.Role.OFFICER and secret_code != settings.OFFICER_SECRET_CODE:
            self.add_error("secret_code", "合言葉が間違っています。")

        return cleaned_data

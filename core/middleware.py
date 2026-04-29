from django.shortcuts import redirect
from django.urls import reverse


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and not user.is_staff:
            path = request.path
            allowed_prefixes = (
                "/accounts/",
                "/admin/",
                "/healthz/",
                "/media/",
                "/static/",
            )
            profile_path = reverse("profile_edit")

            if (
                path != profile_path
                and not path.startswith(allowed_prefixes)
                and not user.is_circle_profile_complete
            ):
                return redirect("profile_edit")

        return self.get_response(request)

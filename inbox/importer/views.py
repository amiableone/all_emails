from django.contrib.auth.forms import UserCreationForm
from django.http import (
    HttpRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView

from . import models
from .forms import AddAccountForm
from .utils import (
    google_oauth2,
    google_oauth2_cb,
)


def go_to_emails(*args, **kwargs):
    return redirect(reverse("importer:emails"))


class SignupView(CreateView):
    form_class = UserCreationForm
    success_url = "/login/"
    template_name = "importer/signup.html"


class EmailsView(ListView):
    context_object_name = "emails"
    paginate_by = 100
    template_name = "importer/emails.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("importer:login"))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = models.Message.objects.filter(account__user=user)
        return qs


class AddAccountView(View):
    form_class = AddAccountForm
    template_name = "importer/add_account.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            platform = form.cleaned_data["platform"]
            email = form.cleaned_data["email"]
            request.session["platform"] = platform
            request.session["email_account"] = email
            return HttpResponseRedirect(reverse("importer:add-gmail"))
        return render(request, self.template_name, {"form": form})


class GoogleAuthView(View):
    def get(self, request, *args, **kwargs):
        # email is set in AddAccountView.
        email = request.session["email_account"]
        # Tell Google's OAuth2.0 server to redirect to redirect_uri
        # on user consent being granted.
        request: HttpRequest
        redirect_uri = request.build_absolute_uri(
            reverse("importer:complete-google-oauth")
        )
        auth_url, state = google_oauth2(email, redirect_uri)
        # Pass state as session parameter to protect from CSRF by passing
        # the parameter value from CompleteGoogleAuthView.get(), which
        # will handle the redirect back from the Google's OAuth2.0
        # server, to Flow object constructor.
        request.session["state"] = state
        request.session.modified = True
        return HttpResponseRedirect(auth_url)


class CompleteGoogleAuthView(View):
    def get(self, request, *args, **kwargs):
        # This method will be called on request from Google OAuth2.0
        # server after successful authentication.
        request: HttpRequest
        state = request.session["state"]
        redirect_uri = request.build_absolute_uri(
            reverse("importer:complete-google-oauth")
        )
        auth_resp = request.build_absolute_uri()
        credentials = google_oauth2_cb(state, redirect_uri, auth_resp)
        request.session["credentials"] = credentials
        return HttpResponseRedirect(reverse("importer:create-gmail"))


class CreateAccountView(CreateView):
    model = models.Account
    fields = ["platform", "email", "credentials"]
    success_url = "/emails/"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.post(self, request, *args, **kwargs)
        return HttpResponseRedirect(reverse("importer:login"))

    def post(self, request, *args, **kwargs):
        # platform and email values are set in AddAccountView.
        # credentials is set in CompleteGoogleAuthView.
        platform = request.session["platform"]
        email = request.session["email_account"]
        credentials = request.session["credentials"]
        form = self.get_form_class(
            {
                "platform": platform,
                "email": email,
                "credentials": credentials,
            }
        )
        user = request.user
        if form.is_valid():
            form.instance.user = user
            form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect(
                # in the AddAccountView.get() render a form with an error
                # message about failed authentication.
                reverse("importer:add-account", kwargs={"email": email})
            )

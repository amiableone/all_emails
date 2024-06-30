from django.http import (
    HttpRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView

from . import models
from .utils import (
    google_oauth2,
    google_oauth2_cb,
)


class GoogleAuthView(View):
    def get(self, request, *args, **kwargs):
        # email is set in AddAccountView.
        email = request.session["email_account"]
        # Tell Google's OAuth2.0 server to redirect to redirect_uri
        # on user consent being granted.
        redirect_uri = reverse("importer:complete-google-oauth")
        auth_url, state = google_oauth2(email, redirect_uri)
        # Pass state as session parameter to protect from CSRF by passing
        # the parameter value from CompleteGoogleAuthView.get(), which will
        # handle the redirect back from the Google's OAuth2.0 server, to
        # Flow object constructor.
        request.session["state"] = state
        request.session.modified = True
        return HttpResponseRedirect(auth_url)


class CompleteGoogleAuthView(View):
    def get(self, request, *args, **kwargs):
        request: HttpRequest
        state = request.session["state"]
        redirect_uri = reverse("importer:complete-google-oauth")
        auth_resp = request.resolver_match
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

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
        # session["email_account"] is set to email provided by the user
        # via the form handled by AddAccountView.
        login = request.session["email_account"]
        # Tell Google's OAuth2.0 server to redirect to redirect_uri
        # on user consent being granted.
        redirect_uri = reverse("importer:complete-google-oauth")
        auth_url, state = google_oauth2(login, redirect_uri)
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


class CreateGmailAccount(CreateView):
    model = models.Account
    fields = ["credentials"]
    success_url = None  # to be provided.

    def post(self, request, *args, **kwargs):
        # session["email_account"] is set to email provided by the user
        # via the form handled by AddAccountView.
        email = request.session["email_account"]
        credentials = request.session["credentials"]
        form = self.get_form_class(
            {
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
                # telling that the authentication failed.
                reverse("importer:add-account", kwargs={"email": email})
            )

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

appname = "importer"
urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="importer/login.html"),
        name="login",
    ),
    path("emails/", views.EmailsView.as_view(), name="emails"),
    path(
        "add-account/",
        views.AddAccountView.as_view(),
        name="add-account",
    ),
    path("add-gmail/", views.GoogleAuthView.as_view(), name="add-gmail"),
    path(
        "google-oauth-cb/",
        views.CompleteGoogleAuthView.as_view(),
        name="complete-google-oauth",
    ),
    path("create-gmail/", view.CreateAccount.as_view(), name="create-gmail" ),
]
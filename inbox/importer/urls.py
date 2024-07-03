from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "importer"
urlpatterns = [
    path("", views.go_to_emails, name="root"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            next_page="/emails/",
            template_name="importer/login.html",
        ),
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
    path(
        "create-gmail/",
        views.CreateAccountView.as_view(),
        name="create-gmail" ,
    ),
]
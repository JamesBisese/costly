from django.urls import re_path

from authtools import views


urlpatterns = [
    re_path(
        r'^login/$',
        views.LoginView.as_view(),
        name='login'
    ),
    re_path(
        r'^logout/$'
        , views.LogoutView.as_view(),
        name='logout'
    ),
    re_path(
        r'^password_change/$',
        views.PasswordChangeView.as_view(),
        name='password_change'
    ),
    re_path(
        r'^password_change/done/$',
        views.PasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),
    re_path(
        r'^password_reset/$',
        views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    re_path(
        r'^password_reset/done/$',
        views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    re_path(
        r'^reset/done/$',
        views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
    re_path(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
]

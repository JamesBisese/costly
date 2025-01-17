
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib import messages
from authtools import views as authviews
from braces import views as bracesviews
from django.conf import settings
from . import forms

User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin,
                authviews.LoginView):
    template_name = "accounts/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        redirect = super().form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            ONE_MONTH = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", ONE_MONTH)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    url = reverse_lazy('home')


class SignUpView(bracesviews.AnonymousRequiredMixin,
                 bracesviews.FormValidMessageMixin,
                 generic.CreateView):
    form_class = forms.SignupForm
    model = User
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:administrator-will-respond')
    form_valid_message = "You're registered!"

    # found: https://stackoverflow.com/questions/50893917/django-allauth-signup-prevent-login
    # def form_valid(self, form):
    #     # By assigning the User to a property on the view, we allow subclasses
    #     # of SignupView to access the newly created User instance
    #     self.user = form.save(self.request)
    #     try:
    #         signals.user_signed_up.send(
    #             sender=self.user.__class__,
    #             request=self.request,
    #             user=self.user,
    #             **{}
    #         )
    #         return HttpResponseRedirect(self.get_success_url())
    #     except ImmediateHttpResponse as e:
    #         return e.response

    def form_valid(self, form):
        r = super().form_valid(form)
        # username = form.cleaned_data["email"]
        # password = form.cleaned_data["password1"]
        # # user = auth.authenticate(email=username, password=password)
        # # auth.login(self.request, user)
        # send_mail(
        #     'User Registered: ' + username,
        #     'Please check the website and validate the new user account for ' + username,
        #     'gsicosttool@gmail.com',
        #     ['james.bisese@tetratech.com'],
        #     fail_silently=False,
        #     auth_user=getattr(settings, "EMAIL_HOST_USER", None),
        #     auth_password=getattr(settings, "EMAIL_HOST_PASSWORD", None),
        # )
        return r

class AdministratorWillRespondView(authviews.PasswordResetDoneView):
    template_name = 'accounts/administrator_will_respond.html'

class PasswordChangeView(authviews.PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please relogin")
        return super().form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'accounts/password-reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/emails/password-reset-email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/password-reset-done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = 'accounts/password-reset-confirm.html'
    form_class = forms.SetPasswordForm

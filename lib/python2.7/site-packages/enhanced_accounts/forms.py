from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Fieldset, Layout, HTML, Field
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.core.urlresolvers import reverse

from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from crispy_forms.helper import FormHelper

attrs_dict = { 'class': 'required' }

class EnhancedRegistrationForm(RegistrationFormUniqueEmail):
    '''
    We need to enhance generic form in django-registration to add crispy and hide username
    '''

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Registration',
                'email',
                'password1',
                'password2',
                'username',
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='button btn-primary'),

            )
        )
        super(EnhancedRegistrationForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_username(self):
        "This function is required to overwrite an inherited username clean"
        return self.cleaned_data['username']

    def clean(self):
        if not self.errors:
            self.cleaned_data['username'] = '%s%s' % (self.cleaned_data['email'].split('@',1)[0], User.objects.count())

        MIN_LENGTH = 6
        original_password = self.cleaned_data['password1']
        if len(original_password) < MIN_LENGTH:
            raise forms.ValidationError("Password too short (requires 6 or more characters).")

        super(EnhancedRegistrationForm, self).clean()
        return self.cleaned_data


class EnhancedLoginForm(AuthenticationForm):
    '''
    We need to enhance generic login form in django-auth to add crispy and change login label
    '''
    username = forms.CharField(label="Email", max_length=30)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Log In',
                'username',
                'password',
            ),
            HTML("<div class='control-group'><div class='controls'><a href={% url auth_password_reset %}>Forgot password?</a></div></div>"),
            FormActions(
                Submit('submit', 'Submit', css_class='button btn-primary'),

            ),
	    HTML("<div class='control-group'><div class='controls'><a href={% url socialauth_begin 'facebook'%}><img src='/static/img/facebook-logo.png'></a> <a href={% url socialauth_begin 'google'%}><img src='/static/img/google-logo.png'></a></div></div>"),

        )
        super(EnhancedLoginForm, self).__init__(*args, **kwargs)

class EnhancedLoginMiniForm(AuthenticationForm):
    '''
    We need to enhance generic login form in django-auth to add crispy and change login label
    '''
    username = forms.CharField(label="Email", max_length=30)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Fieldset(
               'Log In',
            ),
            Field('username',  css_class="input-medium", title="Explanation"),
            Field('password',  css_class="input-medium", title="Explanation"),
            HTML("<div style='padding-bottom:10px;'><input type='submit' class='btn btn-primary'></div>"),
            HTML("<div class='control-group'><div class='controls'><a href={% url socialauth_begin 'facebook'%}><img src='/static/img/facebook-logo.png'></a></div></div>"),
            HTML("<div class='control-group'><div class='controls'><a href={% url socialauth_begin 'google'%}><img src='/static/img/google-logo.png'></a></div></div>")
        )
        self.helper.form_action = reverse('auth_login')
        super(EnhancedLoginMiniForm, self).__init__(*args, **kwargs)

class EnhancedPasswordResetForm(PasswordResetForm):
    '''
    We need to enhance generic login form in django-auth to add crispy
    '''
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Reset password',
                'email',
            ),

            FormActions(
                Submit('submit', 'Submit', css_class='button btn-primary'),

            )
        )
        super(EnhancedPasswordResetForm, self).__init__(*args, **kwargs)


class EnhancedSetPasswordForm(SetPasswordForm):
    '''
    We need to enhance generic login form in django-auth to add crispy
    '''
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Set new password',
                'new_password1',
                'new_password2',
            ),

            FormActions(
                Submit('submit', 'Submit', css_class='button btn-primary'),

            )
        )
        super(EnhancedSetPasswordForm, self).__init__(*args, **kwargs)

class EnhancedPasswordChangeForm(PasswordChangeForm):
    '''
    We need to enhance generic login form in django-auth to add crispy
    '''
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Change password',
                'old_password',
                'new_password1',
                'new_password2',
            ),

            FormActions(
                Submit('submit', 'Submit', css_class='button btn-primary'),

            )
        )
        super(EnhancedPasswordChangeForm, self).__init__(*args, **kwargs)

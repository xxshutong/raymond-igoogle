from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from webcontent.core import utils
from webcontent.core.models import Member
from webcontent.core.utils import wrap_email

class RegisterUserForm(forms.Form):

    handle = forms.RegexField(max_length=50, regex=r'^[\w.@+-]+$', widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'User''s Handler'}),
        error_messages = {'invalid': u"Required. 50 characters or fewer. Letters, numbers and @/./+/-/_ characters."})
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Confirm Password'}))
    tos = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    def clean_handle(self):
        """
        Validate that the supplied handler is unique for the
        site.
        """
        handle = self.cleaned_data["handle"]
        try:
            Member.objects.get(handle=handle)
        except Member.DoesNotExist:
            return handle
        raise forms.ValidationError(u'Handle already exists.')

    def clean_email(self):
        """
        Validate that the supplied email is unique for the
        site.

        """
        email = wrap_email(self.cleaned_data['email'])
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError((u'Email already exists.'))
        return email

    def clean_password2(self):
        """
        Validate that password and password2 is the same.

        """
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError(u"Two of the input password is not consistent.")
        return password2

    def clean_tos(self):
        """
        Validate that the user accepted the Terms of Service.

        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(u'You must agree before continue.')

    @transaction.commit_on_success
    def save(self, **new_data):
        #create user
        username = utils.generate_base64_string(new_data['email'])
        user = User.objects.create_user(username, new_data['email'], new_data['password'])
        user.is_active = False
        user.save()

        #create member
        Member.objects.create(user = user, type = 0, handle = new_data['handle'])
        return user

class RegisterAuthorForm(forms.Form):

    handle = forms.RegexField(max_length=50, regex=r'^[\w.@+-]+$', widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Author''s Handler'}),
        error_messages = {'invalid': u"Required. 50 characters or fewer. Letters, numbers and @/./+/-/_ characters."})
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Email Address'}))
    paypal = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Paypal Account Name'}))
    gst_hst = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'GST/HST Number (optional)'}), required=False)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Confirm Password'}))
    tos = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    def clean_handle(self):
        """
        Validate that the supplied handler is unique for the
        site.

        """
        handle = self.cleaned_data["handle"]
        try:
            Member.objects.get(handle=handle)
        except Member.DoesNotExist:
            return handle
        raise forms.ValidationError(u'Handle already exists.')

    def clean_email(self):
        """
        Validate that the supplied email is unique for the
        site.

        """
        email = wrap_email(self.cleaned_data['email'])
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError((u'Email already exists.'))
        return email

    def clean_password2(self):
        """
        Validate that password and password2 is the same.

        """
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError(u"Two of the input password is not consistent.")
        return password2

    def clean_tos(self):
        """
        Validate that the user accepted the Terms of Service.

        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(u'You must agree before continue.')

    @transaction.commit_on_success
    def save(self, **new_data):
        #create user
        username = utils.generate_base64_string(new_data['email'])
        user = User.objects.create_user(username, new_data['email'], new_data['password'])
        user.is_active = False
        user.save()

        #create member
        del new_data['email']
        del new_data['password']
        del new_data['password2']
        del new_data['tos']
        Member.objects.create(user = user, type = 1, **new_data)
        return user

class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Password'}))

class AccountSettingForm(RegisterAuthorForm):
    """
    Used to update account settings
    """
    member_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_handle(self):
        """
        Validate that the supplied handler is unique for the
        site.

        """
        cur_member = Member.objects.get(pk=self.data['member_id'])
        handle = self.cleaned_data["handle"]
        try:
            member = Member.objects.get(handle=handle)
            if member.handle == cur_member.handle:
                return handle
        except Member.DoesNotExist:
            return handle
        raise forms.ValidationError(u'Handle already exists.')

    def clean_email(self):
        """
        Validate that the supplied email is unique for the
        site.

        """
        cur_member = Member.objects.get(pk=self.data['member_id'])
        email = wrap_email(self.cleaned_data['email'])
        try:
            user = User.objects.get(email__iexact=email)
            if user.email == cur_member.user.email:
                return email
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(u'Email already exists.')

    def clean_tos(self):
        pass

    @transaction.commit_on_success
    def save(self, **new_data):
        #update user
        member = Member.objects.get(pk=new_data['member_id'])
        if member.type == 1:
            member.paypal = new_data['paypal']
            member.gst_hst = new_data['gst_hst']
        member.handle = new_data['handle']
        member.user.email = new_data['email']
        member.user.set_password(new_data['password'])
        member.user.save()
        member.save()
        return member

class AdminLoginForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'User Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-large', 'placeholder': 'Password'}))

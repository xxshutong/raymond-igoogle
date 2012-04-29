import datetime
import random
from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.forms.models import ModelForm
from webcontent.core.models import UserProfile, Tab, TabGadgetsR
from webcontent.core.utils import wrap_email

class RegisterUserForm(ModelForm):
    class Meta:
        model = UserProfile

    def __init__(self, *args, **kwargs):
        self.base_fields['full_name'].widget.attrs.update({'placeholder': 'Full Name'})
        self.base_fields['birthday'].widget.attrs.update({'placeholder': 'Birthday', 'readonly':'true'})
        self.base_fields['ic_num'].widget.attrs.update({'placeholder': 'IC Number'})
        super(RegisterUserForm, self).__init__(*args, **kwargs)

    username = forms.RegexField(max_length=30, regex=r'^[\w.@+-]+$', widget=forms.TextInput(attrs={'placeholder': 'User name'}),
        error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Confirm Password'}))
    tos = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("A user with that username already exists.")

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
        user = User.objects.create_user(new_data['username'], new_data['email'], new_data['password'])
        user.save()

        #create member
        del new_data['email']
        del new_data['password']
        del new_data['password2']
        del new_data['tos']
        del new_data['user']
        del new_data['username']
        UserProfile.objects.create(user = user,  created_at = datetime.datetime.now(), updated_at = datetime.datetime.now(), **new_data)
        return user


class LoginForm(forms.Form):

    username = forms.RegexField(max_length=30, regex=r'^[\w.@+-]+$', widget=forms.TextInput(attrs={'placeholder': 'User name'}),
        error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    password = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'input-large', 'placeholder': 'Password'}))

class TabForm(ModelForm):
    class Meta:
        model = Tab
        exclude = ('user_profile', 'order')

    def __init__(self, *args, **kwargs):
        self.base_fields['name'].widget.attrs.update({'placeholder': 'Tab Name'})
        super(TabForm, self).__init__(*args, **kwargs)

class TabGadgetsRForm(ModelForm):
    class Meta:
        model = TabGadgetsR
        fields = ('tab', 'gadget', 'title')

    def __init__(self, *args, **kwargs):
        self.base_fields['title'].widget.attrs.update({'placeholder': 'Gadget Title'})
        super(TabGadgetsRForm, self).__init__(*args, **kwargs)

    @transaction.commit_on_success
    def save(self, **new_data):
        tgr = TabGadgetsR()
        tgr.gadget_id = new_data['gadget']
        tgr.tab_id = new_data['tab']
        tgr.title = new_data['title']
        column = random.uniform(1, 3)
        tgr.save()
        return tgr

class AccountSettingForm(RegisterUserForm):
#    """
#    Used to update account settings
#    """
#    member_id = forms.IntegerField(widget=forms.HiddenInput())
#
#    def clean_handle(self):
#        """
#        Validate that the supplied handler is unique for the
#        site.
#
#        """
#        cur_member = Member.objects.get(pk=self.data['member_id'])
#        handle = self.cleaned_data["handle"]
#        try:
#            member = Member.objects.get(handle=handle)
#            if member.handle == cur_member.handle:
#                return handle
#        except Member.DoesNotExist:
#            return handle
#        raise forms.ValidationError(u'Handle already exists.')
#
#    def clean_email(self):
#        """
#        Validate that the supplied email is unique for the
#        site.
#
#        """
#        cur_member = Member.objects.get(pk=self.data['member_id'])
#        email = wrap_email(self.cleaned_data['email'])
#        try:
#            user = User.objects.get(email__iexact=email)
#            if user.email == cur_member.user.email:
#                return email
#        except User.DoesNotExist:
#            return email
#        raise forms.ValidationError(u'Email already exists.')
#
#    def clean_tos(self):
#        pass
#
#    @transaction.commit_on_success
#    def save(self, **new_data):
#        #update user
#        member = Member.objects.get(pk=new_data['member_id'])
#        if member.type == 1:
#            member.paypal = new_data['paypal']
#            member.gst_hst = new_data['gst_hst']
#        member.handle = new_data['handle']
#        member.user.email = new_data['email']
#        member.user.set_password(new_data['password'])
#        member.user.save()
#        member.save()
#        return member
    pass

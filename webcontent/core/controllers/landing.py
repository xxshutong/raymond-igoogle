import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
import logging
from webcontent import settings
from webcontent.core import models, utils
from webcontent.core.forms.forms import RegisterUserForm, RegisterAuthorForm, LoginForm
from django.contrib.auth import login as djlogin
from django.contrib.auth import logout as djlogout
from webcontent.settings import SITE_DOMAIN, REQUIRE_ENCRYPTED_REQUESTS

DASHBOARD_PAGE = 'dashboard.html'
LOGIN_PAGE = 'login.html'
REGISTER_USER_PAGE = 'register_user.html'
REGISTER_AUTHOR_PAGE = 'register_author.html'
REGISTER_SUCCESS_PAGE = 'register_success.html'
MEMBER_DASHBOARD_PAGE = 'member_dashboard.html'

def dashboard(request):
    """
    Nav to dashboard page
    """
    return render_to_response(DASHBOARD_PAGE, {},
        RequestContext(request,
                {
            }),
    )

def login(request):
    """
    User & Author Login
    """
    errors = ''
    login_error_message = "Please enter a correct email and password."

    if request.method == 'GET':
        form = LoginForm()
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            #Authenticate user
            user = authenticate(username=utils.generate_base64_string(form.cleaned_data['email']),
                password=form.cleaned_data['password'])
            if user:
                if user.is_active:
                    if not user.is_staff and not user.is_superuser:
                        djlogin(request, user)
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                        return render_to_response(MEMBER_DASHBOARD_PAGE, {},
                            RequestContext(request,
                                    {
                                }),
                        )
                    else:
                        errors = login_error_message
                else:
                    errors = "Your account is not activated yet, please check your email to verify."
            else:
                errors = login_error_message
        else:
            errors = login_error_message


    return render_to_response(LOGIN_PAGE, {},
        RequestContext(request,
                {
                'form':form,
                'errors':errors
            }),
    )

def logout(request):
    """
    Logs user out.
    """
    djlogout(request)
    return redirect('/')

def register_user(request):
    """
    User Registration
    """
    if request.method == 'GET':
        form = RegisterUserForm()
    else:
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(**form.cleaned_data)
            is_success = send_active_email(user)
            return render_to_response(REGISTER_SUCCESS_PAGE, {},
                RequestContext(request,
                        {
                        'is_author':False,
                        'email': user.email,
                        'is_success': is_success
                    }),
            )
    return render_to_response(REGISTER_USER_PAGE, {},
        RequestContext(request,
                {
                'form':form
            }),
    )

def register_author(request):
    """
    Author Registration
    """
    if request.method == 'GET':
        form = RegisterAuthorForm()
    else:
        form = RegisterAuthorForm(request.POST)
        if form.is_valid():
            user = form.save(**form.cleaned_data)
            is_success = send_active_email(user)
            return render_to_response(REGISTER_SUCCESS_PAGE, {},
                RequestContext(request,
                        {
                        'is_author':True,
                        'email': user.email,
                        'is_success': is_success
                    }),
            )
    return render_to_response(REGISTER_AUTHOR_PAGE, {},
        RequestContext(request,
                {
                'form':form
            }),
    )

def register_verify(request, user_id=None, token=None):
    form = LoginForm()
    if user_id and token:
        try:
            active_token = models.ActiveToken.objects.filter(user__id=user_id).latest('created_at')
            if active_token and active_token.token == token:
                now = datetime.datetime.now()
                timedelta = now.date() - active_token.created_at.date()
                active_token.delete()
                user = User.objects.get(id=user_id)
                if user:
                    if timedelta.days < settings.EMAIL_EXPIRE_TIME:
                        user.is_active = True
                        user.save()
                        return render_to_response(LOGIN_PAGE, {}, RequestContext(request,
                                    {
                                    'info': 'success',
                                    'form': form
                                }
                            )
                        )
                    else:
                        is_success = send_active_email(user)
                        return render_to_response(LOGIN_PAGE, {}, RequestContext(request,
                                    {
                                    'info': 'resend',
                                    'form': form,
                                    'email_again': is_success
                                }
                            )
                        )
        except ObjectDoesNotExist:
            logging.error('DoesNotExist: Member matching query does not exist.')
    return render_to_response('404.html', {}, RequestContext(request, {}))





def send_active_email(user):
    """
    Send email for active account
    """
    token = utils.generate_valid_string()
    now = datetime.datetime.now()
    active_token = models.ActiveToken(user=user, token=token, created_at=now, updated_at=now)
    active_token.save()

    url = "%s%s/verify/member/%s/%s/" % ('https://' if REQUIRE_ENCRYPTED_REQUESTS else 'http://', SITE_DOMAIN, user.id, token)
    return utils.send_email((utils.register_mail_template % (url, url, settings.EMAIL_EXPIRE_TIME) ), user.email, u'Welcome to StockTrenz')
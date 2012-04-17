from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils import simplejson
from webcontent import settings
from webcontent.core.forms.forms import RegisterUserForm, LoginForm, TabForm
from django.contrib.auth import login as djlogin
from django.contrib.auth import logout as djlogout
from webcontent.core.models import Tab

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
    login_error_message = "Please enter a correct username and password."

    if request.method == 'GET':
        form = LoginForm()
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            #Authenticate user
            user = authenticate(username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            if user:
                if user.is_active:
                    if not user.is_staff and not user.is_superuser:
                        djlogin(request, user)
                        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                        return go_member_dashboard(request)
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

def go_member_dashboard(request):
    tab_form = TabForm()
    tab_list = Tab.objects.filter(user_profile=request.user).order_by('order')
    return render_to_response(MEMBER_DASHBOARD_PAGE, {},
        RequestContext(request,
                {
                'tab_form': tab_form,
                'tab_list': tab_list
            }),
    )

def add_tab(request):
    '''
    Add a new tab
    '''
    instance = Tab()
    instance.user_profile = request.user
    tab_from = TabForm(request.POST, instance=instance)
    if tab_from.is_valid():
        tab_from.save()
    return go_member_dashboard(request)

def delete_tab(request):
    '''
    Delete selected tab
    '''
    tab_id = request.POST.get('selected_tab', None)
    tab = Tab.objects.get(pk=tab_id)
    tab.delete()
    return go_member_dashboard(request)

def ajax_check_name(request):
    '''
    Check tab name is unique for one person
    '''
    success = False
    name = request.GET.get('name', None)
    try:
        Tab.objects.get(user_profile=request.user, name__iexact=name)
    except Tab.DoesNotExist:
        success = True
    data = {'success': success}
    data = simplejson.dumps(data)
    return HttpResponse(data, 'application/json')


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
            return render_to_response(REGISTER_SUCCESS_PAGE, {},
                RequestContext(request,
                        {
                        'is_author':False,
                        'email': user.email,
                    }),
            )
    return render_to_response(REGISTER_USER_PAGE, {},
        RequestContext(request,
                {
                'form':form
            }),
    )


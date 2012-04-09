from django.contrib.auth import authenticate
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from webcontent import settings
from webcontent.core.forms.forms import AdminLoginForm
from django.contrib.auth import login as djlogin
from django.contrib.auth import logout as djlogout
from django.contrib.auth.decorators import login_required, permission_required

ADMIN_LOGIN_PAGE = 'admin/admin_login.html'
ADMIN_DASHBOARD_PAGE = 'admin/admin_dashboard.html'

def login(request):
    """
    Admin Login
    """
    user = request.user
    if user.is_active and user.is_staff:
        return redirect('/admin/dashboard/')

    errors = ''
    login_error_message = "Please enter a correct user and password."

    if request.method == 'GET':
        form = AdminLoginForm()
    else:
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            #Authenticate user
            user = authenticate(username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            if user:
                if user.is_active and user.is_staff and user.is_superuser:
                    djlogin(request, user)
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    return redirect('/admin/dashboard/')
            else:
                errors = login_error_message
        else:
            errors = login_error_message

    return render_to_response(ADMIN_LOGIN_PAGE, {},
        RequestContext(request,
                {
                'form':form,
                'errors':errors
            }),
    )

def logout(request):
    """
    Logs admin user out.
    """
    djlogout(request)
    return redirect('/admin/')

@login_required
@permission_required('polls.can_vote')
def dashboard(request):
    """
    Admin dashboard
    """
    return render_to_response(ADMIN_DASHBOARD_PAGE, {},
        RequestContext(request,
                {

            }),
    )


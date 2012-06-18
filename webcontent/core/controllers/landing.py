import random
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models.aggregates import Max, Count
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils import simplejson
from webcontent import settings
from webcontent.core import models
from webcontent.core.forms.forms import RegisterUserForm, LoginForm, TabForm, TabGadgetsRForm
from django.contrib.auth import login as djlogin
from django.contrib.auth import logout as djlogout
from webcontent.core.models import Tab, TabGadgetsR

DASHBOARD_PAGE = 'dashboard.html'
LOGIN_PAGE = 'login.html'
REGISTER_USER_PAGE = 'register_user.html'
REGISTER_AUTHOR_PAGE = 'register_author.html'
REGISTER_SUCCESS_PAGE = 'register_success.html'
MEMBER_DASHBOARD_PAGE = 'member_dashboard.html'
MEMBER_GADGET_PAGE = 'member_gadgets.html'
MEMBER_SEARCH_PAGE = 'member_search_badget.html'

MEMBER_GADGET_FRAME_PAGE = 'member_gadgets_frame.html'

def dashboard(request):
    """
    Nav to dashboard page
    """
    latest_tabs = models.Tab.objects.filter().order_by('-created_at')[:20]
    url_pre = 'http://' + request.META["HTTP_HOST"] + '/tab/show_detail/'
    return render_to_response(DASHBOARD_PAGE, {},
        RequestContext(request,
                {

                'latest_tabs': latest_tabs,
                'url_pre': url_pre
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
    latest_tabs = models.Tab.objects.filter().order_by('-created_at')[:20]
    url_pre = 'http://' + request.META["HTTP_HOST"] + '/tab/show_detail/'
    return render_to_response(MEMBER_DASHBOARD_PAGE, {},
        RequestContext(request,
                {
                'tab_form': tab_form,
                'tab_list': tab_list,
                'latest_tabs': latest_tabs,
                'url_pre': url_pre
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

def search_gadget(request):
    tab_form = TabForm()
    tag_gadget_form = TabGadgetsRForm()
    tab_list = Tab.objects.filter(user_profile=request.user).order_by('order')
    gadgets = models.Gadgets.objects.filter().order_by('type')
    return render_to_response(MEMBER_SEARCH_PAGE, {},
        RequestContext(request,
                {
                'tag_gadget_form': tag_gadget_form,
                'tab_list': tab_list,
                'gadgets': gadgets,
                'tab_form': tab_form
            }),
    )

def add_gadget(request):
    '''
    Add gadget to selected tab
    '''
#    tab_id = request.POST.get('gadget_tab')
#    tag_gadget_form = TabGadgetsRForm(request.POST)
#    if tag_gadget_form.is_valid():
    tgr = TabGadgetsR()
    tgr.gadget_id = request.POST['gadget']
    tgr.tab_id = request.POST['tab']
    tgr.title = request.POST['title']
    tgr.rss_url = request.POST['rss_url']
    existing_rs = models.TabGadgetsR.objects.filter(tab=tgr.tab_id).values('column').annotate(row_count = Count('id')).order_by('row_count')
    if len(existing_rs) == 3:
        column = existing_rs[0].get('column')
    elif len(existing_rs) == 2:
        column = 3
    elif len(existing_rs) == 1:
        column = 2
    else:
        column = 1
    row = models.TabGadgetsR.objects.filter(tab=tgr.tab_id, column=column).aggregate(Max('row'))
    tgr.column = column
    tgr.row = row.get('row__max') + 1 if row.get('row__max') else 1
    tgr.save()
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

def show_detail(request, tab_id=None):
    """
    Show tab gadget list
    """
    tab_form = TabForm()
    if request.user.is_active:
        tab_list = Tab.objects.filter(user_profile=request.user).order_by('order')
    else:
        tab_list = ''
    domain_prefix = 'http://' + request.META["HTTP_HOST"]
    return render_to_response(MEMBER_GADGET_PAGE, {},
        RequestContext(request,
                {
                'tab_form': tab_form,
                'tab_list': tab_list,
                'domain_prefix': domain_prefix,
                'tab_id': tab_id
            }),
    )

def show_detail_frame(request, tab_id=None):
    tab_gadget1_list = models.TabGadgetsR.objects.filter(tab__id=tab_id, column=1)
    tab_gadget2_list = models.TabGadgetsR.objects.filter(tab__id=tab_id, column=2)
    tab_gadget3_list = models.TabGadgetsR.objects.filter(tab__id=tab_id, column=3)
    return render_to_response(MEMBER_GADGET_FRAME_PAGE, {},
        RequestContext(request,
                {
                'tab_gadget1_list': tab_gadget1_list,
                'tab_gadget2_list': tab_gadget2_list,
                'tab_gadget3_list': tab_gadget3_list
            }),
    )

def ajax_change_title(request, tab_gadget_id=None, new_title=None):
    tab_gadget = models.TabGadgetsR.objects.get(pk=tab_gadget_id)
    tab_gadget.title = new_title
    tab_gadget.save()
    return HttpResponse('', 'application/json')

def ajax_change_color(request, tab_gadget_id=None, new_color=None):
    tab_gadget = models.TabGadgetsR.objects.get(pk=tab_gadget_id)
    tab_gadget.color_class = new_color
    tab_gadget.save()
    return HttpResponse('', 'application/json')

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


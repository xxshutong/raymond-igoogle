from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from webcontent import settings
from webcontent.core import models, utils
from webcontent.core.forms import forms
from webcontent.core.forms.forms import AccountSettingForm
from webcontent.settings import SITE_DOMAIN, REQUIRE_ENCRYPTED_REQUESTS

EMAIL_SETTINGS_PAGE = 'member_email.html'
ACCOUNT_SETTINGS_PAGE = 'member_account.html'

@login_required
def email_settings(request, show_success = False):
    """
    Go to Edit email settings
    """
    member = models.Member.objects.get(user=request.user)
    is_favourite = member.e_favourite
    is_author = member.e_authors
    is_none = member.e_none

    favourite_authors = models.FavouriteAuthor.objects.filter(member__user=request.user)
    selected_author_list = []
    for favourite_author in favourite_authors:
        selected_author = {}
        selected_author['id'] = favourite_author.author.id
        selected_author['handle'] = favourite_author.author.handle
        selected_author_list.append(selected_author)

    return render_to_response(EMAIL_SETTINGS_PAGE, {},
        RequestContext(request,
                {
                'active_menu': 'email_settings',
                'selected_author_list': selected_author_list,
                'is_favourite': is_favourite,
                'is_author': is_author,
                'is_none':is_none,
                'show_success': show_success
            }
        ),
    )

@login_required
def account_settings(request):
    """
    Go to Edit account settings
    """
    show_success = False
    member = models.Member.objects.get(user=request.user)
    if request.method == 'GET':
        form = forms.AccountSettingForm(initial={'member_id': member.id, 'handle':member.handle, 'email':member.user.email,
                        'paypal':member.paypal, 'gst_hst':member.gst_hst, 'password': None, 'password2': None})
    else:
        form = AccountSettingForm(request.POST)
        if form.is_valid():
            member = form.save(**form.cleaned_data)
            #        is_success = send_active_email(user)
            show_success = True

    return render_to_response(ACCOUNT_SETTINGS_PAGE, {},
        RequestContext(request,
                {
                'active_menu': 'account_settings',
                'form': form,
                'is_author': (member.type == 1),
                'show_success': show_success
            }
        ),
    )

@login_required
def ajax_get_author_handle(request):
    """
    returns data displayed at autocomplete list -
    this function is accessed by AJAX calls
    """
    limit = 10
    query = request.GET.get('q', None)
    # it is up to you how query looks
    kwargs = {}
    if query:
        kwargs['handle__istartswith'] = query
    kwargs['type'] = 1
    kwargs['is_auth_active'] = True

    instances = models.Member.objects.filter(**kwargs).order_by('handle')[:limit]

    data = {}
    data['keys'] = [member.id for member in instances]
    data['values'] = [member.handle for member in instances]

    data = simplejson.dumps(data)
    return HttpResponse(data, 'application/json')



@login_required
def update_email_settings(request):
    """
    Update email settings
    """
    keys = request.GET.get('keys', None)
    is_favourite = utils.str2bool(request.GET.get('favourite', None))
    is_author = utils.str2bool(request.GET.get('author', None))
    is_none = utils.str2bool(request.GET.get('none', None))

    member = models.Member.objects.filter(user = request.user)[0]
    member.e_authors = is_author
    member.e_favourite = is_favourite
    member.e_none = is_none
    member.save()

    # Update member's favourite authors
    author_ids = keys.split(',')
    models.FavouriteAuthor.objects.filter(member__id=member.id).exclude(author__pk__in=author_ids).delete()
    for author_id in author_ids:
        try:
            models.FavouriteAuthor.objects.get(member__id=member.id, author__id=author_id)
        except ObjectDoesNotExist:
            favourite_author = models.FavouriteAuthor(member_id=member.id, author_id=author_id)
            favourite_author.save()
    return email_settings(request, True)

def send_active_email(user):
    """
    Send email for active account
    """
    token = utils.generate_valid_string()
    active_token = models.ActiveToken(user=user, token=token)
    active_token.save()

    url = "%s%s/verify/member/%s/%s/" % ('https://' if REQUIRE_ENCRYPTED_REQUESTS else 'http://', SITE_DOMAIN, user.id, token)
    return utils.send_email((utils.register_mail_template % (url, url, settings.EMAIL_EXPIRE_TIME) ), user.email, u'Welcome to StockTrenz')
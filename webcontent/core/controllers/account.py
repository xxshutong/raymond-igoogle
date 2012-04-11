from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from webcontent.core import models
from webcontent.core.forms import forms
from webcontent.core.forms.forms import AccountSettingForm

EMAIL_SETTINGS_PAGE = 'member_email.html'
ACCOUNT_SETTINGS_PAGE = 'member_account.html'


@login_required
def account_settings(request):
    """
    Go to Edit account settings
    """
    show_success = False
    member = models.UserProfile.objects.get(user=request.user)
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

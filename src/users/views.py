from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

# list of Users accessed from Audit page

# @login_required
# def audit_users(request):
#     context_data = {'title': 'Audit Users',
#                     'header': 'Audit Users'}
#     context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
#     return render(request, 'audit/user.html', context_data)

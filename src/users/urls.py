from django.conf.urls import url
from django.urls import path, include

from users.views import audit_users

"""
    this tag makes all the urls reverse into 'users:{name}'
"""
app_name = 'users'

urlpatterns = [

    # Project CRUD
    path(r'audit/users/', audit_users, name='audit_users'),

]

urlpatterns += [
	url(r'^select2/', include('django_select2.urls')),
]

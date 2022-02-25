from django.urls import re_path
from django.urls import path, include

"""
    this tag makes all the urls reverse into 'users:{name}'
"""
app_name = 'users'

urlpatterns = [
]

urlpatterns += [
	re_path(r'^select2/', include('django_select2.urls')),
]

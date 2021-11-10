from django.conf.urls import url
from django.urls import path, include

"""
    this tag makes all the urls reverse into 'users:{name}'
"""
app_name = 'users'

urlpatterns = [
]

urlpatterns += [
	url(r'^select2/', include('django_select2.urls')),
]

from django.urls import path, include, re_path
from django.conf.urls import url

import sys

from . import views

"""
    this tag makes all the urls reverse into 'scenario:{name}'
"""
app_name = 'users'

urlpatterns = [

    # Project CRUD
    path(r'users/', views.UsersPage.as_view(), name='users'),

    # a list of all the Structure - Cost Item Default Assumptions in the database
    # path(r'cost_item/default_equations/', views.CostItemDefaultEquationsList.as_view(), name='costitems_default_equations'),
    # path(r'cost_item/default_factors/', views.CostItemDefaultFactorsList.as_view(), name='costitems_default_factors'),

]

urlpatterns += [
	url(r'^select2/', include('django_select2.urls')),
]

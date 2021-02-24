from django.shortcuts import render
from django.views import generic

# list of Users accessed from Audit page

class UsersPage(generic.TemplateView):
    template_name = "users/user_list.html"
    def get_context_data(self, **kwargs):
        context_data = super(UsersPage, self).get_context_data(**kwargs)

        context_data['title'] = 'Users'
        context_data['header_2'] = 'Audit Users'

        return context_data

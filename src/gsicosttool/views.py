from django.views import generic
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomePage(generic.TemplateView):
    """
        this is the home page accessed from the left-side menu items
    """
    template_name = "gsicosttool/home.html"


"""
    these are the pages accessed from the right-side menu items
"""


@method_decorator(staff_member_required, name='dispatch')
class HelpPage(generic.TemplateView):
    template_name = "gsicosttool/help.html"


@method_decorator(login_required, name='dispatch')
class InstructionsPage(generic.TemplateView):
    template_name = "gsicosttool/instructions.html"


@method_decorator(login_required, name='dispatch')
class ReferencePage(generic.TemplateView):
    template_name = "gsicosttool/reference.html"


@method_decorator(staff_member_required, name='dispatch')
class AuditPage(generic.TemplateView):
    template_name = "gsicosttool/audit.html"


@method_decorator(staff_member_required, name='dispatch')
class AboutPage(generic.TemplateView):
    template_name = "gsicosttool/about.html"


@method_decorator(staff_member_required, name='dispatch')
class ScopePage(generic.TemplateView):
    template_name = "gsicosttool/scope.html"


@method_decorator(staff_member_required, name='dispatch')
class WhyPage(generic.TemplateView):
    template_name = "gsicosttool/why.html"


class SetupPage(generic.TemplateView):
    template_name = "gsicosttool/setup.html"

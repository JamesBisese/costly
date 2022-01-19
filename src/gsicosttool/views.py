from django.views import generic


class HomePage(generic.TemplateView):
    """
        this is the home page accessed from the left-side menu items
    """
    template_name = "gsicosttool/home.html"


"""
    these are the pages accessed from the right-side menu items
"""


class HelpPage(generic.TemplateView):
    template_name = "gsicosttool/help.html"


class InstructionsPage(generic.TemplateView):
    template_name = "gsicosttool/instructions.html"


class ReferencePage(generic.TemplateView):
    template_name = "gsicosttool/reference.html"


class AuditPage(generic.TemplateView):
    template_name = "gsicosttool/audit.html"


class AboutPage(generic.TemplateView):
    template_name = "gsicosttool/about.html"


class ScopePage(generic.TemplateView):
    template_name = "gsicosttool/scope.html"


class WhyPage(generic.TemplateView):
    template_name = "gsicosttool/why.html"


class SetupPage(generic.TemplateView):
    template_name = "gsicosttool/setup.html"

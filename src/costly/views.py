from django.views import generic

'''
    this is the home page accessed from the left-side menu items
'''
class HomePage(generic.TemplateView):
    template_name = "costly/home.html"

'''
    these are the pages accessed from the right-side menu items
'''
class HelpPage(generic.TemplateView):
    template_name = "costly/help.html"

class InstructionsPage(generic.TemplateView):
    template_name = "costly/instructions.html"

class ReferencePage(generic.TemplateView):
    template_name = "costly/reference.html"

class AuditPage(generic.TemplateView):
    template_name = "costly/audit.html"

class AboutPage(generic.TemplateView):
    template_name = "costly/about.html"

class ScopePage(generic.TemplateView):
    template_name = "costly/scope.html"

class WhyPage(generic.TemplateView):
    template_name = "costly/why.html"

class SetupPage(generic.TemplateView):
    template_name = "costly/setup.html"

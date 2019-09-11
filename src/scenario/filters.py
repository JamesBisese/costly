import django_filters

from .models import Scenario

class ActivityFilter(django_filters.FilterSet):
	class Meta:
		model = Scenario
		fields = ['user']

	#TODO
	# person = django_filters.(name='person', initial='')
	# equipment = django_filters.CharFilter(name='equipment', initial='')

from django.core.management.base import BaseCommand
from scenario.models import CostItemDefaultCosts


class Command(BaseCommand):
    """
    one-off to set the new field value_numeric to the old field rsmeans_va
    """
    help = 'Tool to update CostItemDefaultCosts table.'

    def handle(self, *args, **options):
        for c in CostItemDefaultCosts.objects.all():
            if c.rsmeans_va is not None:
                c.value_numeric = c.rsmeans_va
                c.save()

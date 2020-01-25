from django.test import TestCase
from .models import CostItem
from django.contrib.auth import get_user_model
# Create your tests here.

class CostItemTestCase(TestCase):
    def setUp(self):
       CostItem.objects.create(code='swale', name="Swale Test", units="SF", help_text="Swale Test Help Test")
       CostItem.objects.create(code='lake', name="Lake Test", units="SF", help_text="Lake Test Help Test")

    def test_cost_item_exists(self):
        swale = CostItem.objects.get(code='swale')
        lake = CostItem.objects.get(code='lake')
        self.assertEqual(swale.name, "Swale Test")
        self.assertEqual(lake.name, "Lake Test")
from django.contrib import admin

from .models import Scenario, Structures, \
    CostItem, CostItemDefaultFactors, CostItemDefaultCosts, CostItemDefaultEquations

# admin.site.register(Location)
admin.site.register(Scenario)


class StructuresAdmin(admin.ModelAdmin):
    list_display = ('sort_nu', 'classification', 'name')
    list_display_links = ('name',)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    def has_delete_permission(self, request, obj=None):
        return False


class CostItemAdmin(StructuresAdmin):
    list_display = ('sort_nu', 'name')
    list_display_links = ('name',)
    pass

def costitem_sort_nu(obj):
    return obj.costitem.sort_nu
costitem_sort_nu.short_description = 'CostItem Sort No'
def costitem_name(obj):
    return ("%s" % (obj.costitem.name))
costitem_name.short_description = 'CostItem Name'

class CostItemDefaultCostsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name)
    list_display_links = (costitem_name,)
    pass

class CostItemDefaultEquationsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name)
    list_display_links = (costitem_name,)
    pass

admin.site.register(Structures, StructuresAdmin)
admin.site.register(CostItem, CostItemAdmin)
admin.site.register(CostItemDefaultFactors)
admin.site.register(CostItemDefaultCosts, CostItemDefaultCostsAdmin)
admin.site.register(CostItemDefaultEquations, CostItemDefaultEquationsAdmin)
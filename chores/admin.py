from django.contrib import admin

from chores.models import Household, Membership


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'access_code', 'member_count', 'created_at')
    search_fields = ('name', 'access_code')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'household', 'joined_at')
    list_filter = ('household',)
    search_fields = ('user__username', 'household__name')

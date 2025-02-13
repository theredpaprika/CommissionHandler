from django.contrib import admin
from .models import Account, Journal, Entry, AccountType, AccountSubtype


# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    search_fields = ['account_code', 'name', 'account_type', 'account_subtype']
    def get_queryset(self, request):
        return Account.objects.all()


class JournalAdmin(admin.ModelAdmin):
    search_fields = ['date','reference']
    def get_queryset(self, request):
        return Journal.objects.all()


class EntryAdmin(admin.ModelAdmin):
    search_fields = ['account_code', 'journal']
    def get_queryset(self, request):
        return Entry.objects.all()


class AccountTypeAdmin(admin.ModelAdmin):
    search_fields = ['account_type_code','name']


class AccountSubtypeAdmin(admin.ModelAdmin):
    search_fields = ['account_subtype_code','name']


admin.site.register(Account, AccountAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(AccountSubtype, AccountSubtypeAdmin)
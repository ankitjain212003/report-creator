from django.contrib import admin
from .models import Company

# Register your models here.
# admin.site.register(Company)
# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'sector', 'receive_date', 'internal')
#     list_filter = ('category', 'sector', 'internal')
#     search_fields = ('name', 'address', 'hash_value')
#     list_display = ('name',)
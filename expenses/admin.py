from django.contrib import admin
from .models import Expense, Category
# Register your models here.

class ExpensesAdmin(admin.ModelAdmin):
    list_display = (
            'amount',
            'date',
            'description',
            'owner',
            'category'
    )
    search_fields = (
            'amount',
            'description',
            'category'
    )
    list_per_page = 5
admin.site.register(Expense, ExpensesAdmin)
admin.site.register(Category)


from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path('', views.index, name='expenses'),
    path('add-expense', views.add_expense, name='add-expenses'),
    path('edit-expense/<int:id>', views.edit_expense, name='edit-expenses'),
    path('delete-expense/<int:id>', views.delete_expense, name='delete-expenses'),
    path('search-expenses/', csrf_exempt(views.search_expense), name='search-expenses'),
    path('expense_category_summary', views.expense_category_summary, name='expense_category_summary'),
    path('stats_expense', views.stats_expense_view, name='stats_expense'),
    path('expense-export-csv', views.export_csv, name='expense-export-csv'),
    path('expense-export-excel', views.export_excel, name='expense-export-excel'),
]
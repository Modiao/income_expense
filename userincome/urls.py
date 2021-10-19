
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path('', views.index, name='incomes'),
    path('add-income/', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.edit_income, name='edit-income'),
    path('delete-income/<int:id>', views.delete_income, name='delete-income'),
    path('search-income/', csrf_exempt(views.search_income), name='search-income'),
    path('income_source_summary/', views.income_source_summary, name='income_source_summary'),
    path('stats_income', views.stats_income_view, name='stats_income'),
    path('income-export-csv', views.export_csv, name='income-export-csv'),
]
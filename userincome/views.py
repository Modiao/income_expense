from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse

from userpreferences.models import UserPreference

from .models import Source, UserIncome

# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    incomes = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    print(page_obj)
    currency = UserPreference.objects.get(user=request.user)
    context = {
        'incomes': incomes,
        "page_obj": page_obj,
        "currency": currency.currency,
    }
    return render(request, 'userincome/index.html', context)

def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'userincome/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        if not amount:
            messages.error(request, "amount is required")
            return render(request, 'userincome/add_income.html', context)
        if not description:
            messages.error(request, "description is required")
            return render(request, 'userincome/add_income.html', context)
        if not source:
            messages.error(request, "source is required")
            return render(request, 'userincome/add_income.html')
        if not date:
            messages.error(request, "date is required")
            return render(request, 'userincome/add_income.html', context)
        
        UserIncome.objects.create(owner=request.user, amount=amount, description=description, source=source, date=date)
        messages.success(request, "income created succesfully")

        return redirect('incomes')


def edit_income(request, id):   
    sources = Source.objects.all()
    income = UserIncome.objects.get(id=id)
    context = {'income': income, "values": income, "sources": sources}
    if request.method == 'GET':
        return render(request, 'userincome/edit_income.html', context)
    
    if request.method == 'POST':
        income = UserIncome.objects.get(pk=id)
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        if not amount:
            messages.error(request, "amount is required")
            return render(request, 'userincome/add_income.html', context)
        if not source:
            messages.error(request, "source is required")
            return render(request, 'userincome/add_income.html')
        
        income.owner=request.user
        income.amount=amount
        income.description=description
        income.source=source
        income.date=date
        income.save()
        messages.info(request, 'income update successfully')
        return redirect('incomes')

def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'income deleted successfully')

    return redirect('incomes')

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        print(search_str)
        incomes = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | \
            UserIncome.objects.filter(date__istartswith=search_str) | \
            UserIncome.objects.filter(description__icontains=search_str, owner=request.user) | \
            UserIncome.objects.filter(source__icontains=search_str, owner=request.user)
        data = incomes.values()
        return JsonResponse(list(data), safe=False)
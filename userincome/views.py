from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
import datetime
import csv
import xlwt

from userpreferences.models import UserPreference
from .models import Source, UserIncome

# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    incomes = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user)
        currency = currency.currency
    except UserPreference.DoesNotExist:
        currency = "setup the currency"
    context = {
        'incomes': incomes,
        "page_obj": page_obj,
        "currency": currency,
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

def income_source_summary(request):
    print("they call me")
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user,
                    date__gte=six_months_ago, date__lte=todays_date)
    
    def get_source(incomes):
        return incomes.source
    
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        sources = incomes.filter(source=source)
        for items in sources:
            amount += items.amount
        return amount

    finalrep = {}

    for x in incomes:
        for s in source_list:
            finalrep[s] =  get_income_source_amount(s)
    
    return JsonResponse({"income_source_data": finalrep}, safe=False)


def stats_income_view(request):
    if request.method == 'GET':
        return render(request, 'userincome/stats.html')

def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Income_' + \
            str(datetime.datetime.now().strftime("%d-%m-%Y")) + ".csv"
        
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])

    incomes = UserIncome.objects.filter(owner=request.user)

    for income in incomes:
        writer.writerow([income.amount, income.description, \
            income.source, income.date])
    
    return response


def export_excel(request):

    response = HttpResponse(content_type='text/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=expense_' + \
        str(datetime.datetime.now()) + '.excel'

    wb  = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('incomes')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    colums = ['Amount', 'Description', 'Source', 'Date']

    for colum in range(len(colums)):
        ws.write(row_num, colum, colums[colum], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = UserIncome.objects.filter(owner=request.user).values_list('amount', 'description', 'source', 'date' )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum


from userpreferences.models import UserPreference
from .models import Category, Expense

# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user)
        currency = currency.currency
    except UserPreference.DoesNotExist:
        currency = "setup the currency"
    context = {
        'expenses': expenses,
        "page_obj": page_obj,
        "currency": currency,
    }
    return render(request, 'expenses/index.html', context)

def add_expense(request):
    category = Category.objects.all()
    context = {
        'categories': category,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        print(description)
        category = request.POST.get('category')
        date = request.POST.get('expense_date')
        if not date:
            messages.error(request, "date is required")
            return render(request, 'expenses/add_expense.html', context)
        if not amount:
            messages.error(request, "amount is required")
            return render(request, 'expenses/add_expense.html', context)
        if not description:
            messages.error(request, "description is required")
            return render(request, 'expenses/add_expense.html')
        
        Expense.objects.create(owner=request.user, amount=amount, description=description, category=category, date=date)
        messages.success(request, "Expense created succesfully")

        return redirect('expenses')


def edit_expense(request, id):
    categories = Category.objects.all()
    expense = Expense.objects.get(pk=id)
    context = {'expense': expense, "values": expense, "categories": categories}
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    
    if request.method == 'POST':
        expense = Expense.objects.get(pk=id)
        context = {'expense': expense, "values": expense, "categories": categories}
        
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        print(description)
        category = request.POST.get('category')
        date = request.POST.get('expense_date')
        if not amount:
            messages.error(request, "amount is required")
            return render(request, 'expenses/add_expense.html', context)
        if not description:
            messages.error(request, "description is required")
            return render(request, 'expenses/add_expense.html')
        
        expense.owner=request.user
        expense.amount=amount
        expense.description=description
        expense.category=category
        expense.date=date
        expense.save()
        messages.info(request, 'Expense update successfully')
        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'expense deleted successfully')

    return redirect('expenses')

def search_expense(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        print(search_str)
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | \
            Expense.objects.filter(date__istartswith=search_str) | \
            Expense.objects.filter(description__icontains=search_str, owner=request.user) | \
            Expense.objects.filter(category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_expense_view(request):
    if request.method == "GET":
        return render(request, 'expenses/stats.html')



def export_csv(request):

    response  = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expense_' + \
        str(datetime.datetime.now().strftime("%d/%m/%Y")) + ".csv"

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description,\
            expense.category, expense.date])
    
    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel') 
    response['Content-Disposition'] = 'attachment; filename=Expense_' + \
        str(datetime.datetime.now().strftime("%d/%m/%Y")) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    colums = ['Amount', 'Description', 'Category', 'Date']

    for colum in range(len(colums)):
        ws.write(row_num, colum, colums[colum], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date' )
    print("rows")
    print(rows)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Expense_' + \
        str(datetime.datetime.now().strftime("%d/%m/%Y")) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)

    sum = expenses.aggregate(Sum('amount'))

    html_string  = render_to_string('expenses/pdf-output.html', 
                {'expenses': expenses, 'total': sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response

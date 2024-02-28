from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .forms import Calculator,YourForm,newonef
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import pandas as pd
from django.contrib import messages
import numpy as np
from django.contrib import messages
from django.shortcuts import redirect, render
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from persiantools import digits
#from .models import Food

# Create your views here.

es1 = Elasticsearch(['address of elasticsearch1'], http_auth=('es1_user', 'es1_password'), timeout=50)
es2 = Elasticsearch(['address of elasticsearch2'], http_auth=('es2_user', 'es2_password'), timeout=50)


def etesal(context, index, name, fields, in_index=False):  #connect to elasticsearch and search index
    s = Search(using=es1, index=index)
    s = s.params(size=1000)
    response = s.execute()
    hits = response.to_dict()['hits']['hits']
    df = pd.DataFrame(hits)
    new_df = pd.DataFrame.from_records(df['_source'])
    new_df = new_df[fields].dropna().reset_index(drop=True)
    if in_index:
        new_df.insert(0, 'index', new_df.index)
    context[name] = new_df.values.tolist()


def get_index_from_es2(self, index_name): #get index from es2
        scroll_size = 10000
        data = []
        resp = es2.search(
            index=index_name,
            scroll='2m',
            size=scroll_size,
            body={"query": {"match_all": {}}}
        )
        while len(resp['hits']['hits']) > 0:
            data += [hit['_source'] for hit in resp['hits']['hits']]
            resp = self.es2.scroll(scroll_id=resp['_scroll_id'], scroll='2m')
        print("Fetched %d documents from %s" % (len(data), index_name))
        output = pd.DataFrame.from_dict(data)
        output = output.fillna(np.nan).replace([np.nan], [None])
        return output

def conver_csv_to_dict(context, path, name, fields, in_index=False): #convert index to csv
    df = pd.read_csv(path)
    df = df[fields].head(1000).dropna().reset_index(drop=True)
    if in_index:
        df.insert(0, 'index', df.index)
    context[name] = df.values.tolist()


def group_and_aggregate(df, groups, index, operation):
    if operation == "sum":
        grouped_data = df.groupby(groups)[index].sum().reset_index()
    elif operation == 'max':
        grouped_data = df.groupby(groups)[index].max().reset_index()
    else:
        grouped_data = df.groupby(groups)[index].mean().reset_index()
    return grouped_data


def groupby_and_aggregate(context, name, groups, index, operation, years):
    df = pd.DataFrame(context[name])
    if years:
        for year in years:
            year_df = df[df[0] == year]
            grouped_data = group_and_aggregate(year_df, groups, index, operation)
            context[f"{name}_{year}"] = grouped_data[index].tolist()
    else:
        grouped_data = group_and_aggregate(df, groups, index, operation)
        context[name] = grouped_data[index].tolist()


def remove(context, name, ind, fields, in_index=False):
    df = pd.DataFrame(context[name])
    df = df[~df[ind].isin(fields)].reset_index(drop=True)
    if in_index:
        df.pop(df.columns[0])
        df.insert(0, 'index', df.index)
    context[name] = df.values.tolist()


def remove_of(context, name, ind):
    df = pd.DataFrame(context[name])
    df = df[df.iloc[:, ind] != ""].reset_index(drop=True)
    context[name] = df.values.tolist()

def round(context, name, ind):
    df = pd.DataFrame(context[name])
    df[ind] = df[ind].round(decimals=0)  # یا هر تعداد اعشاری که مایلید
    context[name] = df.values.tolist()  # تبدیل دیتافریم به لیست جهت ارسال به قالب HTML

def remove_duplicates(context, name):
    df = pd.DataFrame(context[name])
    df = df.drop_duplicates()
    context[name] = df.values.tolist()

def remove_negatives(context, name, ind):
    df = pd.DataFrame(context[name])
    df[ind] = df[ind].apply(lambda x: x if x >= 0 else pd.NaT)
    df = df.dropna(subset=[ind])
    context[name] = df.values.tolist()
    


def range_of(context, name, start_range, end_range, index, in_index=False):
    df = pd.DataFrame(context[name])
    df = df.loc[(df.iloc[:, index] >= start_range) & (df.iloc[:, index] <= end_range)].reset_index(drop=True)
    if in_index:
        df.pop(df.columns[0])
        df.insert(0, 'index', df.index)
    context[name] = df.values.tolist()




def format_with_commas(context, name, fields): 
    df = pd.DataFrame(context[name])
    df.iloc[:, fields] = df.iloc[:, fields].apply(pd.to_numeric, errors='coerce')
    df = df.dropna().reset_index(drop=True)
    df[df.columns[fields]] = df[df.columns[fields]].astype(int)
    df.iloc[:, fields] = df.iloc[:, fields].applymap('{:,.0f}'.format)
    context[name] = df.values.tolist()






def remove_last_digit(context, name, fields):
    df = pd.DataFrame(context[name])
    df[df.columns[fields]] = df[df.columns[fields]].astype(int)
    df.iloc[:, fields] = df.iloc[:, fields].apply(lambda x: x.astype(str).str[:-1])

    context[name] = df.values.tolist()


def search_predict(request):
    if request.method=='POST':
        form=dict(request.POST)
        form.pop('csrfmiddlewaretoken')

def index(request):
    context = {}

    return render(request,
                  '/var/www/django-soft-ui-dashboard-master/env/lib/python3.9/site-packages/admin_soft/templates/admin/index.html',
                  context)


def control(request):
    context = {}
    s = Search(using=es1, index='akharin_gheymat_kharid')
    s = s.params(size=1000)
    response = s.execute()

    hits = response.to_dict()['hits']['hits']

    # Iterate through results
    value = []
    for hit in hits:
        value.append([hit['_id'], hit['_source']['kalaname'], hit['_source']['fi']])

    total = response.hits.total

    context = {
        'akharin': value
    }

    remove_of(context, "akharin", 2)
    remove_last_digit(context, "akharin", [2])
    format_with_commas(context, "akharin", [2])

    etesal(context, 'sain_last_two_buys', 'last_two',
           ['name_kala', 'idkala', 'fi_diff', 'day_diff', 'fi', 'last_fi', 'time', 'last_time'])

    remove_last_digit(context, "last_two", [4, 5])
    format_with_commas(context, "last_two", [4, 5])

    return render(request, 'pages/control.html', context)


def billing(request):
    return render(request, 'pages/billing.html', {'segment': 'billing'})


def tables(request):
    return render(request, 'pages/tables.html', {'segment': 'tables'})


def vr(request):
    context = {}

    etesal(context, "sain_deeg_pors", "deeg",
           ["Jalali_date_year", "Jalali_date_month", "Jalali_date_day", "total_customer_price", "deeg_pors"], True)
    remove_last_digit(context, "deeg", [4])
    format_with_commas(context, "deeg", [4, 5])

    etesal(context, "last_prices_df", "price", ["name", "original_price", "total_price", "sood", "nesbat"])
    remove(context, "price", 2, [0, 0.0])
    remove_last_digit(context, "price", [1, 2, 3])
    format_with_commas(context, "price", [1, 2, 3])

    #convert_to_persian(context)
    return render(request, 'pages/virtual-reality.html', context)


def rtl(request):
    return render(request, 'pages/rtl.html', {'segment': 'rtl'})


def ltr(request):
    return render(request, 'pages/index_ltr.html', {'segment': 'ltr'})


def profile(request):
    return render(request, 'pages/profile.html', {'segment': 'profile'})


def mali(request):
    context = {}

    conver_csv_to_dict(context, "/var/www/django-soft-ui-dashboard-master/csv/haz_mav_mas.csv", "haz_mav_mas",
                       ['Jalali_date_year', 'Jalali_date_month',
                        'anbarname', 'kalaname', 'ted',
                        'unit', 'fi', 'bed'])

    range_of(context, "haz_mav_mas", 1000, 10000000, 6)
    remove_last_digit(context, "haz_mav_mas", [6, 7])
    format_with_commas(context, "haz_mav_mas", [6, 7])

    conver_csv_to_dict(context, "/var/www/django-soft-ui-dashboard-master/csv/dar_har_mah.csv", "dar_har_mah",
                       ['Jalali_date_year', 'Jalali_date_month', 'srfslname', 'moinname', 'bes'])

    remove_last_digit(context, "dar_har_mah", [4])
    format_with_commas(context, "dar_har_mah", [4])

    conver_csv_to_dict(context, "/var/www/django-soft-ui-dashboard-master/csv/haz_har_mah.csv", "haz_har_mah",
                       ['Jalali_date_year', 'Jalali_date_month', 'srfslname', 'moinname', 'bed'])
    remove_last_digit(context, "haz_har_mah", [4])
    format_with_commas(context, "haz_har_mah", [4])

    etesal(context, 'motalebebeforoosh', 'motalebe', ['Year', 'Month', 'motalebe'])  # مطالبه
    groupby_and_aggregate(context, 'motalebe', 1, 2, 'max', [1400, 1401, 1402])

    etesal(context, 'senimotalebe', 'seni', ['Jalali_date_year', 'motalebe_diff'])  # مطالبه سنی
    groupby_and_aggregate(context, 'seni', 0, 1, 'sum', [])

  
    etesal(context, 'darbehaz', 'dar_be_haz', ['year', 'month', 'nesbat'])  # نسبت درآمد به هزینه
    groupby_and_aggregate(context, 'dar_be_haz', 1, 2, 'avg', [1400, 1401, 1402])

    etesal(context, 'sain_mande_pardakhtany*', 'mande_par',
           ['Jalali_date_year', 'Jalali_date_month', 'srfslname', 'moin', 'mande'])
    range_of(context, "mande_par", 10000000, 10000000000, 4)
    remove_last_digit(context, "mande_par", [4])
    format_with_commas(context, "mande_par", [4])

    etesal(context, 'sain_mande_daryaftani*', 'mande_dar', ['srfslname', 'name', 'mande', 'hsb'], True)
    range_of(context, "mande_dar", 10000000, 10000000000, 3, True)
    remove_last_digit(context, "mande_dar", [3])
    format_with_commas(context, "mande_dar", [3])

    return render(request, 'pages/mali.html', context)


def manabe_ensani(request):

    return render(request, 'pages/manabe_ensani.html', {'segment': 'manabe_ensani'})


def barname_rizi_billing(request):
    context = {}

    etesal(context, "sain_remain_after_6_month_alarm", "remain",
           ['kalaname', "anbarname", "ted", "unit", "remained_worth"])  # کالاهای راکد در ماه جاری
    etesal(context, "mojoodi_kala", "mojoodi",
           ['year', "month", "kalaname", "fi_kol", "ted", "unit"])  # موجودی انبار در ماه جاری
    range_of(context, "remain", 1000000, 1000000000, 4)
    range_of(context, "mojoodi", 1000000, 1000000000, 3)
    remove(context, "mojoodi", 4, [0])
    remove_last_digit(context, "remain", [4])
    remove_last_digit(context, "mojoodi", [3])
    format_with_commas(context, "remain", [2, 4])
    format_with_commas(context, "mojoodi", [3])

    return render(request, 'pages/barname_rizi_billing.html', context)


def control_billing(request):
    context = {}

    etesal(context, "khoroojna", "khorooj", ['year', "month", "day", "kalaname", "bes"], True)  # خروج نامتعارف
    remove_last_digit(context, "khorooj", [5])
    format_with_commas(context, "khorooj", [5])

    return render(request, 'pages/control_billing.html', context)


def c_analysis(request):
  
    return render(request, 'pages/c_analysis.html', {'segment': 'c_analysis'})


def s_t_analysis(request):
    return render(request, 'pages/s_t_analysis.html', {'segment': 's_t_analysis'})


def p_analysis(request):

    context = {}

    etesal(context, "last_prices_df", "price", ["name", "original_price", "total_price", "sood", "nesbat"])
    etesal(context,'mlp_sales', 'mlp_sales', ['food_name', 'sales_increase', 'price_change'])
    etesal(context,'mlp_sales', 'percent_name', ['food_name','increase', 'sales_increase', 'price_change'])
    round(context, 'mlp_sales', 1)
    remove_duplicates(context , 'mlp_sales')
    remove_duplicates(context , 'percent_name')
    remove_negatives(context , 'mlp_sales',1)
   
    remove(context, "price", 2, [0, 0.0])
    remove_last_digit(context, "price", [1, 2, 3])

    format_with_commas(context, "price", [1, 2, 3])

                                #دریافت محصول و درصد افزایش قیمت
    perc=context['percent_name']
    if request.method=='POST':

        form=YourForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            increase = form.cleaned_data['increase']

            predict = []
            for i in perc:
                print(i[1])
                if  name==i[0] :
                    if str(increase)=="":
                        predict.append([i[0],i[1],int(i[2]),i[3]])
                    elif float(increase) == float(f'{i[1]:1f}'):
                        predict.append([i[0],i[1],int(i[2]),i[3]])

            dict = {
                "predict": predict
            } 

        
        return JsonResponse({'data': {'data': dict}})
    return render(request, 'pages/p_analysis.html', context)


day = 0


def barnamerizi(request):
    context = {}

    etesal(context, "sain_depletion_alarm", "depletion",
           ["anbarname", "idkala", "kalaname", "ted", "unit", "needed_money"], True)  # جدول کالاهای در آستانه اتمام
    remove(context, "depletion", 1, ["محصولات", 'انبار محصول 2', 'شهيد قندي', 'محصولات آزاد (رستوران)', 'شهيد قندي '],
           True)
    range_of(context, "depletion", 1000000, 1000000000, 6, True)
    remove_last_digit(context, "depletion", [6])
    format_with_commas(context, "depletion", [4, 6])

    return render(request, "pages/barname_rizi.html", context)

def mlp_view(request):
    context = {}
    etesal(context,'mlp_sales', 'mlp_sales', ['food_name', 'sales_increase', 'price_change'])
    return render(request, 'pages/p_analysis.html', context)


# -----------------en---------------------
def index_en(request):
    return render(request, 'pages/en/index_en.html')


def control_en(request):
    context = {}
    s = Search(using=es1, index='akharin_gheymat_kharid')
    s = s.params(size=1000)
    response = s.execute()

    # Add query
    # s = s.query("match", title="python")

    # Execute search

    # Get hits as standard Python dicts
    hits = response.to_dict()['hits']['hits']

    # Iterate through results
    value = []
    for hit in hits:
        value.append([hit['_id'], hit['_source']['kalaname'], hit['_source']['fi']])

    total = response.hits.total

    context = {
        'akharin': value
    }
    etesal(context, 'tavaromkala', 'bishtarin', ['kalaname', 'tavarom_kala'])
    etesal(context, 'sain_last_two_buys', 'last_two',
           ['name_kala', 'idkala', 'fi_diff', 'day_diff', 'fi', 'last_fi', 'time', 'last_time'])
    return render(request, 'pages/en/control_en.html', context)


def barnamerizi_en(request):
    context = {}

    etesal(context, "sain_depletion_alarm", "depletion",
           ["anbarname", "idkala", "kalaname", "ted", "unit", "needed_money"], True)  # جدول کالاهای در آستانه اتمام

    return render(request, 'pages/en/barnamerizi_en.html', context)


def control_billing_en(request):
    return render(request, 'pages/en/control_billing_en.html')


def barnamerizi_billing_en(request):
    return render(request, 'pages/en/barnamerizi_billing_en.html')


def production_en(request):
    return render(request, 'pages/en/production_en.html')


def st_analysis_en(request):
    return render(request, 'pages/en/s_t_analysis_en.html')


def p_analysis_en(request):
    return render(request, 'pages/en/p_analysis_en.html')


def c_analysis_en(request):
    return render(request, 'pages/en/c_analysis_en.html')


def hr_en(request):
    return render(request, 'pages/en/hr_en.html')


def financial_en(request):
    return render(request, 'pages/en/financial_en.html')




# ------------------test-------------
def test(request):
    context = {}

    etesal(context, "sain_depletion_alarm", "depletion",
           ["anbarname", "idkala", "kalaname", "ted", "unit", "needed_money"], True)  # جدول کالاهای در آستانه اتمام
    etesal(context, "sain_remain_after_6_month_alarm", "remain",
           ['anbarname', "kalaname", "idkala", "ted", "unit", "remained_worth"])

    return render(request,
                  '/var/www/django-soft-ui-dashboard-master/env/lib/python3.9/site-packages/admin_soft/templates/admin/index.html',
                  context)



def process_form(request):
    if request.method == 'POST':
        input_data = request.POST.get('input_data')
        # انجام عملیات مورد نظر با داده‌های دریافتی از فرم
        return HttpResponse(f'The input data is: {input_data}')
    else:
        # اگر درخواست POST نباشد، ممکن است انتقال به این ویو به وسیله دسترسی غیرمجاز صورت گرفته باشد
        return HttpResponse('Invalid request method')


test = {
    "name": [
        ["amir", "amiri", 21, "09162127738"],
        ["sara", "karami", 20, "09162783328"],
        ["armin", "jahani", 38, "09219876538"],
    ]
}

def newone(request):
    context = {}
    if request.method == 'POST':
        form = newonef(request.POST)
        if form.is_valid( ):
            name = form.cleaned_data['name']
            context['name']=name

    return render(request,'pages/newone.html',context)



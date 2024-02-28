from django.urls import path

from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('barnamerizi/', views.barnamerizi, name='barnamerizi'),
    path('control/', views.control, name='control'),
    path('billing/', views.billing, name='billing'),
    path('tables/', views.tables, name='tables'),
    path('vr/', views.vr, name='vr'),
    path('rtl/', views.rtl, name='rtl'),

    path('profile/', views.profile, name='profile'),
    path('mali/', views.mali, name='mali'),
    path('manabe_ensani/', views.manabe_ensani, name='manabe_ensani'),
    path('c_analysis/', views.c_analysis, name='c_analysis'),
    path('s_t_analysis/', views.s_t_analysis, name='s_t_analysis'),
    path('p_analysis/', views.p_analysis, name='p_analysis'),
    path('predict/', views.search_predict, name='predict'),
    path('barname_rizi_billing/', views.barname_rizi_billing, name='barname_rizi_billing'),
    path('control_billing/', views.control_billing, name='control_billing'),
    path('p_analysis/', views.mlp_view, name='mlp_view'),

    # ----------------------------------ltr-----------------------------------



    path('en/', views.index_en, name='en'),
    path('control_en',views.control_en,name='control_en'),
    path('planning/',views.barnamerizi_en,name='planning'),
    path('control_bil_en/',views.control_billing_en,name='control_bil_en'),
    path('planning_bil_en/',views.barnamerizi_billing_en,name='planning_bil_en'),
    path('production_en/',views.production_en,name='production_en'),
    path('st_analysis_en/',views.st_analysis_en,name='st_analysis_en'),
    path('p_analysis_en/',views.p_analysis_en,name='p_analysis_en'),
    path('c_analysis_en/',views.c_analysis_en,name='c_analysis_en'),
    path('hr_en/',views.hr_en,name='hr_en'),
    path('financial_en/',views.financial_en,name='financial_en'),


    path('newone/',views.newone,name='newone'),]




    
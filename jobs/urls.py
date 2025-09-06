from django.urls import path
from . import views


app_name = 'jobs'


urlpatterns = [
path('', views.dashboard, name='dashboard'),
path('scrape/', views.run_scrape, name='scrape'),
path('progress/<str:operation_id>/', views.get_scrape_progress, name='progress'),
path('clear/', views.clear_jobs, name='clear'),
path('latest-jobs/', views.get_latest_jobs, name='latest_jobs'),
path('download-csv/', views.download_csv, name='download_csv'),
]
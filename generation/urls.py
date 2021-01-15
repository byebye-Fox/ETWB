
from django.urls import path

from . import views


urlpatterns = [

    path('generation/generate', views.generate,name= "generate"),
    path('generation/generatedata/',views.generateData),
    path('generation/filedownload/',views.downfile,name='filedownload'),
    path('generation/stationsdownload',views.stationdownload,name='stationdownload'),
    
    path('oristations/',views.oristations,name="oristations"),
    path('oristations/generatedata_ori/',views.generatedata_ori),
    path('oristaions/filedownload/',views.ori_downfile,name='ori_filedownload'),
    path('oristations/stationsdownload',views.ori_stationdownload,name='ori_stationdownload'),
    
    path('datafile/',views.datafile,name="datafile"),
    path('uploadFile/',views.import_csv,name="uploadFile"),
    path('uploadFile/generatedata_file/',views.generatedata_file),
    path('uploadFile/filedownload/',views.file_downfile,name="file_filedownload"),

]
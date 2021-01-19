from django.shortcuts import render

from django.http import JsonResponse,HttpResponseRedirect,FileResponse

from to_visual.generate_data import generation
import pandas as pd
import json
import os
from django.views.decorators.csrf import csrf_exempt
import math

pi = 3.14159265358979324
a = 6378245.0
ee = 0.00669342162296594323

def outOfChina(lat, lon):
    if (lon < 72.004 or lon > 137.8347):
        return True
    if (lat < 0.8293 or lat > 55.8271):
        return True
    return False

def outOfshenzhen(lat,lon):
    if (lon < 113 or lon > 115):
        return True
    if (lat < 22.2 or lat > 22.7):
        return True
    return False

def transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(math.fabs(x))
    ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * pi) + 40.0 * math.sin(y / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * pi) + 320 * math.sin(y * pi / 30.0)) * 2.0 / 3.0
    return ret

def transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(math.fabs(x))
    ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * pi) + 40.0 * math.sin(x / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * pi) + 300.0 * math.sin(x / 30.0 * pi)) * 2.0 / 3.0
    return ret

def transform(wgLat, wgLon):
    latlng = [0, 1]

    if outOfChina(wgLat, wgLon):
        latlng[0] = wgLat
        latlng[1] = wgLon
        return latlng

    dLat = transformLat(wgLon - 105.0, wgLat - 35.0)
    dLon = transformLon(wgLon - 105.0, wgLat - 35.0)
    radLat = wgLat / 180.0 * pi
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * pi)
    latlng[0] = wgLat + dLat
    latlng[1] = wgLon + dLon
    return latlng

# Create your views here.

def to_json1(df,orient='split'):
    df_json = df.to_json(orient=orient , force_ascii=False)
    return json.loads(df_json)


def generate(request):
    return render(request , 'generation/generate.html')

def generateData(request):
    ajax = request.GET
    stations = ajax["stations"]
    vechileNumb = ajax["vechileNmub"]
    vechileNumb = int(vechileNumb)
    temp1 = stations.replace('[','')
    temp2 = temp1.replace(']','')
    temp3 = temp2.split(',')
    thedata = []

    for i in range(0,len(temp3),4):
        tempattr = []
        No = int((i/4)+1)
        name = "A"+str(temp3[i])
        lng = float(temp3[i+1])
        lat = float(temp3[i+2])
        noname = 1
        vechnum = int(temp3[i+3])
        tempattr = [No,name,lng,lat,noname,vechnum]
        thedata.append(tempattr)

    df_cs2 = pd.DataFrame(thedata,columns=['ID','cs_name','Longitude','Latitude','Online','chg_points'])
    df_cs2 = df_cs2.drop("Online",axis = 1)
    df_cs2.to_csv('generated_data/stations.csv', index=False)

    generated_data = generation(amount=vechileNumb, df_cs=df_cs2)
    generated_data.to_csv('generated_data/generated_data.csv', index=False)
    json_res = to_json1(generated_data)
    return JsonResponse(json_res , safe = False)

def downfile(request):
    file = open("generated_data/generated_data.csv",'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="generated_data.csv"'
    return response

def stationdownload(request):
    file = open("generated_data/stations.csv",'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="stations.csv"'
    return response

def oristations(request):
    return render(request,'generation/oristations.html')


def generatedata_ori(request):
    ajax = request.GET
    # vechileNumb = ajax["vechileNmub"]
    # vechileNumb = int(vechileNumb)

    # datas=[[1,'A01',114.007401,22.535500,1,12],[2,'FN0002',114.009001,22.534233,1,6],[3,'N04',113.987547,22.560519,1,40],[4,'D08',114.088303,22.562599,1,20],[5,'LJDL',114.361504,22.678499,2,16],[6,'D10',114.074406,22.559000,1,16],[7,'B04',113.922977,22.546375,1,20],[8,'D01',114.123241,22.562538,1,12],[9,'C01',114.101748,22.582541,1,52],[10,'E11',114.068837,22.573326,1,20],[11,'A02',114.023404,22.542650,1,16],[12,'E01',114.023902,22.619512,1,16],[13,'F02',113.817750,22.650682,1,8],[14,'A08',113.944128,22.506854,1,14],[15,'A09',113.941642,22.527053,1,16],[16,'A10',113.962844,22.528519,1,14],[17,'BN0002',113.814932,22.651322,2,12],[18,'D06',114.304419,22.600844,1,16],[19,'N02',114.032902,22.524276,1,16],[20,'F07',113.858390,22.579457,1,8],[21,'A03',113.995054,22.547247,1,16],[22,'E04',114.003978,22.636233,2,10],[23,'D09',114.045125,22.551410,1,10],[24,'F08',113.838486,22.609576,1,16],[25,'F10',114.043404,22.601,1,12],[26,'F11',113.985199,22.547701,2,12],[27,'F12',113.8134,22.624201,1,100],[28,'F13',114.135002,22.544001,1,100],[29,'PSBYD',114.353401,22.679399,1,12],[30,'S1',113.8564,22.616899,1,100],[31,'F15',114.031502,22.5252,1,100],[32,'S2',114.1798,22.5585,1,100]]

    # df_cs2 = pd.DataFrame(datas,columns=['ID','cs_name','Longitude','Latitude','Online','chg_points'])
    # generated_data = generation(amount=vechileNumb, df_cs=df_cs2)
    # generated_data.to_csv('generated_data/ori_generated_data.csv', index=False)
    # 上部分代码在测试生成等待时间的过程中被注释，完成后记得解释

    generate_data = pd.read_parquet('generated_data/generated_trajectories.parquet')
    generate_data.reset_index(inplace = True)
    shape = generate_data.shape
    if(shape[0] > 1000):
        send_data = generate_data.iloc[0:100000]

    print(send_data)

    hours = []
    dates_charging_times = []
    charging_times = {}
    queuing_time = {}
    traveled_before_charging = []
    day_traveled = []
    print(shape[0])

    def date_filling(oneCar_oneDay):
        row = oneCar_oneDay.shape[0]
        charging_events = oneCar_oneDay.loc[oneCar_oneDay['event'] == 'charging']
        traveled_total = charging_events['traveled'].sum() + oneCar_oneDay.iloc[0,:]['traveled'] + oneCar_oneDay.iloc[-1,:]['traveled']
        day_traveled.append(traveled_total)

    def day_filling(one_day):
        hours.append(one_day.iloc[0]['time_of_day'])
        charging_events = one_day.loc[one_day['event'] == 'charging']
        date_charging_times = charging_events.shape[0]
        dates_charging_times.append(date_charging_times)   
         # 每个小时的充电事件发生次数

    def filling(onetip):
        if(onetip['event'] == 'charging'):
            traveled_before_charging.append(onetip['traveled'])
            the_id = 'A' + str(onetip['station'])
            if(the_id in charging_times.keys()):
                charging_times[the_id] = charging_times[the_id] + 1
                queuing_time[the_id] = queuing_time[the_id] + onetip['queuing']
            else:
                charging_times[the_id] = 1
                queuing_time[the_id] = onetip['queuing']

    send_data['time_of_day'] = send_data['timestamp'].apply(lambda x:x.strftime('%H'))
    send_data['date'] = send_data['timestamp'].apply(lambda x:x.strftime('%Y-%m-%d'))
    send_data.groupby('time_of_day').apply(day_filling)
    send_data.groupby('date').apply(lambda x: x.groupby('id').apply(date_filling))
    charging_events = send_data.loc[generate_data['event'] == 'charging']
    charging_events.apply(filling , axis=1)

    def get_dis(data , dis_counts):
        max_data = max(data)
        min_data = min(data)
        dis = {}
        dis_distance = (max_data - min_data) / dis_counts
        for i in range(0,(dis_counts + 1)):
            dis[i] = 0
        for i in data:
            label = int((i - min_data)//dis_distance)
            dis[label] = dis[label] + 1
        return {'dis':dis,'dis_distance':dis_distance,'min_data':min_data}

    print(hours)
    print(dates_charging_times)
    print(charging_times)
    print(queuing_time)
    print(get_dis(traveled_before_charging , 50) )
    print(get_dis(day_traveled , 50))

    for key in queuing_time:
        queuing_time[key] = queuing_time[key] / charging_times[key]

    json_res = to_json1(send_data)
    json_res['hours'] = hours
    json_res['dates_charging_times'] = dates_charging_times
    json_res['charging_times'] = charging_times
    json_res['queue_time'] = queuing_time
    json_res['traveled_before_charging'] = get_dis(traveled_before_charging , 50)
    json_res['day_traveled'] = get_dis(day_traveled , 50)
    return JsonResponse(json_res , safe = False)

def ori_downfile(request):
    file = open("generated_data/ori_generated_data.csv",'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="ori_generated_data.csv"'
    return response

def ori_stationdownload(request):
    file = open("generated_data/ori_stations_1.csv",'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="ori_stations_1.csv"'
    return response

def datafile(request):
    return render(request,'uploadFile/datafileupload.html')

def generatedata_file(request):
    ajax = request.GET
    vechileNumb = ajax["vechileNmub"]
    vechileNumb = int(vechileNumb)

    df_cs = pd.read_csv('static/dataUpload/uploadstations.csv',engine='python')
    df_cs.insert(4,'Online',1)
    generated_data = generation(amount=vechileNumb, df_cs=df_cs)
    generated_data.to_csv('generated_data/file_generated_data.csv', index=False)
   
    json_res = to_json1(generated_data)
    return JsonResponse(json_res , safe = False)

def import_csv(request):
    ajax = request.POST
    if request.method == "POST":
        thisFile = request.FILES.get("myfile",None)
        filecheck = fileOp(thisFile)
        if filecheck["CheckRes"]:
            return render(request,'uploadFile/datafileWrong.html',filecheck)
        else:
            destination = open("static/dataUpload/uploadstations.csv", 'wb+')
            for chunk in thisFile.chunks():
                destination.write(chunk)
            destination.close()
            return render(request, 'generation/datafile.html')

def file_downfile(request):
    file = open("generated_data/file_generated_data.csv",'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="file_generated_data.csv"'
    return response

# 错误文件的输入类型检查
def fileOp(upfile):
    iswrong = False
    warringlist = []

    try:
        thefile = pd.read_csv(upfile)
    except Exception as e:
        fileopenCheck = "The file could not be opened because : " + str(e)
        warringlist.append(fileopenCheck)
        iswrong = True
    else:
        correctColumns = ['ID', 'cs_name', 'Longitude', 'Latitude', 'chg_points']

        res = []
        idlist = []

        theshape = thefile.shape[1]
        if theshape != 5:
            shapecheck = 'The number of the list is incorrect, expect 5 but saw ' + str(theshape)
            iswrong = True
            warringlist.append(shapecheck)
        else:
            columns = list(thefile)
            columnNameWrong = []
            for i in range(0, 5):
                if correctColumns[i] != columns[i]:
                    columnNameWrong.append(i+1)

            if len(columnNameWrong) >= 1:
                columnNamecheck = 'Columns : ' + str(columnNameWrong) + 'name is incorrect.'
                iswrong = True
                warringlist.append(columnNamecheck)

            repeatIds = []
            notInShenzhen = []
            NotInlaw = []
            outofRange = []

            rownum = thefile.shape[0]
            for i in range(0, rownum):
                print("in check")
                newlng = 0.0
                newlat = 0.0
                numofvp = 0
                oneRow = thefile.iloc[i, :]

                if oneRow[0] in idlist:
                    iswrong = True
                    repeatIds.append(i)
                else:
                    idlist.append(oneRow[0])

                try:
                    templng = float(oneRow[2])
                    templat = float(oneRow[3])
                except:
                    NotInlaw.append("Row." + str(i+1) + ": lng or lat")
                else:
                    if outOfshenzhen(templat, templng):
                        notInShenzhen.append(i)
                        iswrong = True
                    else:
                        newlat, newlng = transform(templat, templng)

                try:
                    numofvp = int(oneRow[4])
                except:
                    NotInlaw.append("Row." + str(i+1) + ": number of charging piles")
                    iswrong = True
                else:
                    if numofvp <= 0 or numofvp >= 300:
                        outofRange.append("Row." + str(i+1) + ": number of vehicles is out of range")
                        iswrong = True

                if not iswrong:
                    tempres = [oneRow[0], oneRow[1], newlng, newlat, numofvp]
                    res.append(tempres)

            if iswrong:
                if len(repeatIds)>0:
                    idcheck = "Rows : " + str(repeatIds) + "'s id should be unique.?"
                    warringlist.append(idcheck)
                if len(notInShenzhen) > 0:
                    shenzhencheck = "Rows : " + str(notInShenzhen) + "'s coordinate is not in ShenZhen.?"
                    warringlist.append(shenzhencheck)
                if len(NotInlaw)>0:
                    inlawcheck = "The elements :" + str(NotInlaw) + " not in law.?"
                    warringlist.append(inlawcheck)
                if len(outofRange)>0:
                    rangeCheck = "The number of charging piles : " + str(outofRange) + " is out of range(1~300).?"
                    warringlist.append(rangeCheck)
    return {
        "CheckRes":iswrong,
        "detail":warringlist
    }

# 检测列名，如果列名缺少，则添加列名，否则正常读取
# id需要唯一
# Longtitude 和 Latitude 为合理的对子
# 包括：限制位置在深圳范围之内，限制输入为number类型
# 对GPS地图坐标提供向高德地图坐标的转换功能
# chargpoints限制其输入为number类型，同时输入的范围为1~300之间




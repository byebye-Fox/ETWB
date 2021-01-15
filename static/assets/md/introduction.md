[TOC]

# The name

**it provides:**

- generate the travel data of electric taxi cars. 

**this can be used:**

- provide predicted travel data that 

## how to use

### data generation

This section provides methods to use (model name) to generate travel data.  The following three methods are different from the way you specify the distribution of sites and the number of vehicles used for data generation.

![](../static/assets/img/flow.png)

```flow
st=>start: begin
cond1=>condition: station_distrubution
ori=>operation: use ori stations
inputvehicles=>inputoutput: input the number of the vehicles
datafile=>operation: datafile
uploadthedatafile=>inputoutput: upload the distribution file
filecheck=>condition: check file structures
selfcharging=>operation: self charging stations
clickthestations=>operation: edit the station distribution
cond2=>condition: use_ori
getresult=>operation: get the result

st->cond1
cond1(yes)->datafile->uploadthedatafile->filecheck
filecheck(yes)->inputvehicles
filecheck(no)->datafile
cond1(no)->cond2
cond2(yes)->ori->inputvehicles
cond2(no)->selfcharging->clickthestations->inputvehicles
inputvehicles->getresult
```


#### use original stations

The real charging station distribution data of Shenzhen city is used to generate the data.  The distribution is shown at the bottom of the interface. You just need to fill in the corresponding number of vehicles, click the “*Generate data*” button, and you can wait for the results. 


#### self charge stations

You can choose the distribution of the corresponding charging stations in this method. Click the "*charge stations*" button to enter the edit mode, you can add stations by click on the map, and delete the stations you don't need in "*station list*". Input the number of the vehicles, click the “*Generate data*” button to get the result.

#### upload data file

If you have a clear target for the distribution of your charging stations, you can use this feature. You can upload the station distribution file that conforms to the rules. We will check the file provided by you, and generate the corresponding distribution map. Confirm that you have correctly input the number of the vehicles, click the “*Generate data*” button to get the result.

## contribution



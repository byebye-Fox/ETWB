<code>

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

</code>


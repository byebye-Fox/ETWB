$('#card2').hide()
$("#ori_card2").hide()
$("#ori_progressing").hide()
$("#file_card2").hide()
$("#file_progressing").hide()


var map2 = new AMap.Map("container2", {
    zoom: 12,
    center: [114.029652662306, 22.5529062486263],
    viewMode: "2D",
    lang: "en", //地图语言
    mapStyle: 'amap://styles/whitesmoke',
})

var stationList = []
var markerlist = []

listmarkerid = 0

var the_e

$("#generateData").click(function() {
    $('#card1').hide()
    $("#progressing").show()

    vechileNmub = $("#numofvechicles").val()
    if (vechileNmub >= 0 && vechileNmub <= 200 && vechileNmub != '' && stationList.length >= 1) {
        $("#multi-filter-select").dataTable().fnDestroy()
            // 销毁原有表格，生成新的表格

        res = ''
        $.ajax({
            url: "generatedata/",
            type: "GET",
            dataType: "json",
            data: {
                "stations": JSON.stringify(stationList),
                "vechileNmub": vechileNmub

            },
            success: function(resdata) {

                $('#card2').show()
                $("#progressing").hide()

                thedata = resdata["data"]
                var stationdic = {}
                if (thedata.length > 1000) {
                    info = "<p class='bg-warning ml-1'>there are too much records,this table will only show 1000 records,please download to get the complete data</p>"
                    $("#infoshow").append(info)
                }
                for (let i = 0; i < thedata.length; i++) {
                    oneTip = thedata[i]
                    ifin = false
                    for (var key in stationdic) {
                        if (key == oneTip[9]) {
                            ifin = true
                            break
                        }
                    }
                    if (ifin) {
                        stationdic[oneTip[9]] = stationdic[oneTip[9]] + 1
                    } else {
                        stationdic[oneTip[9]] = 1
                    }

                    kkeys = []
                    vvalues = []
                    for (var key in stationdic) {
                        if (key != 'null') {
                            kkeys.push(key)
                            vvalues.push(stationdic[key])
                        }
                    }

                    if (i < 1000) {
                        var time1 = new Date();
                        time1.setTime(oneTip[1]).toLocaleString()
                        var time2 = new Date();
                        time2.setTime(oneTip[2]).toLocaleString()
                        var test = "<tr class='odd'role='row' ><td>" + oneTip[0] + "</td><td>" + time1 + "</td> <td>" + time2 + "</td>" + "<td>" + oneTip[3] + "</td>" + "<td>" + oneTip[4] + "</td>" + "<td>" + oneTip[5] + "</td>" + "<td>" + oneTip[6] + "</td>" + "<td>" + oneTip[7] + "</td>" + "<td>" + oneTip[8] + "</td>" + "<td>" + oneTip[9] + "</td>" + "</tr>"
                        res = res + test
                    }

                }

                var barChart = echarts.init(document.getElementById('barChart2'));
                var colors = ['#5793f3', '#d14a61', '#675bba'];

                option = {
                    color: colors,

                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    legend: {
                        data: ['charge time']
                    },
                    xAxis: [{
                        type: 'category',
                        name: 'charge Station',
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: kkeys
                    }],
                    yAxis: [{
                            type: 'value',
                            name: 'charge times',
                            min: 0,
                            position: 'left',
                            axisLine: {
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} times'
                            }
                        }

                    ],
                    series: [{
                        name: '当前充电站',
                        type: 'bar',
                        data: vvalues
                    }, ]
                };

                barChart.setOption(option);
                console.log(stationdic)
                $('#thetbody').append(res)

                $('#multi-filter-select').DataTable({
                    "pageLength": 10,
                    initComplete: function() {
                        this.api().columns().every(function() {
                            var column = this;
                            var select = $('<select class="form-control"><option value=""></option></select>')
                                .appendTo($(column.footer()).empty())
                                .on('change', function() {
                                    var val = $.fn.dataTable.util.escapeRegex(
                                        $(this).val()
                                    );

                                    column
                                        .search(val ? '^' + val + '$' : '', true, false)
                                        .draw();
                                });

                            column.data().unique().sort().each(function(d, j) {
                                select.append('<option value="' + d + '">' + d + '</option>')
                            });
                        });
                    }
                });
            },
            error: function(msg) {
                swal(msg, {
                    icon: "error",
                    buttons: {
                        confirm: {
                            className: 'btn btn-error'
                        }
                    }
                });
            }

        })



    } else if (stationList.length == 0) {
        swal("Make sure there are at least one station you've picked", {
            icon: "warning",
            buttons: {
                confirm: {
                    className: 'btn btn-warning'
                }
            }
        });
    } else {
        swal("Please input the correct number of the vechciles(1~200)", {
            icon: "warning",
            buttons: {
                confirm: {
                    className: 'btn btn-warning'
                }
            }
        });
    }
})

function input_num_of_veh(e) {
    the_e = e
    swal({
        title: 'Input Something',
        html: '<br><input class="form-control" placeholder="Input Something" id="input-field">',
        content: {
            element: "input",
            attributes: {
                placeholder: "Input Something",
                type: "text",
                id: "input-field",
                className: "form-control"
            },
        },
        buttons: {
            confirm: {
                text: "submit",
                className: 'btn btn-success'
            },
            cancel: {
                visible: true,
                text: 'cancel',
                className: 'btn btn-danger'
            },
        },
    }).then((yes) => {
        if (yes) {
            var numofchargingpiles = $("#input-field").val()
            if (numofchargingpiles >= 0 && numofchargingpiles <= 200 && numofchargingpiles != '') {
                lng = e.lnglat.getLng()
                lat = e.lnglat.getLat()
                listmarkerid = listmarkerid + 1

                lnglatpair = [listmarkerid, lng, lat, parseInt(numofchargingpiles)]
                stationList.push(lnglatpair)
                thetitle = "marker" + listmarkerid
                marker = new AMap.Marker({
                    title: thetitle,
                    icon: "//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png",
                    position: e.lnglat,
                    offset: new AMap.Pixel(-10, -30)
                });
                marker.setLabel({
                    offset: new AMap.Pixel(10, 10), //设置文本标注偏移量
                    content: "<div class='info'>" + "A" + lnglatpair[0] + ":(" + lnglatpair[1] + "," + lnglatpair[2] + ") " + numofchargingpiles + "</div>", //设置文本标注内容
                    direction: 'top' //设置文本标注方位
                })
                map2.add(marker)
                stationNew = "<li id ='limarker?" + listmarkerid + "'><button class='btn btn-default btn-border col-10'>" + "A" + lnglatpair[0] + ":(" + lnglatpair[1] + "," + lnglatpair[2] + ") " + numofchargingpiles + "</button><button type='button' class='btn btn-icon btn-round btn-danger deleteMarker' id='marker?" + listmarkerid + "'><i class='fas fa-times'></button></li>"
                markerlist.push(marker)
                $("#stationList").append(stationNew)
                swal("One station set successfully.", {
                    icon: "success",
                    buttons: {
                        confirm: {
                            className: 'btn btn-success'
                        }
                    }
                });



            } else {
                swal("please input the number of the charging piles correctly (1~200)", {
                    icon: "warning",
                    buttons: {
                        confirm: {
                            className: 'btn btn-warning'
                        }
                    }
                });
            }
        }
    })
}


$("#stationCharge").click(function() {
    swal("Start edit", {
        buttons: false,
        timer: 3000,
    });
    $("#stationCharge").prop('disabled', true)
    $("#editmodeloff").prop('disabled', false)
    map2.on("click", input_num_of_veh)
})

$("#editmodeloff").click(function() {
    swal("Edit mode off", {
        buttons: false,
        timer: 3000,
    });
    $("#stationCharge").prop('disabled', false)
    $("#editmodeloff").prop('disabled', true)
    map2.off("click", input_num_of_veh)

})

$("#stationList").on("click", "button.deleteMarker", function() {
    var markerID = $(this).attr('id');
    console.log(markerID)
    idnum = markerID.split("?")[1]

    for (var thepostition = 0; thepostition < stationList.length; thepostition++) {
        if (stationList[thepostition][0] == idnum) {
            markerlist[thepostition].setMap(null)
            console.log(stationList)

            markerlist.splice((thepostition), 1)
            stationList.splice((thepostition), 1)

            liID = "li" + markerID

            deteletLi = document.getElementById(liID)
            deteletLi.remove()
        }
    }
    console.log(stationList)

})

$("#oriGenerateData").click(function() {

    $("#ori_card1").hide()
    $("#ori_progressing").show()

    vechileNmub = $("#ori_numofvechicles").val()
    if (vechileNmub >= 0 && vechileNmub <= 200 && vechileNmub != '') {

        $("#ori-multi-filter-select").dataTable().fnDestroy()

        res = ''

        $.ajax({
            url: "generatedata_ori/",
            type: "GET",
            dataType: "json",
            data: {
                "vechileNmub": vechileNmub
            },
            success: function(resdata) {
                console.log(resdata)

                $("#ori_card2").show()
                $("#ori_progressing").hide()

                thedata = resdata["data"]
                charging_times = resdata['charging_times']
                queue_time = resdata['queue_time']

                stations = []
                for(var key in charging_times){
                    stations.push(key)
                }

                charging_by_license = []
                for(let i in stations){
                    charging_by_license.push(charging_times[stations[i]])
                }

                queuing_by_stations = []
                for(let i in stations){
                    queuing_by_stations.push(queue_time[stations[i]])
                }

                console.log(queue_time)
                var stationdic = {}

                if (thedata.length > 1000) {
                    info = "<p class='bg-warning ml-1'>there are too much records,this table will only show 1000 records,please download to get the complete data</p>"
                    $("#ori_infoshow").append(info)
                }
                for (let i = 0; i < thedata.length; i++) {
                    oneTip = thedata[i]
                    ifin = false
                    for (var key in stationdic) {
                        if (key == oneTip[9]) {
                            ifin = true
                            break
                        }
                    }
                    if (ifin) {
                        stationdic[oneTip[9]] = stationdic[oneTip[9]] + 1
                    } else {
                        stationdic[oneTip[9]] = 1
                    }

                    if (i < 1000) {
                        var time2 = new Date();
                        time2.setTime(oneTip[2]).toLocaleString()
                        var test = "<tr class='odd'role='row' ><td>" + oneTip[0] + "</td><td>" + oneTip[1] + "</td> <td>" + time2 + "</td>" + "<td>" + oneTip[3] + "</td>" + "<td>" + oneTip[4] + "</td>" + "<td>" + oneTip[5] + "</td>" + "<td>" + oneTip[6] + "</td>" + "<td>" + oneTip[7] + "</td>" +  "</tr>"
                        res = res + test
                    }

                }

                var barChart = echarts.init(document.getElementById('ori_barChart'));
                var barChart2 = echarts.init(document.getElementById('queuing_time_chart'));
                var colors = ['#5793f3', '#d14a61', '#675bba'];
                var colors2 = ['#578432' , '#d14561' , '#123456']

                option = {
                    color: colors,

                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    legend: {
                        data: ['charge time']
                    },
                    xAxis: [{
                        type: 'category',
                        name: 'charge Station',
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: stations
                    }],
                    yAxis: [{
                            type: 'value',
                            name: 'charge times',
                            min: 0,
                            position: 'left',
                            axisLine: {
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} times'
                            }
                        }

                    ],
                    series: [{
                        name: '当前充电站',
                        type: 'bar',
                        data: charging_by_license
                    }, ]
                };

                option2 = {
                    color: colors2,

                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    legend: {
                        data: ['charge time']
                    },
                    xAxis: [{
                        type: 'category',
                        name: 'charge Station',
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: stations
                    }],
                    yAxis: [{
                            type: 'value',
                            name: 'queuing times',
                            min: 0,
                            position: 'left',
                            axisLine: {
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} s'
                            }
                        }

                    ],
                    series: [{
                        name: '当前充电站',
                        type: 'bar',
                        data: queuing_by_stations
                    }, ]
                };

                barChart.setOption(option);
                barChart2.setOption(option2);

                
                $('#ori_thetbody').append(res)
                $('#ori-multi-filter-select').DataTable({
                    "pageLength": 10,
                    initComplete: function() {
                        this.api().columns().every(function() {
                            var column = this;
                            var select = $('<select class="form-control"><option value=""></option></select>')
                                .appendTo($(column.footer()).empty())
                                .on('change', function() {
                                    var val = $.fn.dataTable.util.escapeRegex(
                                        $(this).val()
                                    );

                                    column
                                        .search(val ? '^' + val + '$' : '', true, false)
                                        .draw();
                                });

                            column.data().unique().sort().each(function(d, j) {
                                select.append('<option value="' + d + '">' + d + '</option>')
                            });
                        });
                    }
                });

            },
            error: function(msg) {
                swal(msg, {
                    icon: "error",
                    buttons: {
                        confirm: {
                            className: 'btn btn-error'
                        }
                    }
                });
            }

        })

    } else {
        swal("please input the correct number of the vechciles(1~200)", {
            icon: "warning",
            buttons: {
                confirm: {
                    className: 'btn btn-warning'
                }
            }
        });
    }

})

$("#fileGenerateData").click(function() {
    $("#file_card1").hide()
    $("#file_progressing").show()

    vechileNmub = $("#file_numofvechicles").val()
    if (vechileNmub >= 0 && vechileNmub <= 200 && vechileNmub != '') {

        $("#file-multi-filter-select").dataTable().fnDestroy()

        res = ''

        $.ajax({
            url: "generatedata_file/",
            type: "GET",
            dataType: "json",
            data: {
                "vechileNmub": vechileNmub
            },
            success: function(resdata) {
                $("#file_card2").show()
                $("#file_progressing").hide()

                thedata = resdata["data"]
                var stationdic = {}

                if (thedata.length > 1000) {
                    info = "<p class='bg-warning ml-1'>there are too much records,this table will only show 1000 records,please download to get the complete data</p>"
                    $("#file_infoshow").append(info)
                }
                for (let i = 0; i < thedata.length; i++) {
                    oneTip = thedata[i]
                    ifin = false
                    for (var key in stationdic) {
                        if (key == oneTip[9]) {
                            ifin = true
                            break
                        }
                    }
                    if (ifin) {
                        stationdic[oneTip[9]] = stationdic[oneTip[9]] + 1
                    } else {
                        stationdic[oneTip[9]] = 1
                    }

                    kkeys = []
                    vvalues = []
                    for (var key in stationdic) {
                        if (key != 'null') {
                            kkeys.push(key)
                            vvalues.push(stationdic[key])
                        }
                    }

                    if (i < 1000) {
                        var time1 = new Date();
                        time1.setTime(oneTip[1]).toLocaleString()
                        var time2 = new Date();
                        time2.setTime(oneTip[2]).toLocaleString()
                        var test = "<tr class='odd'role='row' ><td>" + oneTip[0] + "</td><td>" + time1 + "</td> <td>" + time2 + "</td>" + "<td>" + oneTip[3] + "</td>" + "<td>" + oneTip[4] + "</td>" + "<td>" + oneTip[5] + "</td>" + "<td>" + oneTip[6] + "</td>" + "<td>" + oneTip[7] + "</td>" + "<td>" + oneTip[8] + "</td>" + "<td>" + oneTip[9] + "</td>" + "</tr>"
                        res = res + test
                    }

                }

                var barChart = echarts.init(document.getElementById('file_barChart'));
                var colors = ['#5793f3', '#d14a61', '#675bba'];

                option = {
                    color: colors,

                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross'
                        }
                    },
                    grid: {
                        right: '20%'
                    },
                    legend: {
                        data: ['charge time']
                    },
                    xAxis: [{
                        type: 'category',
                        name: 'charge Station',
                        axisTick: {
                            alignWithLabel: true
                        },
                        data: kkeys
                    }],
                    yAxis: [{
                            type: 'value',
                            name: 'charge times',
                            min: 0,
                            position: 'left',
                            axisLine: {
                                lineStyle: {
                                    color: colors[1]
                                }
                            },
                            axisLabel: {
                                formatter: '{value} times'
                            }
                        }

                    ],
                    series: [{
                        name: '当前充电站',
                        type: 'bar',
                        data: vvalues
                    }, ]
                };

                barChart.setOption(option);


                $('#file_thetbody').append(res)
                $('#file-multi-filter-select').DataTable({
                    "pageLength": 10,
                    initComplete: function() {
                        this.api().columns().every(function() {
                            var column = this;
                            var select = $('<select class="form-control"><option value=""></option></select>')
                                .appendTo($(column.footer()).empty())
                                .on('change', function() {
                                    var val = $.fn.dataTable.util.escapeRegex(
                                        $(this).val()
                                    );

                                    column
                                        .search(val ? '^' + val + '$' : '', true, false)
                                        .draw();
                                });

                            column.data().unique().sort().each(function(d, j) {
                                select.append('<option value="' + d + '">' + d + '</option>')
                            });
                        });
                    }
                });

            },
            error: function(msg) {
                swal(msg, {
                    icon: "error",
                    buttons: {
                        confirm: {
                            className: 'btn btn-error'
                        }
                    }
                });
            }

        })
    } else {
        swal("please input the correct number of the vechciles (1~200)", {
            icon: "warning",
            buttons: {
                confirm: {
                    className: 'btn btn-warning'
                }
            }
        });
    }
})

$('#multi-filter-select').DataTable({
    "pageLength": 10,
    initComplete: function() {
        this.api().columns().every(function() {
            var column = this;
            var select = $('<select class="form-control"><option value=""></option></select>')
                .appendTo($(column.footer()).empty())
                .on('change', function() {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );

                    column
                        .search(val ? '^' + val + '$' : '', true, false)
                        .draw();
                });

            column.data().unique().sort().each(function(d, j) {
                select.append('<option value="' + d + '">' + d + '</option>')
            });
        });
    }
});

$('#ori-multi-filter-select').DataTable({
    "pageLength": 10,
    initComplete: function() {
        this.api().columns().every(function() {
            var column = this;
            var select = $('<select class="form-control"><option value=""></option></select>')
                .appendTo($(column.footer()).empty())
                .on('change', function() {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );

                    column
                        .search(val ? '^' + val + '$' : '', true, false)
                        .draw();
                });

            column.data().unique().sort().each(function(d, j) {
                select.append('<option value="' + d + '">' + d + '</option>')
            });
        });
    }
});

$('#file-multi-filter-select').DataTable({
    "pageLength": 10,
    initComplete: function() {
        this.api().columns().every(function() {
            var column = this;
            var select = $('<select class="form-control"><option value=""></option></select>')
                .appendTo($(column.footer()).empty())
                .on('change', function() {
                    var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                    );

                    column
                        .search(val ? '^' + val + '$' : '', true, false)
                        .draw();
                });

            column.data().unique().sort().each(function(d, j) {
                select.append('<option value="' + d + '">' + d + '</option>')
            });
        });
    }
});

$('#true_upload').click(function() {
    $('#true_upload').val('');
});

$('#true_upload').on('change', function() {
    var fileNameStr = $('#true_upload').val();
    var index2 = fileNameStr.length;
    if (fileNameStr.indexOf("/") != -1) {
        var index1 = fileNameStr.lastIndexOf("/");
    } else {
        var index1 = fileNameStr.lastIndexOf("\\");
    }
    if (index1 <= -1) {
        index1 = 0;
    } else {
        index1 += 1;
    }
    fileNameStr = "You've pick : " + fileNameStr.substring(index1, index2);
    $('#uploadFileButton').val(fileNameStr);
});

$("#uploadFileButton").click(function() {
    $("#true_upload").click()
    $("#to_submit").prop('disabled', false)
})
$("#onboard").click(function(){
  $.notify({
    icon: 'flaticon-desk',
    title: 'Data processing',
    message: 'this could take a while ...',
  },{
    type: 'info',
    placement: {
        from: "bottom",
        align: "right"
    },
    time:50,
  });
  
  var map = new AMap.Map("container",{
    zoom:12,
    center:[114.029652662306,22.5529062486263],
    viewMode:"2D",
    lang:"en",//地图语言
    mapStyle: 'amap://styles/whitesmoke',
  })
  
  var layer = new Loca.ScatterPointLayer({
    map:map
  })
  
  var colors = ["rgba(241, 42, 42, 0.5)","rgb(16, 0, 245,0.5)"]

  $.get("../static/assets/data/load_points.csv",function(data){ 
    layer.setData(data,{
      lnglat:function(obj){
        var value = obj.value
        return [value["0"],value["1"]]
      },
      type:"csv"
    });
  
    layer.setOptions({
      unit:"px",
      style:{
        radius:function(obj){
          var value = obj.value;
          switch(parseInt(value["2"])){
            case -1:
              return 2;
            default:
              return 2;
          }
        },
        height:0,
        color:function(obj){
          value = obj.value;
          switch(parseInt(value["2"])){
            case -1:
              return colors[1];
            default:
              return colors[0];
  
          }
        },
        opacity:0.8
      }
  
    });
    layer.render(); 
  })
})

$("#getoff").click(function(){

  $.notify({
    icon: 'flaticon-desk',
    title: 'Data processing',
    message: 'this could take a while ...',
  },{
    type: 'info',
    placement: {
        from: "bottom",
        align: "right"
    },
    time:50,
  });

  var map = new AMap.Map("container",{
    zoom:12,
    center:[114.029652662306,22.5529062486263],
    viewMode:"2D",
    lang:"en",//地图语言
    mapStyle: 'amap://styles/whitesmoke',
  })
  
  var layer = new Loca.ScatterPointLayer({
    map:map
  })
  
  var colors = ["rgba(241, 42, 42, 0.5)","rgb(16, 0, 245,0.5)"]

  $.get("../static/assets/data/dropthe_points.csv",function(data){
    layer.setData(data,{
      lnglat:function(obj){
        var value = obj.value
        return [value["0"],value["1"]]
      },
      type:"csv"
    });
  
    layer.setOptions({
      unit:"px",
      style:{
        radius:function(obj){
          var value = obj.value;
          switch(parseInt(value["2"])){
            case -1:
              return 2;
            default:
              return 2;
          }
        },
        height:0,
        color:function(obj){
          value = obj.value;
          switch(parseInt(value["2"])){
            case -1:
              return colors[1];
            default:
              return colors[0];
  
          }
        },
        opacity:0.8
      }
  
    });
    layer.render(); 
  })
})

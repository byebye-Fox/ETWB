import pickle
import torch
import logging
import to_visual.utils.data_loader as data_loader
# import utils.data_loader as data_loader
import to_visual.utils.display as display
# import utils.display as display
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
from sklearn.metrics.pairwise import haversine_distances

import to_visual.charging_behavior.where_to_charge.NN_utility_model as NN_utility_model
# import charging_behavior.where_to_charge.NN_utility_model as NN_utility_model

display.configure_pandas()
display.configure_logging()
tqdm.pandas()


def generation(amount=10, df_cs=None):
    # rest schedule
    generated_rest = data_loader.load_generated()
    generated_rest = generated_rest.loc[generated_rest['id'] < amount]

    # CS location processing
    df_cs = df_cs.loc[~df_cs['cs_name'].isin(['LJDL', 'E04', 'BN0002', 'F11',
                                              'S1', 'S2', 'F12', 'F13', 'F15'])].reset_index()
    cs_location = df_cs[['Latitude', 'Longitude']].to_numpy()

    # Pick-up hotspots and  drop-off hotspots
    p_hs = data_loader.load_clusters()
    d_hs = data_loader.drop_clusters()
    p_hs = pd.DataFrame.from_dict(p_hs)
    d_hs = pd.DataFrame.from_dict(d_hs)

    with open('to_visual/generated_data/generation_input/departure_distributions.pickle', mode='rb') as f:
        departure_distributions = pickle.load(f)

    # Transit matrices
    with open('to_visual/data/transit_matrix/p2d_v3.list_of_df', 'rb') as f:
        p2d = pickle.load(f)
    with open('to_visual/data/transit_matrix/p2d_time_v3.list_of_df', 'rb') as f:
        p2d_t = pickle.load(f)
    with open('to_visual/data/transit_matrix/d2p_v3.list_of_df', 'rb') as f:
        d2p = pickle.load(f)
    with open('to_visual/data/transit_matrix/d2p_time_v3.list_of_df', 'rb') as f:
        d2p_t = pickle.load(f)
    p2d_distance = pd.read_csv('to_visual/generated_data/generation_input/p2d_distance.csv', index_col=[0, 1])['od_distance']
    d2p_distance = pd.read_csv('to_visual/generated_data/generation_input/d2p_distance.csv', index_col=[0, 1])[
        'distance_before_od']

    wtc_model, whether_charge_scaler = data_loader.pickle_load('if_to_charge')

    # Choose a device to deploy NN
    # device = 'cuda' if torch.cuda.is_available() else 'cpu'

    device = 'cpu'
    logging.info(device + ' is available')
    # 初始化模型并加载参数
    model = NN_utility_model.Net()
    model.to(device)
    # model_path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\preference_learning\pytorch_model\para_v2'
    model_path = 'to_visual/charging_behavior/where_to_charge/para_v3_30epoch.pkl'
    model.load_state_dict(torch.load(model_path,map_location=torch.device('cpu')))
    model.eval()
    softmax = torch.nn.Softmax(dim=1)

    def individual_generation(vehicle_rest, amount=10):
        # Initializaiton
        time_interval = timedelta(minutes=20)
        traveled_distance = 0
        start_timestamp = datetime(2014, 7, 1)
        current_timestamp = datetime(2014, 7, 1)

        generated_od = pd.DataFrame(
            columns=['license', 'begin_time', 'end_time', 'load_hotspot', 'drop_hotspot', 'od_distance',
                     'traveled_from_charged', 'to_charge', 'cs_index', 'cs_name'])

        for _, row in vehicle_rest.iterrows():
            if row['begin_hour'] == -1:
                row['begin_hour'] = 24
                row['rest_length'] = 0
            if current_timestamp > start_timestamp + timedelta(days=row['day'], hours=row['begin_hour']):
                status = 'rest'
            else:
                status = 'occupied'
                temp_distribution = departure_distributions[current_timestamp.hour]
                load_hs = temp_distribution.sample(1, weights=temp_distribution).index[0]
            while True:
                if 'occupied' == status:
                    # Get time interval
                    window_index = (current_timestamp.hour * 3600 + current_timestamp.minute * 60) // time_interval.seconds
                    # 根据时间窗口取转移矩阵
                    p2d_transit = p2d[window_index]
                    p2d_transit_t = p2d_t[window_index]

                    # if pick-up hot spot in p2d matrix
                    if load_hs not in p2d_transit.index:
                        # 寻找离当前出发hotspots最近的，有转移分布的hotspots作为替代出发hotspots
                        # select load hot spots geodetic coordinates
                        load_hotspots_loc = p_hs[['latitude', 'longitude']].values
                        # select coordinates of hot spots that have drop distribution
                        valid_load_hotspots_loc = load_hotspots_loc[p_hs.loc[p_hs['id'].isin(p2d_transit.index)].index]
                        # original load hot spot geodetic coordinate
                        load_offset = p_hs.loc[p_hs['id'] == load_hs].index[0]
                        loc_a = p_hs.loc[[load_offset], ['latitude', 'longitude']].values
                        # select nearest load hot spot
                        nearest_offset = haversine_distances(np.radians(loc_a),
                                                             np.radians(valid_load_hotspots_loc)).argmin()
                        load_hs = p_hs.loc[p_hs['id'].isin(p2d_transit.index), 'id'].iloc[nearest_offset]

                    transit_distribution = p2d_transit.loc[load_hs]
                    # select drop hotsopt by load hotspot and transit matrix
                    drop_hs = transit_distribution.sample(1, weights=transit_distribution).index[0]

                    move_duration = p2d_transit_t.loc[load_hs, drop_hs]
                    move_distance = p2d_distance[load_hs, drop_hs]

                    # Advance time and distance
                    current_timestamp += timedelta(seconds=move_duration)
                    traveled_distance += move_distance
                    #                 print(vehicle_rest.name, current_timestamp, 'p2d', load_hs, drop_hs, 'travel', move_distance)
                    pre_status = 'occupied'
                    status = 'empty'
                elif 'empty' == status:
                    # First predict charging behavior
                    if 'occupied' == pre_status:
                        d_offset = d_hs.loc[d_hs['id'] == drop_hs].index[0]
                        loc_d = d_hs.loc[[d_offset], ['latitude', 'longitude']].values
                        AVG_EARTH_RADIUS = 6371.0088
                        distances_to_cs = haversine_distances(np.radians(loc_d), np.radians(cs_location)) * AVG_EARTH_RADIUS
                        time_of_day = current_timestamp.hour + current_timestamp.minute / 60 + current_timestamp.second / 3600

                        whether_charge_features = [time_of_day, distances_to_cs.min(), distances_to_cs.max(),
                                                   distances_to_cs.mean(), np.median(distances_to_cs), traveled_distance]

                        whether_charge_features_scaled = whether_charge_scaler.transform(np.reshape(whether_charge_features,
                                                                                                    (1, -1)))
                        to_charge = wtc_model.predict(whether_charge_features_scaled)
                        #                   columns=['licence', 'begin_time', 'end_time', 'load_hotspot', 'drop_hotspot', 'od_distance',
                        #              'traveled_from_charged', 'to_charge', 'cs_index', 'cs_name'])
                        if to_charge & (traveled_distance < 40):
                            to_charge = np.array([0])
                        elif ~to_charge & (traveled_distance > 180):
                            to_charge = np.array([1])
                        if to_charge:
                            status = 'charging'
                            continue
                        else:
                            # Generate data
                            record = [vehicle_rest.name, current_timestamp - timedelta(seconds=move_duration),
                                      current_timestamp, load_hs, drop_hs, move_distance, traveled_distance,
                                      to_charge[0], None, None]
                            generated_od.loc[generated_od.shape[0]] = record
                    if current_timestamp > start_timestamp + timedelta(days=row['day'], hours=row['begin_hour']):
                        status = 'rest'
                    else:
                        # Get time interval
                        window_index = (current_timestamp.hour * 3600 + current_timestamp.minute * 60) \
                                       // time_interval.seconds
                        # 根据时间窗口取转移矩阵
                        d2p_transit = d2p[window_index]
                        d2p_transit_t = d2p_t[window_index]

                        # if drop-off hot spot in d2p matrix
                        if (drop_hs not in d2p_transit.index) or ():
                            # 寻找离当前drop hotspots最近的，有转移分布的hotspot作为替代drop hotspot
                            # select drop-off hot spots geodetic coordinates
                            drop_hotspots_loc = d_hs[['latitude', 'longitude']].values
                            # select coordinates of hot spots that have load distribution
                            valid_drop_hotspots_loc = drop_hotspots_loc[d_hs.loc[d_hs['id'].isin(d2p_transit.index)].index]
                            # original drop hot spot geodetic coordinate
                            d_offset = d_hs.loc[d_hs['id'] == drop_hs].index[0]
                            loc_a = d_hs.loc[[d_offset], ['latitude', 'longitude']].values
                            # select nearest drop hot spot
                            nearest_offset = haversine_distances(np.radians(loc_a),
                                                                 np.radians(valid_drop_hotspots_loc)).argmin()
                            drop_hs = d_hs.loc[d_hs['id'].isin(d2p_transit.index), 'id'].iloc[nearest_offset]
                        transit_distribution = d2p_transit.loc[drop_hs]
                        # select load hotsopt by drop hotspot and transit matrix

                        load_hs = transit_distribution.sample(1, weights=transit_distribution).index[0]
                        move_duration = d2p_transit_t.loc[drop_hs, load_hs]
                        move_distance = d2p_distance[drop_hs, load_hs]
                        # Advance time and distance
                        current_timestamp += timedelta(seconds=move_duration)
                        traveled_distance += move_distance
                        #                         print(vehicle_rest.name, current_timestamp, 'd2p', drop_hs, load_hs, 'travel', move_distance)
                        status = 'occupied'
                elif 'charging' == status:
                    where_charge_features = pd.DataFrame(index=range(len(df_cs.index)))
                    #                 [traveled_distance, distances_to_cs.min(), np.median(distances_to_cs),
                    #                                                distances_to_cs.mean(), distances_to_cs.max(), time_of_day]
                    where_charge_features['max_dis'] = distances_to_cs.max()
                    where_charge_features['mean_dis'] = distances_to_cs.mean()
                    where_charge_features['mid_dis'] = np.median(distances_to_cs)
                    where_charge_features['min_dis'] = distances_to_cs.min()
                    where_charge_features['traveled_after_charged'] = traveled_distance
                    where_charge_features['distance'] = distances_to_cs.reshape((-1))
                    where_charge_features['weekday'] = 1 if current_timestamp.weekday() < 5 else 0
                    where_charge_features['time_of_day'] = time_of_day
                    where_charge_features['chg_points'] = df_cs['chg_points']
                    data = torch.from_numpy(where_charge_features.to_numpy()).to(device).float()
                    data = data.view(-1, len(df_cs.index), len(where_charge_features.columns))
                    output = model(data)

                    output = softmax(output).view(-1).cpu().detach().numpy()
                    station_index = np.random.choice(len(output), 1, p=output).item()

                    #                 print('CS:', df_cs.loc[station_index, 'cs_name'], 'probability:', output[station_index])
                    # Generate data
                    record = [vehicle_rest.name, current_timestamp - timedelta(seconds=move_duration),
                              current_timestamp, load_hs, drop_hs, move_distance, traveled_distance, to_charge[0],
                              station_index, df_cs.loc[station_index, 'cs_name']]
                    generated_od.loc[generated_od.shape[0]] = record
                    current_timestamp += timedelta(hours=1.5)
                    pre_status = 'charging'
                    traveled_distance = 0
                    status = 'empty'
                elif 'rest' == status:
                    #                 print('rest', current_timestamp)
                    current_timestamp += timedelta(hours=row['rest_length'])
                    break
        return generated_od
    generated_od = generated_rest.groupby('id').progress_apply(individual_generation, amount=amount)
    return generated_od.reset_index(drop=True)


# if __name__ == '__main__':
#     df_cs, dates = data_loader.load_cs(date=datetime(2014, 7, 1))
#     # df_cs是充电站分布
#     datas = [[1,'A01',114.007401,22.535500,1,112],
#     [2 ,'FN0002',  114.009001 , 22.534233  ,     1      ,     6],
#     [3    ,'N04',  113.987547 , 22.560519    ,   1     ,     40],
#     [4   ,  'D08',  114.088303 , 22.562599   ,    1   ,       20],
#     [ 5   , 'LJDL' , 114.361504 , 22.678499   ,    2    ,      16],
#     [6   ,'D10',  114.074406,  22.559000    ,   1      ,    16],
#     [7  ,   'B04',  113.922977 , 22.546375    ,   1      ,    20],
#     [8  ,   'D01',  114.123241 , 22.562538    ,   1   ,       12],
#     [9   ,  'C01',  114.101748 , 22.582541     ,  1    ,      52],
#     [   10  ,   'E11',  114.068837 , 22.573326    ,   1     ,     20],
#     [11   ,  'A02',  114.023404 , 22.542650   ,    1     ,     16],
#     [12   ,  'E01',  114.023902 , 22.619512   ,    1      ,    16],
#     [13   ,  'F02',  113.817750 , 22.650682     ,  1    ,       8],
#     [14    , 'A08',  113.944128 , 22.506854  ,     1       ,   14],
#     [15   ,  'A09',  113.941642 , 22.527053   ,    1     ,     16],
#     [16   ,  'A10',  113.962844 , 22.528519   ,    1      ,    14],
#     [17,  'BN0002',  113.814932 , 22.651322    ,   2    ,      12],
#     [18  ,   'D06',  114.304419 , 22.600844    ,   1     ,     16],
#     [19  ,   'N02',  114.032902 , 22.524276   ,    1    ,      16],
#     [20   ,  'F07',  113.858390 , 22.579457    ,   1        ,   8],
#     [  21  ,   'A03',  113.995054 , 22.547247  ,     1     ,     16],
#     [  22  ,   'E04',  114.003978 , 22.636233   ,    2       ,   10],
#     [23   ,  'D09',  114.045125 , 22.551410    ,   1       ,   10],
#     [24   ,  'F08',  113.838486 , 22.609576     ,  1   ,       16],
#     [25,'F10',114.043404,22.601,1,12],
#     [26,'F11',113.985199,22.547701,2,12],
#     [27,'F12',113.8134,22.624201,1,100],
#     [28,'F13',114.135002,22.544001,1,100],
#     [29,'PSBYD',114.353401,22.679399,1,12],
#     [30,'S1',113.8564,22.616899,1,100],
#     [31,'F15',114.031502,22.5252,1,100],
#     [32,'S2',114.1798,22.5585,1,100]]
  
#     df_cs2 = pd.DataFrame(datas,columns=['ID','cs_name','Longitude','Latitude','Online','chg_points'])

#     print(df_cs2)
#     print(df_cs)
#     print(type(df_cs))
#     generated_data = generation(amount=10, df_cs=df_cs2)
#     generated_data.to_csv('generated_data/generated_data_v5.csv', index=False)

import pandas as pd
import logging
import glob
import os
import datetime
import pickle
# import config


project_path = r'C:\Users\hkrept\PycharmProjects\ElectricVehicleMobility'


def load_ce(scale='full', with_source=False, version=None):
    if 'full' == scale:
        if with_source:
            if version is None:
                path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\ce\ce_with_source_info_v9.csv'
            else:
                path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\ce\ce_with_source_info_' + version + '.csv'
            parse_dates = ['begin_time', 'start_charging', 'end_time', 'source_t']
        else:
            if version is None:
                path = os.path.join(project_path, 'data/ce_v5_30min.csv')
                parse_dates = ['arrival_time', 'start_charging', 'begin_time', 'end_time', 'waiting_duration',
                               'charging_duration']
            else:
                path = r'data/ce/' + version + '.csv'
                parse_dates = ['arrival_time', 'start_charging', 'end_time', 'waiting_duration', 'charging_duration']
                logging.info('Loading ' + path)
                temp_df = pd.read_csv(path, parse_dates=parse_dates)
                return temp_df
    elif 'part' == scale:
        raise NotImplementedError
    else:
        raise NotImplementedError
    logging.info('Loading ' + path)
    temp_df = pd.read_csv(path, parse_dates=parse_dates)
    temp_df['waiting_duration'] = temp_df['waiting_duration'].apply(pd.Timedelta)
    temp_df['charging_duration'] = temp_df['charging_duration'].apply(pd.Timedelta)
    return temp_df


def load_trajectory(with_status=False):
    if with_status:
        path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\trajectory\trajectories_with_dis_status.csv'

        logging.info('Loading ' + path)
        return pd.read_csv(path, sep=',', parse_dates=['timestamp'], infer_datetime_format=True, low_memory=False,
                           usecols=['timestamp', 'Licence', 'Longitude', 'Latitude', 'Speed', 'cs_index', 'cs_lat',
                                    'cs_log', 'cs_name', 'cs_points', 'distance_to_cs', 'cs_date', 'status'],
                           na_values=['nan', '?', 'NaN'], header=0, index_col=None)
    else:
        path = os.path.join(project_path, 'data/history_trajectories.csv')
        logging.info('Loading ' + path)
        return pd.read_csv(path, sep=',', parse_dates=['timestamp'], infer_datetime_format=True, low_memory=False,
                           usecols=['plate', 'longitude', 'latitude', 'timestamp', 'velocity'])


def load_trajectory_od_intersection():
    path = 'data/201407et_list.pickle'
    with open(path, 'rb') as f:
        traj_od_common = pickle.load(f)
    return traj_od_common


def load_od(scale='full', with_hotpots=False, with_feature=False, with_distance=False, version='v3', common=True):
    if not common:
        path = r'data/transaction_201407.csv'
        logging.info('Loading ' + path)
        df = pd.read_csv(path, parse_dates=['begin_time', 'end_time'], infer_datetime_format=True, low_memory=False)
        return df
    if 'full' == scale:
        if with_hotpots:
            path = 'data/od/full_od_with_hotpots_' + version + '.csv'
            logging.info('Loading ' + path)
            df = pd.read_csv(path, parse_dates=['begin_time', 'end_time'], infer_datetime_format=True, low_memory=False)
            df.fillna(value={'load_label': -1, 'drop_label': -1}, axis=0, inplace=True)
            df = df.astype({'load_label': int, 'drop_label': int})
            return df
        elif with_feature:
            path = 'data/od/od_with_traveled_v5.csv'
            logging.info('Loading ' + path)
            df = pd.read_csv(path, parse_dates=['begin_time', 'end_time'], infer_datetime_format=True, low_memory=False)
            df['seeking_duration'] = pd.to_timedelta(df['seeking_duration'])
            return df
        elif with_distance:
            path = r'data/od/od_with_distance_between_before.csv'
            logging.info('Loading' + path)
            df = pd.read_csv(path, parse_dates=['begin_time', 'end_time', 'last_drop_time'], infer_datetime_format=True,
                             low_memory=False)
            return df
        else:
            path = 'data/transaction_common_201407.csv'
    elif 'part' == scale:
        if with_hotpots:
            path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\od\od_with_hotpots.csv'
        else:
            path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\od\part_od_20140704_05.csv'
    else:
        raise NotImplementedError
    logging.info('Loading ' + path)
    df = pd.read_csv(path, parse_dates=['begin_time', 'end_time'], infer_datetime_format=True, low_memory=False)
    return df


def load_cs(scale='full', date=datetime.datetime(2014, 7, 1)):
    path = 'data/cs/ChargeLocation' + date.strftime('%Y%m')
    logging.info('Loading' + path)
    df_cs = pd.read_csv(path, sep=',', names=['ID', 'cs_name', 'Longitude', 'Latitude', 'Online', 'chg_points'],
                        infer_datetime_format=True, low_memory=False, na_values=['nan', '?', 'NaN'])
    dates_ = date
    return df_cs, dates_


def load_clusters():
    load_data_path = 'to_visual/data/transit_matrix/full_load_clusters.list_of_dict_v4'
    logging.info('Load ' + load_data_path)
    with open(load_data_path, 'rb') as f:
        load_hotpots = pickle.load(f)
    return load_hotpots


def drop_clusters():
    drop_cluster_path = 'to_visual/data/transit_matrix/full_drop_clusters.list_of_dict_v4'
    logging.info('Load ' + drop_cluster_path)
    with open(drop_cluster_path, 'rb') as f:
        drop_clusters = pickle.load(f)
    return drop_clusters


def road_shp():
    road_shp_wgs84_path = r'C:\Users\hkrep\PycharmProjects\ChargingEventsExtraction\data\SZXshp\road_wgs84.csv'
    logging.info('Load ' + road_shp_wgs84_path)
    road_shp_wgs84 = pd.read_csv(road_shp_wgs84_path)
    return road_shp_wgs84


# def load_driver_work_info():
#     path = config.driver_start_work_info_path
#     driver_work_info = pd.read_csv(path, )
#     return driver_work_info


def pickle_load(file=None):

    if 'if_to_charge' == file:
        model_path = 'to_visual/charging_behavior/whether_to_charge/model_80train.pickle'
        logging.info('Loading ' + model_path)
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        scaler_path = 'to_visual/charging_behavior/whether_to_charge/StandardScaler.pickle'
        logging.info('Loading ' + scaler_path)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    else:
        raise NotImplementedError
    return file


def load_rest():
    path = 'data/rest/rest_events.csv'
    logging.info('Loading' + path)
    rest_events = pd.read_csv(path, parse_dates=['start_time', 'end_time', 'duration'], infer_datetime_format=True)
    return rest_events


def load_generated(version='v1'):
    path = r'to_visual/data/rest/generated_rest_event_' + version + '.csv'
    logging.info('Loading' + path)
    generated_rest = pd.read_csv(path)
    return generated_rest

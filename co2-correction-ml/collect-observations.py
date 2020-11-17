import pandas as pd
import os
import numpy as np
from glob import glob

import datetime

workspace_path = '/Users/monicazhu/Box/CS189-Project-Shared'
obs_path = os.path.join(workspace_path, 'node_measurements')
emission_path = os.path.join(workspace_path, 'Emissions')
footprint_path = os.path.join(workspace_path, 'Footprint/compressedFoot')
obs_feature_path = os.path.join(workspace_path, 'node_measurements_feature_attach')

fp_filenames_all = os.listdir(footprint_path)
emis_filenames_all = os.listdir(emission_path)
node_info = pd.read_csv(os.path.join(workspace_path, 'beaconNodes.csv'))
node_info.set_index('id')


def read_node_lon_lat_obs_file(data):
    node_id = np.unique(data['node_id'].values)
    node_lon = node_info.loc[node_id, 'lng'].values
    node_lat = node_info.loc[node_id, 'lat'].values
    return node_lon, node_lat

def find_emis_file_using_lon_lat_datetime(timestamp):
    data_pattern = 'BEACON_{:04}x{:02}x{:02}x{:02}'.format(timestamp.year, timestamp.month, timestamp.day,
                                                                    timestamp.hour)
    emis_filename = [emis_name for emis_name in emis_filenames_all if data_pattern in emis_name]
    if len(emis_filename) == 1:
        print('Attach emission file at {}'.format(timestamp))
    else:
        if len(emis_filename) == 0:
            print('There is no emis file at {}'.format(timestamp))
        else:
            print('More than one file is found at {}'.format((timestamp)))
    return emis_filename

def find_foot_print_file_using_lon_lat_datetime(node_lon, node_lat, timestamp):
    data_pattern = 'obs_{:04}{:02}{:02}{:02}_{:g}_{:g}'.format(timestamp.year, timestamp.month,
                                                                        timestamp.day, timestamp.hour,
                                                                        node_lon[0], node_lat[0])
    fp_filename = [fp_name for fp_name in fp_filenames_all if data_pattern in fp_name]
    if len(fp_filename) == 1:
        print('Attach footprint file at {} for node at {}, {}'.format(timestamp, node_lon[0], node_lat[0]))
    else:
        fp_filename = []
        print('There is no fp file at {} for node at {}, {}'.format(timestamp, node_lon[0], node_lat[0]))
    return fp_filename

def collect_obs():
    obs_filenames = sorted(glob(os.path.join(obs_path, '*.csv')))
    for obs_filename in obs_filenames:
        data = pd.read_csv(os.path.join(obs_path, obs_filename))
        data['timestamp'] = pd.to_datetime(data['local_timestamp'], format='%Y-%m-%d  %H:%M:%S')
        data.index = data['timestamp']
        node_lon, node_lat = read_node_lon_lat_obs_file(data)
        emis_files = []
        fp_files = []
        data.rename(columns={'co2_corrected_avg_drift_applied': 'co2'}, inplace=True)
        data['lon'] = node_lon[0]
        data['lat'] = node_lat[0]
        for timestamp in data.index:
            fp_filename = find_foot_print_file_using_lon_lat_datetime(node_lon, node_lat, timestamp)
            fp_files.append(fp_filename)
            emis_filename = find_emis_file_using_lon_lat_datetime(timestamp)
            emis_files.append(emis_filename)
        data['emis_files'] = emis_files
        data['fp_files'] = fp_files
        data = data.drop(['local_timestamp', 'epoch', 'datetime', 'node_id', 'node_file_id', 'timestamp'], axis=1)
        save_name = os.path.join(obs_feature_path, os.path.basename(obs_filename))
        data.to_csv(save_name)




if __name__ == '__main__':
    collect_obs()
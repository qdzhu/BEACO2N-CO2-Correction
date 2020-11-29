from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

import pandas as pd
import os
import numpy as np
from glob import glob
import geopy.distance
from co2correction import utils
import pytz

workspace_path = '/Users/monicazhu/Box/CS189-Project-Shared'
obs_path = os.path.join(workspace_path, 'node_measurements')
emission_path = os.path.join(workspace_path, 'Emissions')
footprint_path = os.path.join(workspace_path, 'Footprint/compressedFoot')
obs_feature_path = os.path.join(workspace_path, 'node_measurements_feature_attach')
obs_merge_path = os.path.join(workspace_path, 'obs_feature_merge')
ref_obs_path = os.path.join(workspace_path, 'reference_site_measurements')
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


def read_emis_weight_by_sp(emis_file, fp_file, mask):
    emis, lon, lat = utils.read_emis_from_emission_file(emis_file)
    foot, lon, lat = utils.read_footprint_file(fp_file)
    emisxfoot = emis[mask] * foot[mask]
    return emisxfoot


def read_ref_obs():
    ref_obs_filenames = sorted(glob(os.path.join(ref_obs_path, '*Picarro*.csv')))
    ref_collections = []
    for ref_filename in ref_obs_filenames:
        data = pd.read_csv(os.path.join(ref_obs_path, ref_filename))
        data['timestamp'] = pd.to_datetime(data['local_timestamp'], format='%Y-%m-%d  %H:%M:%S')
        data.index = data['timestamp']
        data.rename(columns={'co2_dry_sync': 'ref_co2'}, inplace=True)
        data['ref_lon'] = -122.336
        data['ref_lat'] = 37.913
        data = data.drop(['local_timestamp', 'epoch', 'datetime', 'node_id', 'node_file_id', 'timestamp'], axis=1)
        ref_collections.append(data)
    ref_co2 = pd.concat(ref_collections)
    return ref_co2


def read_ref_temp():
    ref_temp_filename = sorted(glob(os.path.join(ref_obs_path, '*temperature*.csv')))
    data = pd.read_csv(os.path.join(ref_obs_path, ref_temp_filename[0]))
    data['timestamp'] = pd.to_datetime(data['local_timestamp'], format='%Y-%m-%d  %H:%M:%S')
    data.index = data['timestamp']
    data.rename(columns={'temp': 'ref_temp'}, inplace=True)
    data = data.drop(['local_timestamp', 'epoch', 'datetime', 'node_id', 'node_file_id', 'timestamp'], axis=1)
    data.reset_index(inplace=True)
    return data


def collect_obs():
    obs_filenames = sorted(glob(os.path.join(obs_path, '*.csv')))
    for obs_filename in obs_filenames:
        save_name = os.path.join(obs_feature_path, os.path.basename(obs_filename))
        if os.path.isfile(save_name):
            print('File already exist.')
            continue
        else:
            data = pd.read_csv(os.path.join(obs_path, obs_filename))
            data['timestamp'] = pd.to_datetime(data['local_timestamp'], format='%Y-%m-%d  %H:%M:%S')
            data.index = data['timestamp']
            node_lon, node_lat = read_node_lon_lat_obs_file(data)
            emis_files = []
            fp_files = []
            data.rename(columns={'co2_corrected_avg_drift_applied': 'co2'}, inplace=True)
            data['lon'] = node_lon[0]
            data['lat'] = node_lat[0]
            local = pytz.timezone("America/Los_Angeles")
            for timestamp in data.index:
                local_dt = local.localize(timestamp, is_dst=None)
                utc_timestamp = local_dt.astimezone(pytz.utc)
                fp_filename = find_foot_print_file_using_lon_lat_datetime(node_lon, node_lat, utc_timestamp)
                fp_files.append(fp_filename)
                emis_filename = find_emis_file_using_lon_lat_datetime(utc_timestamp)
                emis_files.append(emis_filename)
            data['emis_files'] = emis_files
            data['fp_files'] = fp_files
            data = data.drop(['local_timestamp', 'epoch', 'datetime', 'node_id', 'node_file_id', 'timestamp'], axis=1)
            data.to_csv(save_name)


def merge_obs():
    coll_obs_filenames = sorted(glob(os.path.join(obs_feature_path, '*.csv')))
    save_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref.csv'))
    if os.path.isfile(save_name):
        print('Merged file already exist.')
    else:
        obs_collections = []
        for coll_filename in coll_obs_filenames:
            data = pd.read_csv(os.path.join(obs_feature_path, coll_filename))
            obs_collections.append(data)
        merged_obs = pd.concat(obs_collections)
        merged_obs = merged_obs[merged_obs["fp_files"].apply(len).gt(2)]
        merged_obs['timestamp'] = pd.to_datetime(merged_obs['timestamp'], format='%Y-%m-%d  %H:%M:%S')
        ref_obs = read_ref_obs()
        ref_obs.reset_index(inplace=True)
        ref_temp = read_ref_temp()
        ref_obs = ref_obs.merge(ref_temp, how='left', left_on='timestamp', right_on='timestamp')
        merged_obs = merged_obs.merge(ref_obs, how='left', left_on='timestamp', right_on='timestamp')
        merged_obs = merged_obs.dropna()
        merged_obs.to_csv(save_name)


def make_dist_features():
    coll_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref.csv'))
    save_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref_plus_dist.csv'))
    if os.path.isfile(save_name):
        print('Merge file already updated to include reference temperature.')
    else:
        data = pd.read_csv(coll_name)
        locations = data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
        lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
        lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]
        lon, lat = utils.read_lon_lat_from_emission_file(data.loc[0, 'emis_files'][2:-2])
        mesh_lon, mesh_lat = np.meshgrid(lon, lat)
        mask = (mesh_lon >= lon_lim[0]) & (mesh_lon <= lon_lim[1]) \
               & (mesh_lat >= lat_lim[0]) & (mesh_lat <= lat_lim[1])
        ref_lon = data.loc[0, 'ref_lon']
        ref_lat = data.loc[0, 'ref_lat']
        dist_to_ref = []
        for index, row in data.iterrows():
            print('Working on row {}'.format(index))
            obs_lon = row['lon']
            obs_lat = row['lat']
            this_dist = geopy.distance.distance((ref_lat, ref_lon), (obs_lat, obs_lon)).km
            dist_to_ref.append(this_dist)
        data.loc[:, 'dist_to_ref'] = dist_to_ref
        data.to_csv(save_name)


def make_features_from_emis_fp_files():
    coll_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref_plus_dist.csv'))
    save_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_full_features_ref_plus_dist.csv'))
    if os.path.isfile(save_name):
        print('Merge file already updated to include features emission weighted footprint.')
    else:
        data = pd.read_csv(coll_name)
        locations = data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
        lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
        lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]
        lon, lat = utils.read_lon_lat_from_emission_file(data.loc[0, 'emis_files'][2:-2])
        mesh_lon, mesh_lat = np.meshgrid(lon, lat)
        mask = (mesh_lon >= lon_lim[0]) & (mesh_lon <= lon_lim[1]) \
               & (mesh_lat >= lat_lim[0]) & (mesh_lat <= lat_lim[1])
        new_cols = ['ef_{:02}'.format(i) for i in range(np.sum(mask))]
        emis_times_fp_colls = []
        for index, row in data.iterrows():
            print('Working on row {}'.format(index))
            emis_file = row['emis_files'][2:-2]
            fp_file = row['fp_files'][2:-2]
            try:
                emis_times_fp = read_emis_weight_by_sp(emis_file, fp_file, mask)
            except Exception:
                emis_times_fp = np.empty(len(new_cols)) + np.nan
            emis_times_fp_colls.append(emis_times_fp)
        data.loc[:, new_cols] = np.array(emis_times_fp_colls)
        data.to_csv(save_name)


def make_supp_feature_info():
    coll_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_full_features_ref_plus_dist.csv'))
    save_name = os.path.join(obs_merge_path, os.path.basename('ef_feature_info.csv'))
    if os.path.isfile(save_name):
        print('Supplementary file for ef features are created.')
    else:
        data = pd.read_csv(coll_name)
        locations = data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
        lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
        lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]
        lon, lat = utils.read_lon_lat_from_emission_file(data.loc[0, 'emis_files'][2:-2])
        mesh_lon, mesh_lat = np.meshgrid(lon, lat)
        mask = (mesh_lon >= lon_lim[0]) & (mesh_lon <= lon_lim[1]) \
               & (mesh_lat >= lat_lim[0]) & (mesh_lat <= lat_lim[1])
        lon_mask = mesh_lon[mask]
        lat_mask = mesh_lat[mask]
        emis_cols = ['ef_{:02}'.format(i) for i in range(np.sum(mask))]
        supp = pd.DataFrame(data={'column_name': emis_cols, 'mask_lon': lon_mask, 'mask_lat': lat_mask})
        supp.to_csv(save_name)


def trim_redundant_features():
    coll_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_full_features_ref_plus_dist.csv'))
    supp_name = os.path.join(obs_merge_path, os.path.basename('ef_feature_info.csv'))
    coll_save_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_full_features_ref_plus_dist_filter.csv'))
    if os.path.isfile(coll_save_name):
        print('Merge file already updated to include features emission weighted footprint.')
    else:
        data = pd.read_csv(coll_name)
        supp_data = pd.read_csv(supp_name)
        column_names = supp_data.loc[:, 'column_name'].values
        indx = data.loc[:, column_names] <= 1e-5
        data.loc[:, column_names][indx] = 0
        nonredundant_columns = column_names[(data.loc[:, column_names] > 1e-5).any()]
        redundant_columns = [column for column in column_names if column not in nonredundant_columns]
        data = data.drop(redundant_columns, axis=1)
        data = data.dropna()
        data.to_csv(coll_save_name)



if __name__ == '__main__':
    collect_obs()
    merge_obs()
    make_dist_features()
    make_features_from_emis_fp_files()
    make_supp_feature_info()
    trim_redundant_features()



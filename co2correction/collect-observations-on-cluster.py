from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

import pandas as pd
import os
import numpy as np
from co2correction import utils

workspace_path = '/Users/monicazhu/Box/CS189-Project-Shared'
obs_merge_path = os.path.join(workspace_path, 'obs_feature_merge')


def read_emis_weight_by_sp(emis_file, fp_file, mask):
    emis, lon, lat = utils.read_emis_from_emission_file(emis_file)
    foot, lon, lat = utils.read_footprint_file(fp_file)
    emisxfoot = emis[mask] * foot[mask]
    return emisxfoot


def make_features_from_emis_fp_files():
    coll_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref_plus_dist.csv'))
    save_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_full_features_ref_plus_dist.csv'))
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
    new_cols = ['ef_{:02}'.format(i) for i in range(np.sum(mask))]
    emis_times_fp_colls = []
    for index, row in data.iterrows():
        print('Working on row {}'.format(index))
        emis_file = row['emis_files'][2:-2]
        fp_file = row['fp_files'][2:-2]
        obs_lon = row['lon']
        obs_lat = row['lat']
        try:
            emis_times_fp = read_emis_weight_by_sp(emis_file, fp_file, mask)
        except OSError:
            emis_times_fp = np.empty(len(new_cols)) + np.nan
        emis_times_fp_colls.append(emis_times_fp)
    data.loc[:, new_cols] = np.array(emis_times_fp_colls)
    data.to_csv(save_name)

if __name__ == '__main__':
    make_features_from_emis_fp_files()
from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())
import netCDF4 as nc
import datetime
import os
import numpy as np

workspace_path = '/Users/monicazhu/Box/CS189-Project-Shared'
obs_path = os.path.join(workspace_path, 'node_measurements')
emission_path = os.path.join(workspace_path, 'Emissions')
footprint_path = os.path.join(workspace_path, 'Footprint/compressedFoot')
obs_feature_path = os.path.join(workspace_path, 'node_measurements_feature_attach')
obs_merge_path = os.path.join(workspace_path, 'obs_feature_merge')
ref_obs_path = os.path.join(workspace_path, 'reference_site_measurements')

def read_footprint_file(filename):
    ds = nc.Dataset(os.path.join(footprint_path, filename))
    lon = ds['lon'][:]
    lat = ds['lat'][:]
    foot_lon, foot_lat = np.meshgrid(lon, lat)
    foot = ds['foot'][:]
    fp_times_deltas = ds['time'][:]
    fp_times = []
    for time_delta in fp_times_deltas:
        this_datetime = datetime.timedelta(seconds=int(time_delta)) + datetime.datetime(1970, 1, 1)
        fp_times.append(this_datetime)

    return foot, lon, lat


def read_emis_from_emission_file(filename):
    ds = nc.Dataset(os.path.join(emission_path, filename))
    emis = ds['ems_total'][:]
    lon = ds['lon'][:]
    lat = ds['lat'][:]
    return emis, lon, lat


def read_lon_lat_from_emission_file(filename):
    ds = nc.Dataset(os.path.join(emission_path, filename))
    lon = ds['lon'][:]
    lat = ds['lat'][:]
    return lon, lat


def read_info_from_emission_filename(filename):
    filename_parts = filename.split("_")[1].split(".")[0]
    emis_year = int(filename_parts.split("x")[0])
    emis_month = int(filename_parts.split("x")[1])
    emis_day = int(filename_parts.split("x")[2])
    emis_hour = int(filename_parts.split("x")[3])
    emis_datetime = datetime.datetime(emis_year, emis_month, emis_day, emis_hour)
    return emis_datetime
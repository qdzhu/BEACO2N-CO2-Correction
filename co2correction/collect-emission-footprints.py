from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

from mpl_toolkits.basemap import Basemap
from matplotlib import pyplot as plt
import datetime
from glob import glob
import numpy as np
import netCDF4 as nc
import os
from co2correction import utils
import os.path

workspace_path = '/Users/monicazhu/Box/CS189-Project-Shared'
emission_path = os.path.join(workspace_path, 'Emissions')
footprint_path = os.path.join(workspace_path, 'Footprint/compressedFoot')
feature_path = os.path.join(workspace_path, 'Features')

def read_obs_info_from_footprint_filename(filename):
    filename_parts = filename.split("_")
    obs_lon = filename_parts[2]
    obs_lat = filename_parts[3]
    obs_alt = filename_parts[4].split('.')[0]
    obs_datetime = datetime.datetime.strptime(filename_parts[1], '%Y%m%d%H')
    return obs_datetime, obs_lon, obs_lat, obs_alt

def read_footprint_file(filename, do_plot=False):
    obs_datetime, obs_lon, obs_lat, obs_alt = read_obs_info_from_footprint_filename(filename)
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

    if do_plot:
        lon_lim = [np.min(lon), np.max(lon)]
        lat_lim = [np.min(lat), np.max(lat)]
        foot_map = Basemap(projection='cyl', resolution='h',
                      llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
        foot_map.shadedrelief()
        foot_map.drawparallels(lat, labels=[1, 0, 0, 0])
        foot_map.drawmeridians(lat, labels=[0, 0, 0, 1])
        im = foot_map.pcolormesh(foot_lon, foot_lat, foot, shading='flat', cmap=plt.cm.jet)
        im.set_alpha(0.5)
        cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%")
        plt.savefig('foot.png')

    return obs_datetime, obs_lon, obs_lat, obs_alt, lon, lat, foot


def read_emis_from_emission_file(filename):
    ds = nc.Dataset(os.path.join(emission_path, filename))
    emis = ds['ems_total'][:]
    return emis



def collect_emis():
    em_filenames = sorted(os.listdir(emission_path))
    read_lon_lat = True
    emis_datetimes = []
    emis_col = []
    for em_filename in em_filenames:
        this_emis_datetime = utils.read_info_from_emission_filename(em_filename)
        if this_emis_datetime.year == 2020 or this_emis_datetime.year == 2017:
            print("Only 2018 and 2019 data are selected.\n")
        else:
            print("Reading" + em_filename + ".\n")
            if read_lon_lat:
                lon, lat = utils.read_lon_lat_from_emission_file(em_filename)
                read_lon_lat = False
            emis = read_emis_from_emission_file(em_filename)
            emis_datetimes.append(this_emis_datetime)
            emis_col.append(emis)


def collect_foot():
    fp_filenames = os.listdir(footprint_path)
    read_footprint_file(fp_filenames[0], do_plot=True)

if __name__ == '__main__':
    collect_foot()
    collect_emis()
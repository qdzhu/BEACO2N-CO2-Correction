from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())
import pandas as pd
import os
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib import pyplot as plt
from co2correction import utils
import numpy as np

workspace_path = '/Users/monicazhu/Box/CS189-Project-Shared'
obs_merge_path = os.path.join(workspace_path, 'obs_feature_merge')

def plot_obs_location():
    merge_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref.csv'))
    merged_data = pd.read_csv(merge_name)
    emis, lon, lat = utils.read_emis_from_emission_file(merged_data.loc[0, 'emis_files'][2:-2])
    mesh_lon, mesh_lat = np.meshgrid(lon, lat)
    locations = merged_data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
    plt.figure(figsize=[7, 7])
    lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
    lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]
    indx = (mesh_lon >= lon_lim[0]) & (mesh_lon <= lon_lim[1]) \
           & (mesh_lat >= lat_lim[0]) & (mesh_lat <= lat_lim[1])
    emis[~indx] = np.nan
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    #foot_map.bluemarble()
    foot_map.drawcounties(linewidth=1)
   # im = foot_map.pcolormesh(mesh_lon, mesh_lat, emis, shading='flat')
   # im.set_alpha(0.5)
    s = foot_map.scatter(locations['lon'], locations['lat'], c=locations['count'], marker='.', s=50)
    cb = foot_map.colorbar(s, "bottom", size="5%", pad="2%", label='Obs counts (#)')
    foot_map.scatter(merged_data.loc[0, 'ref_lon'], merged_data.loc[0, 'ref_lat'], marker='*', color='black', s=100)
    plt.savefig('obs_location.png')

def plot_one_case_emis_fp():
    merge_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref.csv'))
    merged_data = pd.read_csv(merge_name)
    emis, lon, lat = utils.read_emis_from_emission_file(merged_data.loc[1524, 'emis_files'][2:-2])
    fp, lon, lat = utils.read_footprint_file(merged_data.loc[1522, 'fp_files'][2:-2])
    emis[emis <= 0.01] = np.nan
    fp[fp <= 0.001] = np.nan
    mesh_lon, mesh_lat = np.meshgrid(lon, lat)
    locations = merged_data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
    lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
    lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]

    plt.figure(figsize=[15, 7])
    plt.subplot(1, 3, 1)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, emis, shading='flat', alpha=0.8)
    im.set_clim(0, 10)
    #s = foot_map.scatter(locations['lon'], locations['lat'], c='red', marker='.', s=50)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Emis (Ct/hour)')

    plt.subplot(1, 3, 2)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, fp, shading='flat', alpha=0.8)
    im.set_clim(0, 0.5)
    # s = foot_map.scatter(locations['lon'], locations['lat'], c='red', marker='.', s=50)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Footprint (unitless)')

    plt.subplot(1, 3, 3)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, emis*fp, shading='flat', alpha=0.8)
    im.set_clim(0, 1)
    # s = foot_map.scatter(locations['lon'], locations['lat'], c='red', marker='.', s=50)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Emis weighted by footprint')
    plt.savefig('emis_foot_emisxfoot.png')

if __name__ == '__main__':
    plot_one_case_emis_fp()
    plot_obs_location()


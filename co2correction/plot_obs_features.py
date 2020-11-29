from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())
import pandas as pd
import os
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib import pyplot as plt
from co2correction import utils
from matplotlib import animation as manim
import numpy as np
from glob import glob

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
    s = foot_map.scatter(locations['lon'], locations['lat'], c=locations['count'], marker='.', s=100)
    cb = foot_map.colorbar(s, "bottom", size="5%", pad="2%", label='Obs counts (#)')
    foot_map.scatter(merged_data.loc[0, 'ref_lon'], merged_data.loc[0, 'ref_lat'], marker='*', color='black', s=200)
    plt.savefig('obs_location.eps')


def plot_one_case_emis_fp():
    merge_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref.csv'))
    merged_data = pd.read_csv(merge_name)
    emis, lon, lat = utils.read_emis_from_emission_file('BEACON_2018x06x03x18.ncdf')
    fp_n1, lon, lat = utils.read_footprint_file('obs_2018060318_-122.275_37.974_3.nc')
    fp_n2, lon, lat = utils.read_footprint_file('obs_2018060318_-122.181_37.819_9.nc')
    location_n1 = [-122.275, 37.974]
    location_n2 = [-122.181, 37.819]
    emis[emis <= 0.01] = np.nan
    fp_n1[fp_n1 <= 0.001] = np.nan
    fp_n2[fp_n2 <= 0.001] = np.nan
    mesh_lon, mesh_lat = np.meshgrid(lon, lat)
    locations = merged_data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
    lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
    lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]

    plt.figure(figsize=[30, 7])
    plt.subplot(1, 5, 1)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, emis, shading='flat')
    im.set_clim(0, 1)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Emission')

    plt.subplot(1, 5, 2)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, fp_n1, shading='flat')
    im.set_clim(0, 0.01)
    foot_map.scatter(location_n1[0], location_n1[1], c='black', marker='.', s=100)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Footprint (unitless)')

    plt.subplot(1, 5, 3)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, fp_n2, shading='flat')
    im.set_clim(0, 0.01)
    foot_map.scatter(location_n2[0], location_n2[1], c='black', marker='.', s=100)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Footprint (unitless)')

    plt.subplot(1, 5, 4)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, emis*fp_n1, shading='flat')
    foot_map.scatter(location_n1[0], location_n1[1], c='black', marker='.', s=100)
    im.set_clim(0, 0.005)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Emis weighted by footprint')

    plt.subplot(1, 5, 5)
    foot_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    foot_map.drawcounties(linewidth=1)
    im = foot_map.pcolormesh(mesh_lon, mesh_lat, emis * fp_n2, shading='flat')
    im.set_clim(0, 0.005)
    foot_map.scatter(location_n2[0], location_n2[1], c='black', marker='.', s=100)
    cb = foot_map.colorbar(im, "bottom", size="5%", pad="2%", label='Emis weighted by footprint')

    plt.savefig('emis_foot_emisxfoot_ex1.eps')


def init_map(lon_lim, lat_lim, emis_file):
    emis, lon, lat = utils.read_emis_from_emission_file(emis_file)
    emis[emis <= 0.01] = np.nan
    mesh_lon, mesh_lat = np.meshgrid(lon, lat)
    emis_map = Basemap(projection='cyl', resolution='h',
                       llcrnrlon=lon_lim[0], llcrnrlat=lat_lim[0], urcrnrlon=lon_lim[1], urcrnrlat=lat_lim[1])
    emis_map.drawcounties(linewidth=1)
    im = emis_map.pcolormesh(mesh_lon, mesh_lat, emis, shading='flat')
    im.set_clim(0, 1)
    return im, emis_map

def update_map(im, emis_file):
    emis, lon, lat = utils.read_emis_from_emission_file(emis_file)
    emis[emis <= 0.01] = np.nan
    im.set_array(emis[:-1, :-1].ravel())


def make_emis_movie(movie_file):
    merge_name = os.path.join(obs_merge_path, os.path.basename('merged_obs_sim_features_ref.csv'))
    merged_data = pd.read_csv(merge_name)
    locations = merged_data.groupby(['lon', 'lat']).size().reset_index().rename(columns={0: 'count'})
    lon_lim = [np.min(locations['lon']) - 0.2, np.max(locations['lon']) + 0.2]
    lat_lim = [np.min(locations['lat']) - 0.2, np.max(locations['lat']) + 0.2]

    emis_files = sorted(glob(os.path.join(utils.emission_path, 'BEACON_2018x06x0[1-2]*')))

    writer = manim.FFMpegWriter(fps=2)
    plt.close()
    [im, emis_map] = init_map(lon_lim, lat_lim, emis_files[0])
    emis_map.colorbar(im, "bottom", size="5%", pad="2%", label='Emission')
    fig = plt.gcf()
    plt.savefig('init.png')
    with writer.saving(fig, movie_file, 100):
        for f_emis in emis_files:
            print('Writing frame {} of {} ({})'.format(emis_files.index(f_emis)+1, len(emis_files), f_emis))
            update_map(im, f_emis)
            emis_datetime = utils.read_info_from_emission_filename(f_emis)
            plt.title(emis_datetime.strftime("%m/%d/%Y, %H:%M:%S"))
            #savename = 'Frames/frame{:03d}.png'.format(emis_files.index(f_emis))
            #plt.savefig(savename)
            writer.grab_frame()

if __name__ == '__main__':
    plot_one_case_emis_fp()
    make_emis_movie('emis_movie_06_2018.mp4')
    plot_obs_location()




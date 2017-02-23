"""
Description:
    For a batch of MT_stations,  plot the Penetration Depth vs the station_location,
    for a given period-index (1/freq)-
    Note that the values of periods should be checked if equal across all stations.

Usage:
    python mtpy/imaging/penetration_depth_3d_profile.py /path2/edi_files_dir/  period_index

Author: fei.zhang@ga.gov.au
Date:   2017-01-23
"""

import sys
import os
import glob
import numpy as np
from scipy.interpolate import griddata

import matplotlib.pyplot as plt
import matplotlib as mpl


mpl.rcParams['lines.linewidth'] = 2
# mpl.rcParams['lines.color'] = 'r'

mpl.rcParams['figure.figsize']=[20,10]

import mtpy.core.mt as mt
import mtpy.utils.calculator

from mtpy.utils.mtpylog import MtPyLog

# get a logger object for this module, using the utility class MtPyLog to config the logger
logger = MtPyLog().get_mtpy_logger(__name__)
#logger = MtPyLog(path2configfile='logging.yml').get_mtpy_logger(__name__) # specific

def plot_latlon_depth_profile(edi_dir, period_index, zcomponent='det'): #use the Zcompotent=[det, zxy, zyx]
    """ MT penetration depth profile in lat-lon coordinates with pixelsize =0.002
    :param edi_dir:
    :param period_index:
    :param zcomponent:
    :return:
    """

    # edi_dir = "/Softlab/Githubz/mtpy2/tests/data/edifiles/"
    # edi_dir="E:/Githubz/mtpy2/tests/data/edifiles/"
    # edi_dir=r"E:\Githubz\mtpy2\examples\data/edi2"

    #1 get a list of edi files, which are suppose to be in a profile.
    edifiles = glob.glob(os.path.join(edi_dir, '*.edi'))

    logger.debug("edi files: %s", edifiles)

    (stations, periods, pendep, latlons) = get_penetration_depth(edifiles, period_index, whichrho=zcomponent)

    if check_period_values(periods) is False:
        logger.error("The period values are NOT equal - Please check: %s", periods)
        raise Exception("Period values Not Equal across MT stations EDI files. Please check")
    else:
        Period0 = periods[0]

    period_fmt= mtpy.utils.calculator.roundsf(Period0, 8)  # 8 signifiant digit
    bbox=get_bounding_box(latlons)

    logger.debug("Bounding Box %s", bbox)

    xgrids = bbox[0][1] - bbox[0][0]
    ygrids = bbox[1][1] - bbox[1][0]

    logger.debug("xy grids %s %s", xgrids, ygrids)

    minlat = bbox[1][0]
    minlon = bbox[0][0]

    # Pixel size in Degree:  0.001=100meters, 0.01=1KM 1deg=100KM
    pixelsize = 0.002  # Degree 0.001=100meters, 0.01=1KM 1deg=100KM

    nx = int(np.ceil(xgrids / pixelsize))
    ny = int(np.ceil(ygrids / pixelsize))

    print(nx, ny)

    # make an image bigger than the (nx, ny)
    pad = 4
    nx2 = nx + pad
    ny2 = ny + pad

    # Z = 0.0* np.random.random((nx2,ny2))   # Test data
    # Z=  np.ones((nx2,ny2))
    zdep = np.zeros((ny2, nx2))
    # Z[10, 10]=12
    # Z[11, 20]=20
    # Z[13, 15]=30

    zdep[:, :] = np.nan  # initialize all pixel value as np.nan

    logger.debug("zdep shape %s", zdep.shape)

    for iter, pair in enumerate(latlons):
        print pair
        (xi, yi) = get_index(pair[0], pair[1], minlat, minlon, pixelsize)
        zdep[zdep.shape[0] - yi-1, xi] = np.abs(pendep[iter])

    plt.imshow(zdep, interpolation='none')
    #plt.imshow(zdep,  interpolation='spline36')
    plt.colorbar()

    plt.show()

    # a new figure
    plt.figure(2)

# griddata interpolation of the zdep sample MT points.
    print(zdep.shape[0], zdep.shape[1])

    #grid_x, grid_y = np.mgrid[0:95:96j, 0:83:84j]  # this syntax with complex step 96j has different meaning
    grid_x, grid_y = np.mgrid[0:zdep.shape[0]:1, 0:zdep.shape[1]:1]  #this is more straight forward.

    # print (grid_x, grid_y)
    points = np.zeros((len(latlons), 2))
    values = np.zeros(len(latlons))

    for iter, pair in enumerate(latlons):
        #     print pair

        (i, j) = get_index(pair[0], pair[1], minlat, minlon, pixelsize)
        points[iter, 0] = zdep.shape[0] - j
        points[iter, 1] = i
        values[iter] = np.abs(pendep[iter])

    #grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    #grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

    # set the axix limit to avoid over extended
    plt.xlim(0, zdep.shape[1])      # horizontal axis 0-> the second index (i,j) of the matrix
    plt.ylim(zdep.shape[0], 0)     # vertical axis origin at upper corner, not the lower corner.

    # plt.imshow(grid_z)
    plt.imshow(grid_z, origin='upper')
    plt.plot(points[:, 1], points[:, 0], 'kv', markersize=6) #the stations sample point 1-lon-j, 0-lat-i

    # FZ: fix the axis ticks
    ax = plt.gca()

    xticks=np.arange(0,zdep.shape[1],10)
    yticks=np.arange(0,zdep.shape[0],10)

    xticks_label= ['%.3f'%(bbox[0][0] + pixelsize*xtick) for xtick in xticks]  # formatted float numbers
    yticks_label= ['%.3f'%(bbox[1][0] - pixelsize*ytick) for ytick in yticks]

    plt.xticks(xticks, xticks_label, rotation='0', fontsize=14)
    plt.yticks(yticks, yticks_label,rotation='horizontal', fontsize=14)
    ax.set_ylabel('Latitude(degree)', fontsize=14)
    ax.set_xlabel('Longitude(degree)',fontsize=14)

    plt.title('Penetration Depth at the Period=%.6f (Cubic Interpolation)' % period_fmt)  # Cubic
    plt.colorbar(label='Penetration Depth (meters)')#, fontsize=14)
    plt.gcf().set_size_inches(6, 6)

    plt.show()

# version-1
def plot_gridded_profile(edi_dir, period_index, zcomponent='det'): #use the Zcompotent=[det, zxy, zyx]
    """
    plot a  gridded profile of the pene depth projected into 2D matrix image
    :param edi_dir:
    :param period_index:
    :param zcomponent:
    :return:
    """
    #edi_dir = "/Softlab/Githubz/mtpy2/tests/data/edifiles/"
    # edi_dir="E:/Githubz/mtpy2/tests/data/edifiles/"
    # edi_dir=r"E:\Githubz\mtpy2\examples\data/edi2"

    #1 get a list of edi files, which are suppose to be in a profile.
    edifiles = glob.glob(os.path.join(edi_dir, '*.edi'))

    logger.debug("edi files: %s", edifiles)

    (stations, periods, pendep, latlons) = get_penetration_depth(edifiles, period_index, whichrho=zcomponent)

    bbox=get_bounding_box(latlons)

    logger.debug("Bounding Box %s", bbox)

    xgrids = bbox[0][1] - bbox[0][0]
    ygrids = bbox[1][1] - bbox[1][0]

    logger.debug("xy grids %s %s", xgrids, ygrids)

    minlat = bbox[1][0]
    minlon = bbox[0][0]

    # Pixel size in Degree:  0.001=100meters, 0.01=1KM 1deg=100KM

    pixelsize = 0.002  # Degree 0.001=100meters, 0.01=1KM 1deg=100KM

    nx = int(np.ceil(xgrids / pixelsize))
    ny = int(np.ceil(ygrids / pixelsize))

    print(nx, ny)

    # make an image bigger than the (nx, ny)
    pad = 4
    nx2 = nx + pad
    ny2 = ny + pad

    # Z = 0.0* np.random.random((nx2,ny2))   # Test data
    # Z=  np.ones((nx2,ny2))
    zdep = np.zeros((ny2, nx2))
    # Z[10, 10]=12
    # Z[11, 20]=20
    # Z[13, 15]=30

    zdep[:, :] = np.nan

    logger.debug("zdep shape %s", zdep.shape)

    for iter, pair in enumerate(latlons):
        print pair
        (xi, yi) = get_index(pair[0], pair[1], minlat, minlon, pixelsize)
        zdep[zdep.shape[0] - yi-1, xi] = np.abs(pendep[iter])

    plt.imshow(zdep) #,  interpolation='none')
    #plt.imshow(zdep,  interpolation='spline36')
    plt.colorbar()

    plt.show()

# griddata interpolation
    print(zdep.shape[0], zdep.shape[1])
    #grid_x, grid_y = np.mgrid[0:95:96j, 0:83:84j]  # this syntax with complex step 96j has different meaning
    grid_x, grid_y = np.mgrid[0:zdep.shape[0]:1, 0:zdep.shape[1]:1]  #this is more straight forward.

    # print (grid_x, grid_y)
    points = np.zeros((len(latlons), 2))
    values = np.zeros(len(latlons))

    for iter, pair in enumerate(latlons):
        #     print pair

        (i, j) = get_index(pair[0], pair[1], minlat, minlon, pixelsize)
        points[iter, 0] = zdep.shape[0] - j
        points[iter, 1] = i
        values[iter] = np.abs(pendep[iter])

    #grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    #grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

    # plt.imshow(grid_z)

    plt.subplot(111)

    plt.imshow(grid_z, origin='upper')
    plt.plot(points[:, 1], points[:, 0], 'kv', markersize=6) #stations

    plt.title('Cubic Interpolation of Penetration Depth at the Period=%6.5f' % periods[0])  # Cubic
    plt.colorbar()
    plt.gcf().set_size_inches(6, 6)

    plt.show()


def get_bounding_box(latlons):
    """ get min max lat lon from the list of lat-lon-pairs points"""
    lats = [tup[0] for tup in latlons]
    lons = [tup[1] for tup in latlons]

    minlat = min(lats)
    maxlat = max(lats)

    print(minlat, maxlat)

    minlon = min(lons)
    maxlon = max(lons)

    print(minlon, maxlon)

    return ((minlon, maxlon), (minlat, maxlat))


def get_index(lat, lon, minlat, minlon, pixelsize, offset=1):
    index_x = (lon - minlon) / pixelsize
    index_y = (lat - minlat) / pixelsize

    ix = int(round(index_x))
    iy = int(round(index_y))

    print (ix, iy)

    return (ix + offset, iy + offset)


def get_index2(lat, lon, LL_lat, LL_lon, pixelsize):
    """ Mapping of lat lon to a grid
    :param lat:
    :param lon:
    :param LL_lon:
    :param LL_lat:
    :param pixelsize:
    :return:
    """

    index_x = (lon - LL_lon) / pixelsize
    index_y = (lat - LL_lat) / pixelsize

    return (int(index_x), int(index_y))



def get_penetration_depth(edi_file_list, per_index,  whichrho='det'): #whichrho=[zxy, zyx, zdeterminant]
    """
    compute the penetration depths of a list of edi files at given period/freq
    :param edi_file_list:
    :param per_index: the index of periods 0,1,....
    :param whichrho:
    :return: tuple of (stations, periods, penetrationdepth, lat-lons-pairs)
    """

    scale_param = np.sqrt(1.0 / (2.0 * np.pi * 4 * np.pi * 10 ** (-7)))

    # per_index=0,1,2,....
    periods = []
    pendep = []
    stations = []
    latlons = []

    for afile in edi_file_list:
        mt_obj = mt.MT(afile)
        stations.append(mt_obj.station)
        latlons.append((mt_obj.lat, mt_obj.lon))

        # the attribute Z
        zeta = mt_obj.Z

        if per_index >= len(zeta.freq):
            logger.debug("Number of frequecies (Max per_index)= %s", len(zeta.freq))
            raise Exception("Index out_of_range Error: period index must be less than number of periods in zeta.freq")

        per = 1.0 / zeta.freq[per_index]
        periods.append(per)

        if whichrho == 'zxy':
            penetration_depth = - scale_param * np.sqrt(zeta.resistivity[per_index, 0, 1] * per)
        elif whichrho == 'zyx':
            penetration_depth = - scale_param * np.sqrt(zeta.resistivity[per_index, 1, 0] * per)
        elif whichrho == 'det':
            # determinant
            det2 = np.abs(zeta.det[0][per_index])  # determinant value at the given period index
            penetration_depth = -scale_param * np.sqrt(0.2 * per * det2 * per)
        else:
            logger.critical("un-supported method to compute penetration depth: %s", whichrho)
            sys.exit(100)

        pendep.append(penetration_depth)

    check_period_values(periods)

    return (stations, periods, pendep, latlons)

def check_period_values(period_list):
    """
    check if all the values are equal in the input list
    :param period_list: a list of period
    :return: True/False
    """

    logger.debug(period_list)

    p0= period_list[0] # first value as a ref
    pcounter=0
    for per in period_list:
        if per !=p0:
            logger.warn("Period Not Equal!! p0 VS per: %s VS %s", p0, per)
            return False
        else:
            pcounter=pcounter+1

    return True

#########################################################
def plot_bar3d_depth( edifiles, per_index):
    """
    plot 3D bar of penetration depths
    For a given freq/period index of a set of edifiles/dir, the station,periods, pendepth,(lat, lon) are extracted
    the geo-bounding box calculated, and the mapping from stations to grids is constructed and plotted.

    :param edifiles: an edi_dir or list of edi_files
    :param per_index: period index number 0,1,2

    :return:
    """

    if os.path.isdir(edifiles):
        edi_dir = edifiles # "E:/Githubz/mtpy2/tests/data/edifiles/"
        edifiles = glob.glob(os.path.join(edi_dir, '*.edi'))
        logger.debug(edifiles)
    else:
        # Assume edifiles is [a list of files]
        pass

    scale_param = np.sqrt(1.0 / (2.0 * np.pi * 4 * np.pi * 10 ** (-7)))

    # per_index=0,1,2,....
    periods = []
    pen_depth = []
    stations = []
    latlons = []

    for afile in edifiles:
        mt_obj = mt.MT(afile)

        latlons.append((mt_obj.lat, mt_obj.lon))

        # the attribute Z
        zeta = mt_obj.Z

        if per_index >= len(zeta.freq):
            raise Exception("Error: input period index must be less than the number of freqs in zeta.freq=%s", len(zeta.freq))
        per = 1.0 / zeta.freq[per_index]
        periods.append(per)

        penetration_depth = - scale_param * np.sqrt(zeta.resistivity[per_index, 0, 1] * per)
        pen_depth.append(penetration_depth)

        stations.append(mt_obj.station)

    #return (stations, periods, pen_depth, latlons)

    lats = [tup[0] for tup in latlons]
    lons = [tup[1] for tup in latlons]
    minlat = min(lats)
    maxlat = max(lats)
    minlon = min(lons)
    maxlon = max(lons)

    pixelsize = 0.001  # degree 0.001 = 100meters
    offset = 3
    LL_lat = minlat - offset * pixelsize
    LL_lon = minlon - offset * pixelsize

    xgrids = maxlon - minlon
    ygrids = maxlat - minlat

    nx = xgrids / pixelsize
    ny = ygrids / pixelsize

    from mpl_toolkits.mplot3d import Axes3D
    # import matplotlib.pyplot as plt
    # import numpy as np

    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection='3d')

    xpos = []  # a seq (1,2,3,4,5,6,7,8,9,10)
    ypos = []  # a seq [2,3,4,5,1,6,2,1,7,2]
    dz = []
    for iter, pair in enumerate(latlons):
        xpos.append(get_index(pair[0], pair[1],LL_lat, LL_lon, pixelsize)[0])
        ypos.append(get_index(pair[0], pair[1], LL_lat, LL_lon, pixelsize)[1])
        dz.append(np.abs(pen_depth[iter]))
        #dz.append(-np.abs(pen_depth[iter]))

    num_elements = len(xpos)
    zpos = np.zeros(num_elements)  # zpos = [0,0,0,0,0,0,0,0,0,0]
    dx = np.ones(num_elements)
    dy = np.ones(num_elements)
    # dz = [1,2,3,4,5,6,7,8,9,10]

    print(xpos)
    print(ypos)
    print(zpos)

    print(dx)
    print(dy)
    print(dz)
    ax1.bar3d(xpos, ypos, zpos, dx, dy, dz, color='r')

    #ax1

    plt.title('Penetration Depth (m) Across Stations. MT period= %6.3f Seconds' % periods[0], fontsize=16)
    plt.xlabel('Latitude (deg-grid)', fontsize=16)
    plt.ylabel('Longitude (deg-grid)', fontsize=16)
    #plt.zlabel('Penetration Depth (m)')
    # bar_width = 0.4
    # plt.xticks(index + bar_width / 2, stations, rotation='horizontal', fontsize=16)
    # plt.legend()
    #
    # # plt.tight_layout()
    # plt.gca().xaxis.tick_top()
    # plt.show()

    plt.show()


# ======================
def get_penetration_depths_from_edi_file(edifile, rholist=['det']):
    """Compute the penetration depths of an edi file
    :param edifile: input edifile
    :param rholist: flag the method to compute penetration depth: det zxy zyx
    :return: a tuple:(station_lat, statoin_lon, periods_list, pendepth_list)
    """
    logger.debug("processing the edi file %s", edifile)

    mt_obj = mt.MT(edifile)
    zeta = mt_obj.Z  # the attribute Z represent the impedance tensor 2X2 matrix
    freqs = zeta.freq  # frequencies

    scale_param = np.sqrt(1.0 / (2.0 * np.pi * 4 * np.pi * 10 ** (-7)))

    logger.debug("the scale parameter= %s", scale_param)

    # The periods array
    periods = 1.0 / freqs

    if 'zxy' in rholist:
        # One of the 4-components: XY
        penetration_depth = scale_param * np.sqrt(zeta.resistivity[:, 0, 1] * periods)

    if 'zyx' in rholist:
        penetration_depth = scale_param * np.sqrt(zeta.resistivity[:, 1, 0] * periods)

    if 'det' in rholist:
        # determinant
        det2 = np.abs(zeta.det[0])
        penetration_depth = scale_param * np.sqrt(0.2 * periods * det2 * periods)

    latlong_d=(mt_obj.lat, mt_obj.lon, periods, penetration_depth)
    return latlong_d


def create_csv_file(edi_dir, outputcsv=None, zcomponent='det'):
    """ Loop over all edi files, and create a csv file with columns:
    lat, lon, pendepth0, pendepth1, ...
    :param edi_dir: path_to_edifiles_dir
    :param zcomponent: det | zxy  | zyx
    :param outputcsv: path2output.csv file
    :return:
    """
    import csv

    edi_files = glob.glob(os.path.join(edi_dir, "*.edi"))

    logger.debug(edi_files)

    PER_LIST0=None   # the first period list as a reference for checking other stations period
    latlon_dep=[]  # CSV to be returned
    for afile in edi_files:
        # for efile in edi_files[:2]:
        logger.debug("processing %s", afile)
        lat,lon, per, depths=get_penetration_depths_from_edi_file(afile)
        if PER_LIST0 is None:
            PER_LIST0=per # initial value assignment
            depth_string = ','.join(['%.2f' % num for num in depths])
            latlon_dep.append((lat, lon, depth_string))

        elif len(per)== len(PER_LIST0) and (per == PER_LIST0).all():  # same length and same values.
            depth_string = ','.join(['%.2f' % num for num in depths])
            latlon_dep.append((lat,lon, depth_string))
        else:
            logger.error("MT Periods Not Equal !! %s VS %s", per, PER_LIST0 )
            #raise Exception ("MTPy Exception: Periods Not Equal")
            # pass this edi, let's continue


    #logger.debug(latlon_dep)

    if outputcsv is None:
        outputcsv= r"E:/tmp/MT_pen_depth.csv"

    logger.info("Saving to csv file: %s", outputcsv)
    with open(outputcsv, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(latlon_dep)

    return latlon_dep

def create_shapefile(edi_dir, outputfile=None, zcomponent='det'):
    """
    create a shapefile for station, penetration_depths
    :param edi_dir:
    :param outputfile:
    :param zcomponent:
    :return:
    """

    # TODO:

    return outputfile

# =============================================================================================
# Usage examples:
# python mtpy/imaging/penetration_depth_3d_profile.py /e/Datasets/MT_Datasets/3D_MT_data_edited_fromDuanJM/ 10
# python mtpy/imaging/penetration_depth_3d_profile.py  tests/data/edifiles/ 10
# python mtpy/imaging/penetration_depth_3d_profile.py examples/data/edi2/ 10
# =============================================================================================
if __name__=="__main__":

    if len(sys.argv)<2:
        print("Usage: %s edi_dir"%sys.argv[0])
        print ("python examples/penetration_depth_3d_profile.py tests/data/edifiles/ 10 ")
        sys.exit(1)
    elif os.path.isdir(sys.argv[1]):
        edi_dir = sys.argv[1]
        period_index= int(sys.argv[2])
        #plot_gridded_profile(edi_dir, period_index, zcomponent='det')   # 2D image
        plot_latlon_depth_profile(edi_dir, period_index)
        #plot_bar3d_depth(edi_dir, period_index)
        #create_csv_file(edi_dir, r"E:/tmp/my_mt_pendepth.csv")
    else:
        print("Please provide an edi directory and period_index_list")



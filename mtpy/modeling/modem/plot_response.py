"""
==================
ModEM
==================

# Generate files for ModEM

# revised by JP 2017
# revised by AK 2017 to bring across functionality from ak branch

"""

import os

import numpy as np
from matplotlib import pyplot as plt, gridspec as gridspec
from matplotlib.ticker import MultipleLocator

from mtpy.imaging import mtplottools as mtplottools
from mtpy.modeling.modem.data import Data

__all__ = ['PlotResponse']


class PlotResponse(object):
    """
    plot data and response

    Plots the real and imaginary impedance and induction vector if present.

    :Example: ::

        >>> import mtpy.modeling.new_modem as modem
        >>> dfn = r"/home/MT/ModEM/Inv1/DataFile.dat"
        >>> rfn = r"/home/MT/ModEM/Inv1/Test_resp_000.dat"
        >>> mrp = modem.PlotResponse(data_fn=dfn, resp_fn=rfn)
        >>> # plot only the TE and TM modes
        >>> mrp.plot_component = 2
        >>> mrp.redraw_plot()

    ======================== ==================================================
    Attributes               Description
    ======================== ==================================================
    color_mode               [ 'color' | 'bw' ] color or black and white plots
    cted                     color for data TE mode
    ctem                     color for data TM mode
    ctmd                     color for model TE mode
    ctmm                     color for model TM mode
    data_fn                  full path to data file
    data_object              WSResponse instance
    e_capsize                cap size of error bars in points (*default* is .5)
    e_capthick               cap thickness of error bars in points (*default*
                             is 1)
    fig_dpi                  resolution of figure in dots-per-inch (300)
    fig_list                 list of matplotlib.figure instances for plots
    fig_size                 size of figure in inches (*default* is [6, 6])
    font_size                size of font for tick labels, axes labels are
                             font_size+2 (*default* is 7)
    legend_border_axes_pad   padding between legend box and axes
    legend_border_pad        padding between border of legend and symbols
    legend_handle_text_pad   padding between text labels and symbols of legend
    legend_label_spacing     padding between labels
    legend_loc               location of legend
    legend_marker_scale      scale of symbols in legend
    lw                       line width response curves (*default* is .5)
    ms                       size of markers (*default* is 1.5)
    mted                     marker for data TE mode
    mtem                     marker for data TM mode
    mtmd                     marker for model TE mode
    mtmm                     marker for model TM mode
    phase_limits             limits of phase
    plot_component           [ 2 | 4 ] 2 for TE and TM or 4 for all components
    plot_style               [ 1 | 2 ] 1 to plot each mode in a seperate
                             subplot and 2 to plot xx, xy and yx, yy in same
                             plots
    plot_type                [ '1' | list of station name ] '1' to plot all
                             stations in data file or input a list of station
                             names to plot if station_fn is input, otherwise
                             input a list of integers associated with the
                             index with in the data file, ie 2 for 2nd station
    plot_z                   [ True | False ] *default* is True to plot
                             impedance, False for plotting resistivity and
                             phase
    plot_yn                  [ 'n' | 'y' ] to plot on instantiation
    res_limits               limits of resistivity in linear scale
    resp_fn                  full path to response file
    resp_object              WSResponse object for resp_fn, or list of
                             WSResponse objects if resp_fn is a list of
                             response files
    station_fn               full path to station file written by WSStation
    subplot_bottom           space between axes and bottom of figure
    subplot_hspace           space between subplots in vertical direction
    subplot_left             space between axes and left of figure
    subplot_right            space between axes and right of figure
    subplot_top              space between axes and top of figure
    subplot_wspace           space between subplots in horizontal direction
    ======================== ==================================================
    """

    def __init__(self, data_fn=None, resp_fn=None, **kwargs):
        self.data_fn = data_fn
        self.resp_fn = resp_fn

        self.data_object = None
        self.resp_object = []

        self.color_mode = kwargs.pop('color_mode', 'color')

        self.ms = kwargs.pop('ms', 1.5)
        self.ms_r = kwargs.pop('ms_r', 3)
        self.lw = kwargs.pop('lw', .5)
        self.lw_r = kwargs.pop('lw_r', 1.0)
        self.e_capthick = kwargs.pop('e_capthick', .5)
        self.e_capsize = kwargs.pop('e_capsize', 2)

        # color mode
        if self.color_mode == 'color':
            # color for data
            self.cted = kwargs.pop('cted', (0, 0, 1))
            self.ctmd = kwargs.pop('ctmd', (1, 0, 0))
            self.mted = kwargs.pop('mted', 's')
            self.mtmd = kwargs.pop('mtmd', 'o')

            # color for occam2d model
            self.ctem = kwargs.pop('ctem', (0, .6, .3))
            self.ctmm = kwargs.pop('ctmm', (.9, 0, .8))
            self.mtem = kwargs.pop('mtem', '+')
            self.mtmm = kwargs.pop('mtmm', '+')

        # black and white mode
        elif self.color_mode == 'bw':
            # color for data
            self.cted = kwargs.pop('cted', (0, 0, 0))
            self.ctmd = kwargs.pop('ctmd', (0, 0, 0))
            self.mted = kwargs.pop('mted', 's')
            self.mtmd = kwargs.pop('mtmd', 'o')

            # color for occam2d model
            self.ctem = kwargs.pop('ctem', (0.6, 0.6, 0.6))
            self.ctmm = kwargs.pop('ctmm', (0.6, 0.6, 0.6))
            self.mtem = kwargs.pop('mtem', '+')
            self.mtmm = kwargs.pop('mtmm', 'x')

        self.phase_limits_d = kwargs.pop('phase_limits_d', None)
        self.phase_limits_od = kwargs.pop('phase_limits_od', None)
        self.res_limits_d = kwargs.pop('res_limits_d', None)
        self.res_limits_od = kwargs.pop('res_limits_od', None)
        self.tipper_limits = kwargs.pop('tipper_limits', None)

        self.fig_num = kwargs.pop('fig_num', 1)
        self.fig_size = kwargs.pop('fig_size', [6, 6])
        self.fig_dpi = kwargs.pop('dpi', 300)

        self.subplot_wspace = kwargs.pop('subplot_wspace', .3)
        self.subplot_hspace = kwargs.pop('subplot_hspace', .0)
        self.subplot_right = kwargs.pop('subplot_right', .98)
        self.subplot_left = kwargs.pop('subplot_left', .08)
        self.subplot_top = kwargs.pop('subplot_top', .85)
        self.subplot_bottom = kwargs.pop('subplot_bottom', .1)

        self.legend_loc = 'upper center'
        self.legend_pos = (.5, 1.18)
        self.legend_marker_scale = 1
        self.legend_border_axes_pad = .01
        self.legend_label_spacing = 0.07
        self.legend_handle_text_pad = .2
        self.legend_border_pad = .15

        self.font_size = kwargs.pop('font_size', 6)

        self.plot_type = kwargs.pop('plot_type', '1')
        self.plot_style = kwargs.pop('plot_style', 1)
        self.plot_component = kwargs.pop('plot_component', 4)
        self.plot_yn = kwargs.pop('plot_yn', 'y')
        self.plot_z = kwargs.pop('plot_z', True)
        self.ylabel_pad = kwargs.pop('ylabel_pad', 1.25)

        self.fig_list = []

        # if self.plot_yn == 'y':
        #     self.plot()

    def plot(self):
        """
        plot
        """

        self.data_object = Data()
        self.data_object.read_data_file(self.data_fn)

        # get shape of impedance tensors
        ns = len(self.data_object.mt_dict.keys())

        # read in response files
        if self.resp_fn != None:
            self.resp_object = []
            if type(self.resp_fn) is not list:
                resp_obj = Data()
                resp_obj.read_data_file(self.resp_fn)
                self.resp_object = [resp_obj]
            else:
                for rfile in self.resp_fn:
                    resp_obj = Data()
                    resp_obj.read_data_file(rfile)
                    self.resp_object.append(resp_obj)

        # get number of response files
        nr = len(self.resp_object)

        if type(self.plot_type) is list:
            ns = len(self.plot_type)

        # --> set default font size
        plt.rcParams['font.size'] = self.font_size

        fontdict = {'size': self.font_size + 2, 'weight': 'bold'}
        if self.plot_z:
            h_ratio = [1, 1, .5]
        elif not self.plot_z:
            h_ratio = [1.5, 1, .5]

        ax_list = []
        line_list = []
        label_list = []

        # --> make key word dictionaries for plotting
        kw_xx = {'color': self.cted,
                 'marker': self.mted,
                 'ms': self.ms,
                 'ls': ':',
                 'lw': self.lw,
                 'e_capsize': self.e_capsize,
                 'e_capthick': self.e_capthick}

        kw_yy = {'color': self.ctmd,
                 'marker': self.mtmd,
                 'ms': self.ms,
                 'ls': ':',
                 'lw': self.lw,
                 'e_capsize': self.e_capsize,
                 'e_capthick': self.e_capthick}

        if self.plot_type != '1':
            pstation_list = []
            if type(self.plot_type) is not list:
                self.plot_type = [self.plot_type]
            for ii, station in enumerate(self.data_object.mt_dict.keys()):
                if type(station) is not int:
                    for pstation in self.plot_type:
                        if station.find(str(pstation)) >= 0:
                            pstation_list.append(station)
                else:
                    for pstation in self.plot_type:
                        if station == int(pstation):
                            pstation_list.append(ii)
        else:
            pstation_list = self.data_object.mt_dict.keys()

        for jj, station in enumerate(pstation_list):
            z_obj = self.data_object.mt_dict[station].Z
            t_obj = self.data_object.mt_dict[station].Tipper
            period = self.data_object.period_list
            print 'Plotting: {0}'.format(station)

            # convert to apparent resistivity and phase
            z_obj.compute_resistivity_phase()

            # find locations where points have been masked
            nzxx = np.nonzero(z_obj.z[:, 0, 0])[0]
            nzxy = np.nonzero(z_obj.z[:, 0, 1])[0]
            nzyx = np.nonzero(z_obj.z[:, 1, 0])[0]
            nzyy = np.nonzero(z_obj.z[:, 1, 1])[0]
            ntx = np.nonzero(t_obj.tipper[:, 0, 0])[0]
            nty = np.nonzero(t_obj.tipper[:, 0, 1])[0]

            # convert to apparent resistivity and phase
            if self.plot_z:
                scaling = np.zeros_like(z_obj.z)
                for ii in range(2):
                    for jj in range(2):
                        scaling[:, ii, jj] = 1. / np.sqrt(z_obj.freq)
                plot_res = abs(z_obj.z.real * scaling)
                plot_res_err = abs(z_obj.z_err * scaling)
                plot_phase = abs(z_obj.z.imag * scaling)
                plot_phase_err = abs(z_obj.z_err * scaling)
                h_ratio = [1, 1, .5]

            elif not self.plot_z:
                plot_res = z_obj.resistivity
                plot_res_err = z_obj.resistivity_err
                plot_phase = z_obj.phase
                plot_phase_err = z_obj.phase_err
                h_ratio = [1.5, 1, .5]

                try:
                    self.res_limits_d = (10 ** (np.floor(np.log10(min([plot_res[nzxx, 0, 0].min(),
                                                                       plot_res[nzyy, 1, 1].min()])))),
                                         10 ** (np.ceil(np.log10(max([plot_res[nzxx, 0, 0].max(),
                                                                      plot_res[nzyy, 1, 1].max()])))))
                except ValueError:
                    self.res_limits_d = None
                try:
                    self.res_limits_od = (10 ** (np.floor(np.log10(min([plot_res[nzxy, 0, 1].min(),
                                                                        plot_res[nzyx, 1, 0].min()])))),
                                          10 ** (np.ceil(np.log10(max([plot_res[nzxy, 0, 1].max(),
                                                                       plot_res[nzyx, 1, 0].max()])))))
                except ValueError:
                    self.res_limits_od = None

            # make figure
            fig = plt.figure(station, self.fig_size, dpi=self.fig_dpi)
            plt.clf()
            fig.suptitle(str(station), fontdict=fontdict)

            # set the grid of subplots
            if np.all(t_obj.tipper == 0.0) == True:
                self.plot_tipper = False
            else:
                self.plot_tipper = True
                self.tipper_limits = (np.round(min([t_obj.tipper[ntx, 0, 0].real.min(),
                                                    t_obj.tipper[nty, 0, 1].real.min(),
                                                    t_obj.tipper[ntx, 0, 0].imag.min(),
                                                    t_obj.tipper[nty, 0, 1].imag.min()]),
                                               1),
                                      np.round(max([t_obj.tipper[ntx, 0, 0].real.max(),
                                                    t_obj.tipper[nty, 0, 1].real.max(),
                                                    t_obj.tipper[ntx, 0, 0].imag.max(),
                                                    t_obj.tipper[nty, 0, 1].imag.max()]),
                                               1))

            gs = gridspec.GridSpec(3, 4,
                                   wspace=self.subplot_wspace,
                                   left=self.subplot_left,
                                   top=self.subplot_top,
                                   bottom=self.subplot_bottom,
                                   right=self.subplot_right,
                                   hspace=self.subplot_hspace,
                                   height_ratios=h_ratio)

            axrxx = fig.add_subplot(gs[0, 0])
            axrxy = fig.add_subplot(gs[0, 1], sharex=axrxx)
            axryx = fig.add_subplot(gs[0, 2], sharex=axrxx, sharey=axrxy)
            axryy = fig.add_subplot(gs[0, 3], sharex=axrxx, sharey=axrxx)

            axpxx = fig.add_subplot(gs[1, 0])
            axpxy = fig.add_subplot(gs[1, 1], sharex=axrxx)
            axpyx = fig.add_subplot(gs[1, 2], sharex=axrxx)
            axpyy = fig.add_subplot(gs[1, 3], sharex=axrxx)

            axtxr = fig.add_subplot(gs[2, 0], sharex=axrxx)
            axtxi = fig.add_subplot(gs[2, 1], sharex=axrxx, sharey=axtxr)
            axtyr = fig.add_subplot(gs[2, 2], sharex=axrxx)
            axtyi = fig.add_subplot(gs[2, 3], sharex=axrxx, sharey=axtyr)

            self.ax_list = [axrxx, axrxy, axryx, axryy,
                            axpxx, axpxy, axpyx, axpyy,
                            axtxr, axtxi, axtyr, axtyi]

            # ---------plot the apparent resistivity-----------------------------------
            # plot each component in its own subplot
            # plot data response
            erxx = mtplottools.plot_errorbar(axrxx,
                                             period[nzxx],
                                             plot_res[nzxx, 0, 0],
                                             plot_res_err[nzxx, 0, 0],
                                             **kw_xx)
            erxy = mtplottools.plot_errorbar(axrxy,
                                             period[nzxy],
                                             plot_res[nzxy, 0, 1],
                                             plot_res_err[nzxy, 0, 1],
                                             **kw_xx)
            eryx = mtplottools.plot_errorbar(axryx,
                                             period[nzyx],
                                             plot_res[nzyx, 1, 0],
                                             plot_res_err[nzyx, 1, 0],
                                             **kw_yy)
            eryy = mtplottools.plot_errorbar(axryy,
                                             period[nzyy],
                                             plot_res[nzyy, 1, 1],
                                             plot_res_err[nzyy, 1, 1],
                                             **kw_yy)
            # plot phase
            epxx = mtplottools.plot_errorbar(axpxx,
                                             period[nzxx],
                                             plot_phase[nzxx, 0, 0],
                                             plot_phase_err[nzxx, 0, 0],
                                             **kw_xx)
            epxy = mtplottools.plot_errorbar(axpxy,
                                             period[nzxy],
                                             plot_phase[nzxy, 0, 1],
                                             plot_phase_err[nzxy, 0, 1],
                                             **kw_xx)
            epyx = mtplottools.plot_errorbar(axpyx,
                                             period[nzyx],
                                             plot_phase[nzyx, 1, 0],
                                             plot_phase_err[nzyx, 1, 0],
                                             **kw_yy)
            epyy = mtplottools.plot_errorbar(axpyy,
                                             period[nzyy],
                                             plot_phase[nzyy, 1, 1],
                                             plot_phase_err[nzyy, 1, 1],
                                             **kw_yy)

            # plot tipper
            if self.plot_tipper:
                ertx = mtplottools.plot_errorbar(axtxr,
                                                 period[ntx],
                                                 t_obj.tipper[ntx, 0, 0].real,
                                                 t_obj.tipper_err[ntx, 0, 0],
                                                 **kw_xx)
                erty = mtplottools.plot_errorbar(axtyr,
                                                 period[nty],
                                                 t_obj.tipper[nty, 0, 1].real,
                                                 t_obj.tipper_err[nty, 0, 1],
                                                 **kw_yy)

                eptx = mtplottools.plot_errorbar(axtxi,
                                                 period[ntx],
                                                 t_obj.tipper[ntx, 0, 0].imag,
                                                 t_obj.tipper_err[ntx, 0, 0],
                                                 **kw_xx)
                epty = mtplottools.plot_errorbar(axtyi,
                                                 period[nty],
                                                 t_obj.tipper[nty, 0, 1].imag,
                                                 t_obj.tipper_err[nty, 0, 1],
                                                 **kw_yy)

            # ----------------------------------------------
            # get error bar list for editing later
            if not self.plot_tipper:
                try:
                    self._err_list = [[erxx[1][0], erxx[1][1], erxx[2][0]],
                                      [erxy[1][0], erxy[1][1], erxy[2][0]],
                                      [eryx[1][0], eryx[1][1], eryx[2][0]],
                                      [eryy[1][0], eryy[1][1], eryy[2][0]]]
                    line_list = [[erxx[0]], [erxy[0]], [eryx[0]], [eryy[0]]]
                except IndexError:
                    print 'Found no Z components for {0}'.format(self.station)
                    line_list = [[None], [None],
                                 [None], [None]]

                    self._err_list = [[None, None, None],
                                      [None, None, None],
                                      [None, None, None],
                                      [None, None, None]]

            else:
                try:
                    line_list = [[erxx[0]], [erxy[0]],
                                 [eryx[0]], [eryy[0]],
                                 [ertx[0]], [erty[0]]]

                    self._err_list = [[erxx[1][0], erxx[1][1], erxx[2][0]],
                                      [erxy[1][0], erxy[1][1], erxy[2][0]],
                                      [eryx[1][0], eryx[1][1], eryx[2][0]],
                                      [eryy[1][0], eryy[1][1], eryy[2][0]],
                                      [ertx[1][0], ertx[1][1], ertx[2][0]],
                                      [erty[1][0], erty[1][1], erty[2][0]]]
                except IndexError:
                    print 'Found no Z components for {0}'.format(station)
                    line_list = [[None], [None],
                                 [None], [None],
                                 [None], [None]]

                    self._err_list = [[None, None, None],
                                      [None, None, None],
                                      [None, None, None],
                                      [None, None, None],
                                      [None, None, None],
                                      [None, None, None]]
            # ------------------------------------------
            # make things look nice
            # set titles of the Z components
            label_list = [['$Z_{xx}$'], ['$Z_{xy}$'],
                          ['$Z_{yx}$'], ['$Z_{yy}$']]
            for ax, label in zip(self.ax_list[0:4], label_list):
                ax.set_title(label[0], fontdict={'size': self.font_size + 2,
                                                 'weight': 'bold'})

                # set legends for tipper components
            # fake a line
            l1 = plt.Line2D([0], [0], linewidth=0, color='w', linestyle='None',
                            marker='.')
            t_label_list = ['Re{$T_x$}', 'Im{$T_x$}', 'Re{$T_y$}', 'Im{$T_y$}']
            label_list += [['$T_{x}$'], ['$T_{y}$']]
            for ax, label in zip(self.ax_list[-4:], t_label_list):
                ax.legend([l1], [label], loc='upper left',
                          markerscale=.01,
                          borderaxespad=.05,
                          labelspacing=.01,
                          handletextpad=.05,
                          borderpad=.05,
                          prop={'size': max([self.font_size, 6])})



                # set axis properties
            for aa, ax in enumerate(self.ax_list):
                ax.tick_params(axis='y', pad=self.ylabel_pad)

                if aa < 8:
                    #                    ylabels[-1] = ''
                    #                    ylabels[0] = ''
                    #                    ax.set_yticklabels(ylabels)
                    #                    plt.setp(ax.get_xticklabels(), visible=False)
                    if self.plot_z == True:
                        ax.set_yscale('log', nonposy='clip')

                else:
                    ax.set_xlabel('Period (s)', fontdict=fontdict)

                if aa < 4 and self.plot_z is False:
                    ax.set_yscale('log', nonposy='clip')
                    if aa == 0 or aa == 3:
                        ax.set_ylim(self.res_limits_d)
                    elif aa == 1 or aa == 2:
                        ax.set_ylim(self.res_limits_od)

                if aa > 3 and aa < 8 and self.plot_z is False:
                    ax.yaxis.set_major_formatter(MultipleLocator(10))
                    if self.phase_limits_d is not None:
                        ax.set_ylim(self.phase_limits_d)
                # set axes labels
                if aa == 0:
                    if self.plot_z == False:
                        ax.set_ylabel('App. Res. ($\mathbf{\Omega \cdot m}$)',
                                      fontdict=fontdict)
                    elif self.plot_z == True:
                        ax.set_ylabel('Re[Z (mV/km nT)]',
                                      fontdict=fontdict)
                elif aa == 4:
                    if self.plot_z == False:
                        ax.set_ylabel('Phase (deg)',
                                      fontdict=fontdict)
                    elif self.plot_z == True:
                        ax.set_ylabel('Im[Z (mV/km nT)]',
                                      fontdict=fontdict)
                elif aa == 8:
                    ax.set_ylabel('Tipper',
                                  fontdict=fontdict)

                if aa > 7:
                    ax.yaxis.set_major_locator(MultipleLocator(.1))
                    if self.tipper_limits is not None:
                        ax.set_ylim(self.tipper_limits)
                    else:
                        pass

                ax.set_xscale('log', nonposx='clip')
                ax.set_xlim(xmin=10 ** (np.floor(np.log10(period[0]))) * 1.01,
                            xmax=10 ** (np.ceil(np.log10(period[-1]))) * .99)
                ax.grid(True, alpha=.25)

                ylabels = ax.get_yticks().tolist()
                if aa < 8:
                    ylabels[-1] = ''
                    ylabels[0] = ''
                    ax.set_yticklabels(ylabels)
                    plt.setp(ax.get_xticklabels(), visible=False)


                    ##----------------------------------------------
            # plot model response
            if self.resp_object is not None:
                for resp_obj in self.resp_object:
                    resp_z_obj = resp_obj.mt_dict[station].Z
                    resp_z_err = np.nan_to_num((z_obj.z - resp_z_obj.z) / z_obj.z_err)
                    resp_z_obj.compute_resistivity_phase()

                    resp_t_obj = resp_obj.mt_dict[station].Tipper
                    resp_t_err = np.nan_to_num((t_obj.tipper - resp_t_obj.tipper) / t_obj.tipper_err)

                    # convert to apparent resistivity and phase
                    if self.plot_z == True:
                        scaling = np.zeros_like(resp_z_obj.z)
                        for ii in range(2):
                            for jj in range(2):
                                scaling[:, ii, jj] = 1. / np.sqrt(resp_z_obj.freq)
                        r_plot_res = abs(resp_z_obj.z.real * scaling)
                        r_plot_phase = abs(resp_z_obj.z.imag * scaling)

                    elif self.plot_z == False:
                        r_plot_res = resp_z_obj.resistivity
                        r_plot_phase = resp_z_obj.phase

                    rms_xx = resp_z_err[:, 0, 0].std()
                    rms_xy = resp_z_err[:, 0, 1].std()
                    rms_yx = resp_z_err[:, 1, 0].std()
                    rms_yy = resp_z_err[:, 1, 1].std()

                    # --> make key word dictionaries for plotting
                    kw_xx = {'color': self.ctem,
                             'marker': self.mtem,
                             'ms': self.ms_r,
                             'ls': ':',
                             'lw': self.lw_r,
                             'e_capsize': self.e_capsize,
                             'e_capthick': self.e_capthick}

                    kw_yy = {'color': self.ctmm,
                             'marker': self.mtmm,
                             'ms': self.ms_r,
                             'ls': ':',
                             'lw': self.lw_r,
                             'e_capsize': self.e_capsize,
                             'e_capthick': self.e_capthick}

                    # plot data response
                    rerxx = mtplottools.plot_errorbar(axrxx,
                                                      period[nzxx],
                                                      r_plot_res[nzxx, 0, 0],
                                                      None,
                                                      **kw_xx)
                    rerxy = mtplottools.plot_errorbar(axrxy,
                                                      period[nzxy],
                                                      r_plot_res[nzxy, 0, 1],
                                                      None,
                                                      **kw_xx)
                    reryx = mtplottools.plot_errorbar(axryx,
                                                      period[nzyx],
                                                      r_plot_res[nzyx, 1, 0],
                                                      None,
                                                      **kw_yy)
                    reryy = mtplottools.plot_errorbar(axryy,
                                                      period[nzyy],
                                                      r_plot_res[nzyy, 1, 1],
                                                      None,
                                                      **kw_yy)
                    # plot phase
                    repxx = mtplottools.plot_errorbar(axpxx,
                                                      period[nzxx],
                                                      r_plot_phase[nzxx, 0, 0],
                                                      None,
                                                      **kw_xx)
                    repxy = mtplottools.plot_errorbar(axpxy,
                                                      period[nzxy],
                                                      r_plot_phase[nzxy, 0, 1],
                                                      None,
                                                      **kw_xx)
                    repyx = mtplottools.plot_errorbar(axpyx,
                                                      period[nzyx],
                                                      r_plot_phase[nzyx, 1, 0],
                                                      None,
                                                      **kw_yy)
                    repyy = mtplottools.plot_errorbar(axpyy,
                                                      period[nzyy],
                                                      r_plot_phase[nzyy, 1, 1],
                                                      None,
                                                      **kw_yy)

                    # plot tipper
                    if self.plot_tipper == True:
                        rertx = mtplottools.plot_errorbar(axtxr,
                                                          period[ntx],
                                                          resp_t_obj.tipper[ntx, 0, 0].real,
                                                          None,
                                                          **kw_xx)
                        rerty = mtplottools.plot_errorbar(axtyr,
                                                          period[nty],
                                                          resp_t_obj.tipper[nty, 0, 1].real,
                                                          None,
                                                          **kw_yy)

                        reptx = mtplottools.plot_errorbar(axtxi,
                                                          period[ntx],
                                                          resp_t_obj.tipper[ntx, 0, 0].imag,
                                                          None,
                                                          **kw_xx)
                        repty = mtplottools.plot_errorbar(axtyi,
                                                          period[nty],
                                                          resp_t_obj.tipper[nty, 0, 1].imag,
                                                          None,
                                                          **kw_yy)

                    if self.plot_tipper == False:
                        line_list[0] += [rerxx[0]]
                        line_list[1] += [rerxy[0]]
                        line_list[2] += [reryx[0]]
                        line_list[3] += [reryy[0]]
                        label_list[0] += ['$Z^m_{xx}$ ' +
                                          'rms={0:.2f}'.format(rms_xx)]
                        label_list[1] += ['$Z^m_{xy}$ ' +
                                          'rms={0:.2f}'.format(rms_xy)]
                        label_list[2] += ['$Z^m_{yx}$ ' +
                                          'rms={0:.2f}'.format(rms_yx)]
                        label_list[3] += ['$Z^m_{yy}$ ' +
                                          'rms={0:.2f}'.format(rms_yy)]
                    else:
                        line_list[0] += [rerxx[0]]
                        line_list[1] += [rerxy[0]]
                        line_list[2] += [reryx[0]]
                        line_list[3] += [reryy[0]]
                        line_list[4] += [rertx[0]]
                        line_list[5] += [rerty[0]]
                        label_list[0] += ['$Z^m_{xx}$ ' +
                                          'rms={0:.2f}'.format(rms_xx)]
                        label_list[1] += ['$Z^m_{xy}$ ' +
                                          'rms={0:.2f}'.format(rms_xy)]
                        label_list[2] += ['$Z^m_{yx}$ ' +
                                          'rms={0:.2f}'.format(rms_yx)]
                        label_list[3] += ['$Z^m_{yy}$ ' +
                                          'rms={0:.2f}'.format(rms_yy)]
                        label_list[4] += ['$T^m_{x}$ ' +
                                          'rms={0:.2f}'.format(resp_t_err[:, 0, 0].std())]
                        label_list[5] += ['$T^m_{y}$' +
                                          'rms={0:.2f}'.format(resp_t_err[:, 0, 1].std())]

                legend_ax_list = self.ax_list[0:4]
                #                if self.plot_tipper == True:
                #                    legend_ax_list += [self.ax_list[-4], self.ax_list[-2]]

                for aa, ax in enumerate(legend_ax_list):
                    ax.legend(line_list[aa],
                              label_list[aa],
                              loc=self.legend_loc,
                              bbox_to_anchor=self.legend_pos,
                              markerscale=self.legend_marker_scale,
                              borderaxespad=self.legend_border_axes_pad,
                              labelspacing=self.legend_label_spacing,
                              handletextpad=self.legend_handle_text_pad,
                              borderpad=self.legend_border_pad,
                              prop={'size': max([self.font_size, 5])})

            plt.show()

    def redraw_plot(self):
        """
        redraw plot if parameters were changed

        use this function if you updated some attributes and want to re-plot.

        :Example: ::

            >>> # change the color and marker of the xy components
            >>> import mtpy.modeling.occam2d as occam2d
            >>> ocd = occam2d.Occam2DData(r"/home/occam2d/Data.dat")
            >>> p1 = ocd.plotAllResponses()
            >>> #change line width
            >>> p1.lw = 2
            >>> p1.redraw_plot()
        """
        for fig in self.fig_list:
            plt.close(fig)
        self.plot()

    def save_figure(self, save_fn, file_format='pdf', orientation='portrait',
                    fig_dpi=None, close_fig='y'):
        """
        save_plot will save the figure to save_fn.

        Arguments:
        -----------

            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as
                            save_fn/station_name_PhaseTensor.file_format

                          * full path -> file will be save to the given
                            path.  If you use this option then the format
                            will be assumed to be provided by the path

            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps...

            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait

            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the dpi will be that at
                          which the figure was made.  I don't think that
                          it can be larger than dpi of the figure.

            **close_plot** : [ y | n ]
                             * 'y' will close the plot after saving.
                             * 'n' will leave plot open

        :Example: ::

            >>> # to save plot as jpg
            >>> import mtpy.modeling.occam2d as occam2d
            >>> dfn = r"/home/occam2d/Inv1/data.dat"
            >>> ocd = occam2d.Occam2DData(dfn)
            >>> ps1 = ocd.plotPseudoSection()
            >>> ps1.save_plot(r'/home/MT/figures', file_format='jpg')

        """

        fig = plt.gcf()
        if fig_dpi == None:
            fig_dpi = self.fig_dpi

        if os.path.isdir(save_fn) == False:
            file_format = save_fn[-3:]
            fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation, bbox_inches='tight')

        else:
            save_fn = os.path.join(save_fn, '_L2.' +
                                   file_format)
            fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation, bbox_inches='tight')

        if close_fig == 'y':
            plt.clf()
            plt.close(fig)

        else:
            pass

        self.fig_fn = save_fn
        print 'Saved figure to: ' + self.fig_fn

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.

        Use this if you change an of the .fig or axes properties

        :Example: ::

            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.modeling.occam2d as occam2d
            >>> dfn = r"/home/occam2d/Inv1/data.dat"
            >>> ocd = occam2d.Occam2DData(dfn)
            >>> ps1 = ocd.plotAllResponses()
            >>> [ax.grid(True, which='major') for ax in [ps1.axrte,ps1.axtep]]
            >>> ps1.update_plot()

        """

        self.fig.canvas.draw()

    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """

        return ("Plots data vs model response computed by WS3DINV")

# ==================================================================================
# FZ: add example usage code
# Justdo>  python mtpy/modeling/modem/plot_response.py
# ==================================================================================
if __name__ == "__main__":

    from mtpy.mtpy_globals import *

    # directory where files are located
#    wd = os.path.join(SAMPLE_DIR, 'ModEM')
    wd = os.path.join(SAMPLE_DIR, 'ModEM_2')

    # file stem for inversion result
    filestem = 'Modular_MPI_NLCG_004'

    datafn = 'ModEM_Data.dat'

#    station = 'pb23'
    station = 'Synth02'
    plot_z = False

    ro = PlotResponse(data_fn=os.path.join(wd, datafn),
                      resp_fn=os.path.join(wd, filestem + '.dat'),
                      plot_type=[station],
		              plot_style=2,
                      plot_z=plot_z)

    ro.plot()

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 15:35:39 2013

@author: Alison Kirkby

plots edi files (res/phase vs period) for all edis in a directory and saves out as png files
"""

import os

from tests import _plt_wait
from tests.beta import *
import mtpy.imaging.plotresponse as mtpr
from tests.imaging import ImageTestCase


class Test_PlotResponse(ImageTestCase):
    def test_func(self):
        # path to edis
        epath = EDI_DATA_DIR

        elst = [os.path.join(epath, edi) for edi in os.listdir(epath) if (edi.endswith('.edi'))]

        for efile in elst[:3]:
            # eo = mtedi.Edi(efile)
            pr = mtpr.PlotResponse(fn=efile,
                                   plot_num=2,
                                   plot_tipper='yri',
                                   plot_pt='y')

            _plt_wait(1)

            figfile = os.path.join(self._temp_dir, os.path.basename(efile)[:-4] + '.png')
            pr.save_plot(figfile)

            assert (os.path.exists(figfile))

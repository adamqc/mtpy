MTpy: A Python Toolbox for Magnetotelluric (MT) Data Processing, Analysis, Modelling and Visualization
==================================

|Build Status| |Coverage Status|


Overview
========

A Python Toolbox for Magnetotelluric (MT) Data Processing, Analysis, Modelling and Visualization

This repository has superseded the `geophysics/mtpy <https://github.com/geophysics/mtpy/tree/beta>`_
and `GeoscienceAustralia/mtpy2 <https://github.com/GeoscienceAustralia/mtpy2/tree/develop>`_

Home Page: https://github.com/MTgeophysics/mtpy

Documentation: http://MTgeophysics.github.io/mtpy

Issue tracking: https://github.com/MTgeophysics/mtpy/issues


Contacts
==========

| **Alison Kirkby**
| Alison.Kirkby@ga.gov.au

| **Fei Zhang**
| fei.zhang@ga.gov.au

| **Jared Peacock**
| peacock.jared@gmail.com

| **Yingzhi Gou**
| Yingzhi.Gou@ga.gov.au

| **Rakib Hassan**
| Rakib.Hassan@ga.gov.au

| **Jinming Duan**
| Jingming.Duan@ga.gov.au



System Requirements (Draft)
==========================


-  Software
-  Python 2.7+ or Python 3.5+

Setup Guide for Developers (Draft)
==========================

1. Obtain the source code from https://github.com/MTgeophysics/mtpy:

   -  ``git clone https://github.com/MTgeophysics/mtpy.git``

2. Install Python dependencies. And
   
    ``cd mtpy``
   
    ``pip install -v --user -e .`` (user's own home ~/.local/lib/python2.7/site-packages/mtpy.egg-link)
   
   OR ``pip install -v -e .``  (into python lib's dir site-packages, write-permission required)
   
   OR `` export  PYTHONPATH=/your_path2/mtpy2:$PYTHONPATH `` (each session)
   
   OR ``python setup.py develop --user``
   
   To verify the install : ``pip list | grep mtpy``

   To uninstall the package: ``pip uninstall -v mtpy``

3. Run unit tests + PyLint

   ``./check-code.sh``

   (this script is run by Travis. You can alternatively run ``py.test`` at commandline)
   
  4. Run further functional tests 

   See examples: ``tests/testcases.sh``






License
===============

MTpy is licensed under the GPL version 3

The license agreement is contained in the repository and should be kept together with the code.



Conventions
===============

1. MTpy uses E- and B-fields (although the sensors may be confusingly named as H-sensors in EDI files)
2. [E] = microvolts/meter (muV/m)
3. [B] = nanotesla (nT)
4. [Z] = [E]/[B] = km/s
5. Apparent resistivty rho = 0.2 * T * |Z|^2  (in Ohm m)
6. Angles are given in degrees (mod 360)
7. EDI files can contain data in Z- or rho/phi-form
8. EDI files contain data from one station only
9. Coordinates are handled in decimal degrees (converted when reading)
10. Time stamps refer to UTC
11. Internal coordinates: X = North-South, Y = East-West
12. Rotations are interpreted clockwise (mathematically negative)
13. 0 degrees azimuth = North



.. |Build Status| image:: https://travis-ci.org/MTgeophysics/mtpy.svg?branch=develop
   :target: https://travis-ci.org/MTgeophysics/mtpy
.. |Coverage Status| image:: https://coveralls.io/repos/github/MTgeophysics/mtpy/badge.svg?branch=develop
   :target: https://coveralls.io/github/MTgeophysics/mtpy?branch=develop

.. |Documentation Status| image:: https://readthedocs.org/projects/mtpy2/badge/?version=develop
   :target: https://mtgeophysics.github.io/mtpy/


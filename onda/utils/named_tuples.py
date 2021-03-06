# This file is part of OnDA.
#
# OnDA is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# OnDA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with OnDA.
# If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2019 Deutsches Elektronen-Synchrotron DESY,
# a research centre of the Helmholtz Association.
"""
OnDA named tuples.

This module contains a collection of named tuples used throughout the OnDA framework.
"""
from __future__ import absolute_import, division, print_function

import collections


PeakList = collections.namedtuple("PeakList", ["fs", "ss", "intensity"])
"""
Information about Bragg peaks found in a detector data frame (list of peaks).

Arguments:

    fs (List[float]): a list of fractional fs indexes locating the detected peaks
        in the detector data frame.

    ss (List[float]): a list of fractional ss indexes locating the detected peaks
        in the detector data frame.

    intensity (List[float]): a list of integrated intensities for the detected
        peaks.
"""


Peakfinder8Info = collections.namedtuple(
    "Peakfinder8Info", ["asic_nx", "asic_ny", "nasics_x", "nasics_y"]
)
"""
Peakfinder8 information for a detector.

Arguments:

    asic_nx (int): the fs size in pixels of each detector's ASIC in the detector data
        frame.

    asic_ny (int): the ss size in pixels of each detector's ASIC in the detector data
        frame.

    nasics_x (int): the number of ASICs along the fs axis of the detector data frame.

    nasics_y (int): the number of ASICs along the ss axis of the detector data frame.
"""


HidraInfo = collections.namedtuple("HidraInfo", ["query", "targets", "data_base_path"])
"""
HiDRA initialization information.

TODO: Determine field types.

Arguments:

    query(?): an object storing information about the transfer type.

    targets (?): a list of objects storing information about the worker nodes that will
        receive data from HiDRA.

    data_base_path (str): the absolute or relative base path to be used for locating
        files in the filesystem when HiDRA only provides relative path information.
"""


DataAndCalibrationInfo = collections.namedtuple(
    "DataAndCalibrationInfo", ["data", "info"]
)
"""
Detector frame data and additional information needed for the calibration.

Arguments:

    data (numpy.ndarray): the data frame to calibrate.

    info (Dict[str, Any]): a dictionary storing additional information needed for the
        calibration. The exact content of this dictionary depends on the calibration
        algorithm being used (see the documentation of the relevant algorithm).
"""


ProcessedData = collections.namedtuple("ProcessedData", ["data", "worker_rank"])
"""
Processed data transferred from a worker node to the master node.

Arguments:

    data (Dict[str, Any]): a dictionary storing the transferred data.

    node_rank (int): the rank, in the OnDA pool, of the worker node from which the data
        is transferred.
"""

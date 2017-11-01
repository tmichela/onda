#    This file is part of OnDA.
#
#    OnDA is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OnDA is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OnDA.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import namedtuple
from time import strptime

import h5py


SlabShape = namedtuple('SlabShape', ['ss', 'fs'])
NativeShape = namedtuple('NativeShape', ['ss', 'fs'])

slab_shape = SlabShape(1480, 1552)
native_shape = NativeShape(1480, 1552)

file_extensions = ['.h5']


def open_file(filename):
    return h5py.File(filename, 'r')


def close_file(filehandle):
    filehandle.close()


def num_events_in_file(_):
    return 1


def timestamp(event):
    return strptime(event['filehandle']['/LCLS/eventTimeString'][()].decode('ascii').strip(), '%a %b  %d %H:%M:%S %Y')


def raw_data(event):
    return event.filehandle['/data/data'][()]


def detector_distance(evt):
    return float(evt.filehandle['/LCLS/detector0-EncoderValue'][()])


def beam_energy(evt):
    return float(evt.filehandle['/LCLS/photon_energy_eV'][()])


def filename_and_event(evt):
    return (evt.filehandle, 0)

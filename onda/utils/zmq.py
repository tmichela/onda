#    This file is part of cfelpyutils.
#
#    cfelpyutils is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    cfelpyutils is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with cfelpyutils.  If not, see <http://www.gnu.org/licenses/>.
"""
ZMQ-based communication in OnDA.

This module contains the implementation of several ZMQ-based data
broadcasting and receiving classes.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import socket
import sys

import zmq

try:
    from cPickle import loads
except ImportError:
    from pickle import loads

try:
    from PyQt5 import QtCore
except ImportError:
    from PyQt4 import QtCore


class DataBroadcaster(object):
    """
    Data-broadcasting socket for OnDA monitors.

    A ZMQ socket used to broacast data. The socket supports multiple
    clients (it is based on the ZMQ PUB socket type). It also has no
    queuing system: messages that are not received are dropped.
    """

    def __init__(self, publish_ip=None, publish_port=None):
        """
        Initialize the ZMQOndaPublisherSocket class.

        Args:

            publish_ip (Optional[str]): hostname or IP address of the
                machine where the socket will be opened. If None, the
                hostname will be autodetected. Defaults to None.

            publish_port(Optional[int]): port where the socket will be
                opened. If None, the port number will be set to 12321.
                Defaults to None.
        """
        self._context = zmq.Context()
        self._sock = self._context.socket(zmq.PUB)  # pylint: disable=E1101

        if publish_ip is not None:
            pip = publish_ip
        else:

            # If required, use the socket module to autodetect the
            # hostname of the machine where the OnDA monitor is
            # running.
            pip = [
                (
                    s.connect(('8.8.8.8', 80)),
                    s.getsockname()[0],
                    s.close()
                ) for s in [
                    socket.socket(
                        family=socket.AF_INET,
                        type=socket.SOCK_DGRAM)
                ]
            ][0][1]

        if publish_port is not None:
            pport = publish_port
        else:
            pport = 12321

        print('Binding to tcp://{0}:{1}'.format(pip, pport))
        sys.stdout.flush()

        # Set a high water mark of 1 (A messaging queue 1 message
        # long, so no queuing).
        self._sock.set_hwm(1)
        self._sock.bind('tcp://%s:%d' % (pip, pport))

    def send_data(self, tag, message):
        """
        Broadcast data.

        Send data (a python object) through the broadcasting socket.

        Args:

            tag (str): tag for the data to be sent.

            message (Any): a python object to be sent.
        """
        # Send the tag and the data in one single ZMQ message.
        self._sock.send(tag.encode(), zmq.SNDMORE)
        self._sock.send_pyobj(message)


class DataListener(QtCore.QObject):
    """
    Listening socket for OnDA clients.

    A listening class to be used for OnDA clients, based on a ZMQ
    SUB socket. Suitable to be used in a separate listening thread.
    Check continuously if data is coming to the socket. Emit a custom
    Qt signal every time data is received through the socket. Send the
    data together with the signal.
    """

    zmqmessage = QtCore.pyqtSignal(dict)
    # Custom Qt signal to be emitted when data is received.

    def __init__(self,
                 pub_hostname,
                 pub_port,
                 subscription_string):
        """
        Initialize the DataListener class.

        Args:

            pub_hostname (str): hostname or IP address of the machine
                where the OnDA monitor is running.

            pub_port (int): port on which the the OnDA monitor is
                broadcasting information.

            subscribe string (str): data tag to which the listener
                should subscribe.
        """
        QtCore.QObject.__init__(self)

        # These following information is needed to disconnect/reconnect
        # the socket without destroying and reinstantiating the
        # listener.
        self._pub_hostname = pub_hostname
        self._pub_port = pub_port
        self._subscription_string = subscription_string
        self._zmq_context = zmq.Context()
        self._zmq_subscribe = None
        self._zmq_poller = None

        # Initialize the listening timer. Every time this timer ticks,
        # try to read from the socket.
        self._listening_timer = QtCore.QTimer()
        self._listening_timer.timeout.connect(self.listen)

    def start_listening(self):
        """
        Start listening.

        Connect to the boradcasting socket and start listening.
        """
        print(
            "Connecting to tcp://{}:{}".format(
                self._pub_hostname,
                self._pub_port
            )
        )
        self._zmq_subscribe = (
            self._zmq_context.socket(zmq.SUB)  # pylint: disable=E1101
        )
        self._zmq_subscribe.connect(
            'tcp://{0}:{1}'.format(
                self._pub_hostname,
                self._pub_port
            )
        )
        self._zmq_subscribe.setsockopt_string(
            option=zmq.SUBSCRIBE,  # pylint: disable=E1101
            optval=self._subscription_string
        )

        # Set a high water mark of 1 (A messaging queue 1 message
        # long, so no queuing).
        self._zmq_subscribe.set_hwm(1)
        self._zmq_poller = zmq.Poller()
        self._zmq_poller.register(
            socket=self._zmq_subscribe,
            flags=zmq.POLLIN
        )

        self._listening_timer.start()

    def stop_listening(self):
        """
        Stop listening.

        Stop the listening and disconnect from the broadcasting socket.
        """
        self._listening_timer.stop()
        print(
            "Disconnecting from tcp://{}:{}".format(
                self._pub_hostname,
                self._pub_port
            )
        )

        self._zmq_subscribe.disconnect(
            "tcp://{}:{}".format(
                self._pub_hostname,
                self._pub_port
            )
        )

        self._zmq_poller = None
        self._zmq_subscribe = None

    def listen(self):
        """
        Listen.

        Listen for data. When data comes, emit a signal adding the data
        as payload.
        """
        socks = dict(self._zmq_poller.poll(0))
        if (
                self._zmq_subscribe in socks and
                socks[self._zmq_subscribe] == zmq.POLLIN
        ):
            full_msg = self._zmq_subscribe.recv_multipart()
            msg = full_msg[1]

            # Unpickle the message (a dictionary) and emit the signal.
            zmq_dict = loads(msg)
            self.zmqmessage.emit(zmq_dict)
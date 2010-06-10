################################################################################
##
##  Copyright 2010 Philipp Meier <pmeier82@googlemail.com>
##
##  Licensed under the EUPL, Version 1.1 or – as soon they will be approved by
##  the European Commission - subsequent versions of the EUPL (the "Licence");
##  You may not use this work except in compliance with the Licence.
##  You may obtain a copy of the Licence at:
##
##  http://ec.europa.eu/idabc/eupl
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the Licence is distributed on an "AS IS" basis,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the Licence for the specific language governing permissions and
##  limitations under the Licence.
##
################################################################################
# -*- coding: utf-8 -*-
#
# sim - sim_objects/sim_object.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""simulation object - base class

SimObject are the (virtual) base class for all components in the simulation
scene. They share implement all behavior and statistics common to all objects,
like distinct position, orientation and slots to receive tick notifications.
Subclasses should implement the self._on_<event name> private methods
"""
__doctype__ = 'restructuredtext'


##---IMPORTS

# packages
import scipy as N
# own packages
from math3d import (
    quaternion_about_axis,
    unit_vector,
    random_quaternion,
    quaternion_matrix
)


##---CLASSES

class SimObject(object):
    """simulation object base class"""

    ## constructor

    def __init__(self, **kwargs):
        """
        :Keywords:
            name : str
                An identifier for the SimObject. This should be castable to str.
            orientation : ndarray or bool
                Orientation of the object. ndarray is interpreted as direction
                of orientation relative to the scene's positive z-axis. If True
                a random rotation is created. If False, no orientation.
                Default=False
            points : arraylike
                Coordinates forming this object, expressed in the local
                coordinate system. None if no points, [0,0,0] represents
                self.position in the local coordinate system.
                Default=None
            position : array like
                Position in scene (x,y,z).
                Default=[0,0,0]
            sample_rate : float
                The sample rate in Hertz.
                Default=16000.0
        """

        # members
        self._name = None
        self._points = None
        self._position = None
        self._orientation = None
        self._sample_rate = None
        self.active = True

        # set from kwargs
        self.name = kwargs.get('name', str(id(self)))
        self.points = kwargs.get('points', None)
        self.position = kwargs.get('position', [0, 0, 0])
        self.orientation = kwargs.get('orientation', False)
        self.sample_rate = kwargs.get('sample_rate', 16000.0)

    ## properties

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = N.asarray(value)

    @property
    def orientation(self):
        return self._orientation
    @orientation.setter
    def orientation(self, value):
        if isinstance(value, (list, N.ndarray)):
            value = N.asarray(value)
            # find quaternion for rotation
            n = N.cross([0,0,1], unit_vector(value[:3]))
            phi = N.arccos(N.dot([0,0,1], unit_vector(value[:3])))
            self._orientation = quaternion_about_axis(phi, n)
        elif value is True:
            # random orientation
            self._orientation = random_quaternion()
        else:
            # other stuff goes no orientation
            self._orientation = False

    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = float(value)
        if self._sample_rate <= 0.0:
            self._sample_rate = 1.0

    @property
    def points(self):
        # if we have no points, return self.position
        if self._points is None:
            rval = N.zeros((1,3,))
        else:
            rval = self._points.copy()
        if self.orientation is not False:
            rval = N.dot(quaternion_matrix(self.orientation)[:3,:3], rval.T).T
        rval += self.position
        return N.asarray(rval)
    @points.setter
    def points(self, value):
        self._points = value

    ## special methods

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.name)


##---MAIN

if __name__ == '__main__':
    pass

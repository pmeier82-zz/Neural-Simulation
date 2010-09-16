#﻿# -*- coding: utf-8 -*-
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
#
# nsim - scene/neuron_data/neuron_data.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-13
#

"""interface for neuron data objects as used with the 'Neural Simulation'"""
__docformat__ = 'restructuredtext'


##---IMPORTS

import scipy as N
from tables import openFile
from nsim.math import vector_norm

# import all known NeuronData subclasses



##---CLASSES

class NeuronData(object):
    """dataset factory for a neuron in the Neural Simulation
    
    An interface is defined to represent the spatiotemporal voltage data
    generated by a neuron during the course of an action potential. The voltage
    data is provided as the temporal waveform of the neuron at all points within
    a spherical volume around the neuron, defined by the radius of that volume
    (called the horizon).
    
    The NeuronData object provides means to query data samples or data-strips
    within the spherical volume defined by the horizon. The interface only
    defines the way of data acquisition from the neuron_data subclass. How that
    data is generated  is up to the concrete implementation.
    
    All interface members are read only, the only public method is 'get_data' to
    retrieve a part of the dataset.
    
    NeuronData objects hold a description string, that should be set with a
    useful description of the method used to generate the underlying data. The
    description string is also used to compare NeuronData instances.  
    """

    ## constructor

    def __init__(self, description=None, **kwargs):
        """
        :Parameters:
            description : str
                Description of the dataset.
            kwargs : dict
                Keyword arguments for subclass implementations.
        :Exceptions:
            ValueError:
                Error for inconsistent parameters.
        """

        # description
        self.description = description or 'Undefined'

        # interface members, these have to be set from the subclass constructor

        # the intracellular voltage trace (1-dimensional ndarray)
        self.intra_v = None
        # the extracellular voltage trace (pot. multi-dimensional ndarray)
        self.extra_v = None
        # the distance to the horizon for this dataset [scalar in µm)
        self.horizon = None
        # the temporal sample rate [scalar in Hz]
        self.sample_rate = None

    ## interface methods - public

    def get_data(self, pos, phase=None):
        """return voltage data for relative position and phase
        
        :Parameters:
            pos : ndarray
                The relative position in the dataset.
            phase : sequence
                The phase within the waveform to retrieve. Either a single
                sample index or a sequence. If None is given, return the
                complete waveform.
                Default=None
        """

        # checking pos
        if vector_norm(pos) > self.horizon:
            raise ValueError('norm of pos beyond horizon!')

        # check for phase
        if phase is None:
            phase = xrange(self.intra_v.size)
        if N.isscalar(phase):
            phase = xrange(phase, phase + 1)

        return self._get_data(pos, phase)

    @staticmethod
    def from_file(path):
        """abstract factory method to create an instance from an archive"""

        raise NotImplementedError

    ## interface methods - private

    def _get_data(self, pos, phase):
        """implementation in subclass!"""

        return N.zeros(len(phase))

    ## special methods

    def __str__(self):
        return '%s ( %s )' % (self.__class__.__name__, self.description)
    def __eq__(self, other):
        if not isinstance(other, NeuronData):
            return False
        else:
            return self.description == other.description
    def __hash__(self):
        return hash(self.description)


class NeuronDataContainer(dict):
    """container to administer a set of NeuronData objects, based on dict
    
    The NeuronDataContainer will assert the uniqueness of its contents, using
    the description string of the NeuronData objects.
    """

    ## constructor

    def __init__(self):

        # super
        super(NeuronDataContainer, self).__init__()

    ## public methods

    def insert(self, ndata_list):
        """insert a list of NeuronData objects

        :Parameters:
            ndata_list : list
                A list of NeuronData objects, that will be added to the
                container. The list should not contain any duplicate NeuronData
                objects, else only the first instance will be added. NeuronData
                objects are compared based on the hash of their self.description
                members.
        :Returns:
            Count of successfully inserted NeuronData instances.
        """

        # assert we have a list to iterate over
        if not isinstance(ndata_list, list):
            ndata_list = [ndata_list]
        rval = 0

        # try to add the items in the list
        for item in ndata_list:
            ndata = None
            if isinstance(item, NeuronData):
                ndata = item
            elif isinstance(item, str):
                ndata = self._ndata_from_file(item)
            else:
                continue
            if ndata is not None:
                rval += self._insert(ndata)

        # return the count of inserted NeuronData objects
        return rval

    ## private methods

    def _insert(self, ndata_item):
        """inserts a single NeuronData object into the container

        :Parameters:
            ndata_item : NeuronData
                The NeuronData object to insert.
        :Return:
            bool : True on success, False, if either item is not a NeuronData
                object or a NeuronData object with the same description is
                already present in the container.
        """

        if isinstance(ndata_item, NeuronData):
            if ndata_item.description in self:
                return False
            else:
                self.__setitem__(ndata_item.description, ndata_item)
                return True
        else:
            return False

    def _ndata_from_file(self, path):
        """try to load a NeuronData subclass from a file
        
        All saveable neuron_data datasets are saved as HDF5 archives. The
        archive must provide the nodes '/__TYPE__' and '/__CLASS__', where
        '/__TYPE__' must match 'NeuronData' and '/__CLASS__' must hold the class
        name to load the dataset with as a string. The class name must reference
        a subclass of NeuronData and must equal that classes __name__ attribute.
        Else loading of the archive will fail! 
        
        :Parameters:
            path : str
                The path to the file.
        :Return:
            NeuronData : NeuronData subclass instance loaded from the archive.
                This instance is read to be added to the container.
            None : If the archive is not recognised as a dataset that can be
                loaded as a subclass of NeuronData.  
        """

        # get class function
        def get_class(kls):
            parts = kls.split('.')
            module = ".".join(parts[:-1])
            m = __import__(module)
            for comp in parts[1:]:
                m = getattr(m, comp)
            return m

        try:
            arc = openFile(path, 'r')
            TYPE = str(arc.getNode('/__TYPE__').read())
            assert TYPE == 'NeuronData'
            CLASS = str(arc.getNode('/__CLASS__').read())
            cls = get_class('nsim.scene.neuron_data.%s' % CLASS)
            ndata = cls.from_file(path)
            return ndata
        except:
            return None
        finally:
            try:
                arc.close()
                del arc
            except:
                pass


##---MAIN

__all__ = ['NeuronData', 'NeuronDataContainer']

if __name__ == '__main__':

    CONTI = NeuronDataContainer()
    print CONTI.insert('/home/phil/Data/Einevoll/LFP-20100516_225124.h5')

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
# nsim - scene/neuron_data/ndata_sampled.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2011-06-27
#

"""archive checking script to set proper tags and classes for new archives"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from tables import openFile
import sys, os


##---ALL

__all__ = [
    'check_archive',
]


##---FUNCTIONS

def check_archive(arc_path):
    """checks a single hdf5 archive for the '#TYPE' and '#CLASS' tags"""

    arc = None
    try:
        arc = openFile(arc_path, 'a')
        print 'checking %s' % arc_path
        try:
            arc.getNode('/#TYPE')
            print '#TYPE good'
        except:
            arc.createArray('/', '#TYPE', 'NeuronData')
            print 'adding #TYPE'
        try:
            arc.getNode('/#CLASS')
            print '#CLASS good'
        except:
            arc.createArray('/', '#CLASS', 'SampledND')
            print 'adding #CLASS'
    except:
        print 'bad archive: %s' % arc_path
    finally:
        if arc is not None:
            arc.close()
    print


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit('Give the path to check for!')
    check_dir = sys.argv[1]

    for arc_name in os.listdir(check_dir):

        if arc_name.endswith('.h5'):
            check_archive(os.path.join(check_dir, arc_name))

    print
    print 'ALL DONE!'

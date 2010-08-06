## -*- coding: utf-8 -*-
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
# sim - start.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""debugging helper functions"""
__doctype__ = 'restructuredtext'


##---IMPORTS

import sys
import types


##---FUNCTIONS

def get_refcounts(n=10):
    """collect the class instance references
    
    :Parameters:
        n : int
            collect a list of the top n items
    """

    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = map (lambda x: (x[1], x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs[:n]

def print_top_n(n=10):
    for cnt, cls in get_refcounts(n):
        print '%10d %s' % (cnt, cls.__name__)

if __name__ == '__main__':

    print_top_n(10)

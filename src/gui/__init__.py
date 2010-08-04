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
# sim - gui/__init__.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2010-02-08
#

"""gui stuff for the simulator"""
__docformat__ = 'restructuredtext'


##---PACKAGE DISTRO

from Ui_add_neuron import Ui_AddNeuronDialog
from Ui_add_recorder import Ui_AddRecorderDialog
from Ui_gui_main import Ui_SimGui
from Ui_init_dialog import Ui_InitDialog
from Ui_recorder_controll import Ui_RecorderControll
from ploting import NTrodePlot

__all__ = ['NTrodePlot', 'Ui_AddNeuronDialog', 'Ui_AddRecorderDialog', 'Ui_InitDialog', 'Ui_RecorderControll', 'Ui_SimGui']


##---MAIN

if __name__ == '__main__':
    pass

# -*- coding: utf-8 -*-
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

__all__ = ['Ui_AddNeuronDialog', 'Ui_AddRecorderDialog', 'Ui_SimGui']


##---MAIN

if __name__ == '__main__':
    pass

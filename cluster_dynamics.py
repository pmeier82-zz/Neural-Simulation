# -*- coding: utf-8 -*-
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
# sim - cluster_dynamics.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-12
#

"""point processes w/ and w/o correlations to generate spiketrains"""
__doctype__ = 'restructuredtext'


##---IMPORTS

# packages
import scipy as N
# own imports
from scene import Neuron


##---CLASSES

class ClusterDynamics(dict):
    """class to administrate the firing behavior of several clusters"""

    ## constructor

    def __init__(self, srate=1.0, o2rate=5.0, o3rate=1.0, soffs=1000):
        """
        :Parameters:
            srate : float
                Global sampling rate.
            o2rate : float
                Global rate of overlaps of two units (in Hz)
            o3rate : float
                Global rate of overlaps of three units (in Hz)
            soffs : int
                Positive offset for cluster ids of singleton neurons.
        """

        # members
        self._o2rate = None
        self._o3rate = None
        self._soffs = soffs
        self._srate = None

        # set members
        self.o2rate = o2rate
        self.o3rate = o3rate
        self.sample_rate = srate

    ## properties

    @property
    def o2rate(self):
        return self._o2rate
    @o2rate.setter
    def o2rate(self, value):
        self._o2rate = float(value)

    @property
    def o3rate(self):
        return self._o3rate
    @o3rate.setter
    def o3rate(self, value):
        self._o3rate = float(value)

    @property
    def sample_rate(self):
        return self._srate
    @sample_rate.setter
    def sample_rate(self, value):
        self._srate = float(value)

    @property
    def singleton_offset(self):
        return self._soffs

    ## interface

    def add_neuron(self, neuron, cls_idx=None):
        """add a neuron to a cluster

        :Parameters:
            neuron : Neuron
                The neuron to add to the cluster.
            cls_idx : int
                Cluster idx or None if not clustered.
                Default=None
        """

# commented to have a dummy class for the unit test
#        # check for Neuron instance
#        if not isinstance(neuron, Neuron):
#            raise ValueError(
#                'neuron is not a Neuron, got %s' % neuron.__class__.__name__
#            )

        # if no cluster given -> singletons
        if cls_idx is None:
            skeys = filter(lambda x: x >= self.singleton_offset, sorted(self.keys()))
            cls_idx = self.singleton_offset
            while cls_idx in skeys:
                cls_idx += 1

        # new entry
        if cls_idx not in self:
            self[cls_idx] = {}

        # append to cluster and return cls_idx
        self[cls_idx][id(neuron)] =[neuron, []]
        return cls_idx

    def remove_neuron(self, key):
        """remove neuron if we have a reference to it"""

        # inits and checks
        if isinstance(key, Neuron):
            lookup = id(key)
        elif isinstance(key, (int, long)):
            lookup = key
        else:
            raise ValueError('%s is not a Neuron or an int/long' % key)
        rval = False

        # search
        for cls in self:
            try:
                self[cls].pop(lookup)
                rval = True
                break
            except:
                continue

        # return
        return rval

    # query methods

    def get_clusters(self):
        """returns list holding a lists of references to the neurons"""

        return [
            [self[cls][item][0] for item in self[cls]]
            for cls in self
        ]

    def get_cls_for_nrn(self, nrn):
        """returns the cluster id for a neuron object"""

        rval = -1
        for cls in self:
            if id(nrn) in self[cls]:
                rval = cls
        return rval

    # run methods

    def generate(self, nsmpls):
        """generate spike trains

        :Parameters:
            nsmpls : int
                Spike trains for how many samples?
        """

        for cls in self:

            # get rates:
            rates = N.asarray([
                self[cls][nrn][0].rate_of_fire for nrn in self[cls]
            ])

            # generate spike trains
            trains = cluster_process(
                rates,
                nsmpls,
                self.sample_rate,
                self.o2rate,
                self.o3rate
            )

            # apply spiketrains to neurons
            idx = 0
            for nrn in self[cls]:
                self[cls][nrn][1] = trains[0][idx]
                idx += 1

    ## special methods

    def get_spike_train(self, key):
        """return current spike train for neuron

        :Parameters:
            key : Neuron or int/long
                Either a reference to a Neuron instance or an int/long
                representing the id(Neuron) of that instance.
        :Returns:
            list : the current spike train of the requested neuron
        :Raises:
            KeyError : if we cannot find a neuron with that key.
        """

        # check key
        if isinstance(key, Neuron):
            lookup = id(key)
        elif isinstance(key, (int, long)):
            lookup = key
        else:
            raise ValueError('%s is not a Neuron or an int/long' % key)

        # look up key
        for cls in self:
            for item in self[cls]:
                if item == lookup:
                    return self[cls][item][1]
        raise KeyError(lookup)

    def __str__(self):
        rval = 'ClusterDynamics (sample_rate:%s)\n' % self.sample_rate
        rval += '{\n'
        for cls in self:
            rval += 'cluster %03d :\n' % cls
            for item in self[cls]:
                rval += '\t%s\n' % self[cls][item]
        rval += '}'
        return rval


##---FUNCTIONS

def cluster_process(single_rates, nsmpls, srate, o2rate=5.0, o3rate=1.0):
    """produce spike trains for N units with overlap rates.

    :Parameters:
        single_rates : list
            List of firing rates (in Hz) for the single units in the cluster
        nsmpls : int
            Length of the simulated events in samples.
        srate : float
            Sample rate (in Hz).
        o2rate : float
            Overlap of 2 events, rate in Hertz. If 0.0 do not put overlaps.
            Default=5.0
        o3rate : float
            Overlap of 3 events, rate in Hertz. If 0.0 do not put overlaps.
            Default=1.0
    """

    # inits
    if not isinstance(single_rates, N.ndarray):
        single_rates = N.asarray(single_rates)
    srate = float(srate)
    cumrate = float(single_rates.sum())
    events = N.asarray(poi_pproc_refper(cumrate, srate, nsmpls))
    props = single_rates / cumrate
    rval = [[] for i in xrange(single_rates.size)]
    o2mem = [[] for i in xrange(single_rates.size)]
    o3mem = [[] for i in xrange(single_rates.size)]

    # label single events according rate statistics
    for e in events:
        rval[label_event(props)].append(e)

    # TODO: assert overlaps of order n do not accidentially produce overlaps of
    # order n+1 or higher

    # overlaps of 2 units
    if o2rate > 0.0 and single_rates.size > 1 and events.size > cumrate / o2rate:
        for i in xrange(int(o2rate * nsmpls / srate)):

            # find unit1 and unit2
            u1 = u2 = label_event(props)
            while u1 == u2:
                u2 = label_event(props)

            # generate random event in range and find unit events closest
            my_ev = int(N.rand() * nsmpls)
            u1_ev, _ = find_close(my_ev, rval[u1])
            u2_ev, _ = find_close(my_ev, rval[u2])
            my_ev = jitter_overlaps(my_ev, int(srate/1000.0), 2)

            # save info and replace events with new overlap event
            rval[u1].insert(u1_ev, my_ev[0])
            rval[u1].pop(u1_ev + 1)
            o2mem[u1].append(my_ev[0])
            rval[u2].insert(u2_ev, my_ev[1])
            rval[u2].pop(u2_ev + 1)
            o2mem[u2].append(my_ev[1])

            # TODO: any break criteria?

    # overlaps of 3 units
    if o3rate > 0.0 and single_rates.size > 2 and events.size > cumrate / o3rate:
        for i in xrange(int(o3rate * nsmpls / srate)):

            # find unit1, unit2 and unit3
            u1 = u2 = u3 = label_event(props)
            while u2 == u1:
                u2 = label_event(props)
            while u3 == u1 or u3 == u2:
                u3 = label_event(props)

            # generate random event in range and find unit events closest
            my_ev = int(N.rand() * nsmpls)
            u1_ev, _ = find_close(my_ev, rval[u1])
            u2_ev, _ = find_close(my_ev, rval[u2])
            u3_ev, _ = find_close(my_ev, rval[u3])
            my_ev = jitter_overlaps(my_ev, int(srate/1000.0), 3)

            # save info and replace events with new overlap event
            rval[u1].insert(u1_ev, my_ev[0])
            rval[u1].pop(u1_ev + 1)
            o3mem[u1].append(my_ev[0])
            rval[u2].insert(u2_ev, my_ev[1])
            rval[u2].pop(u2_ev + 1)
            o3mem[u2].append(my_ev[1])
            rval[u3].insert(u3_ev, my_ev[2])
            rval[u3].pop(u3_ev + 1)
            o3mem[u3].append(my_ev[2])

            # TODO: any break criteria?

    # return
    return rval, o2mem, o3mem


def label_event(props):
    """label an event according to a discrete propability distribution

    :Parameters:
        props: ndarray
            The propabilities of the discrete distribution to draw from.
    :Returns:
        The label as the index into the props array or -1 on error.
    """

    # inits
    if props.sum() != 1.0:
        raise ValueError('props is not normalized')
    rval = None

    # labeling
    rnd = N.rand()
    for i in xrange(props.size):
        if rnd <= props.cumsum()[i]:
            return i
    return -1


def find_close(x, y_vec):
    """finds the index and difference of the closest element in y_vec to x

    :Parameters:
        x : float
            the matching item
        y_vec : ndarray
            the array to look up
    """

    # inits
    rval = -1, None

    # search
    for i in xrange(len(y_vec)):
        temp = N.absolute(y_vec[i] - x)
        if rval[1] is None or temp < rval[1]:
            rval = i, temp

    # return
    return rval


def jitter_overlaps(x, tol, n, nstd=4.0):
    """jitter events so they are within at most tol samples of each other

    :Parameters:
        x : int
            Offset
        tol : int
            max jitter range
        n : int
            n points to generate
        nstd : float
            how many unit std of spread are allowed
    """

    return (N.randn(n) * tol / float(nstd) + x).astype(int)


def poi_pproc_refper(frate, srate, nsmpls, refper=2.5):
    """generate events from a poisson distribution w.r.t refractory period

    :Parameters:
        frate : float
            expected firing rate in Hz
        srate : float
            sample rate in Hz
        nsmpls : int
            generate spike train for that many samples
        refper : int
            refractory period in ms
    :Returns:
        list : spiketrain
    """

    # refractory period
    refper = int(refper * srate / 1000.0)
    if refper * frate > srate:
        raise ValueError('inconsistent values for frate, srate and refper!')

    # inits
    rval = []
    lam = float(srate - frate * refper) / float(frate)
    interval_kernel = lambda: -lam * N.log(N.rand())

    # produce train
    now = refper
    while now < nsmpls:

        # draw samples
        next = int(interval_kernel())
        if next < refper:
            continue
            # XXX: wasteful looping?!

        # its ok
        now += next
        rval.append(now)

    if len(rval) > 0:
        if rval[-1] >= nsmpls:
            rval.pop(-1)

    # return
    return rval


##---MAIN

if __name__ == '__main__':

    # inits
    srate = 16000.0
    nsmpls = 2 * srate
    urates = N.array([35.,  10.,  15.])
    uprops = urates / urates.sum()
    ulabels = ['N35', 'N10', 'N15']

    # tests
    print
    print '## POISSON POINT PROCESS ##'
    print 'testing poi_pproc_refper with [cum_rate, sample_rate, samples]:',
    print urates.sum(), srate, nsmpls
    events_wo_lbls = poi_pproc_refper(urates.sum(), srate, nsmpls)
    print events_wo_lbls
    print 'generated N =', len(events_wo_lbls), 'events,',
    print 'expected', nsmpls / srate * urates.sum()
    print 'assert the refper in 100000 cycles:',
    res = []
    for i in xrange(100000):
        res.append(N.any(N.diff(poi_pproc_refper(urates.sum(), srate, nsmpls)) < 40))
    print sum(res), 'errors'
    print
    print '## BASICS ##'
    print 'testing label generator with [rates, props, labels]:',
    print urates, uprops,  ulabels
    events = []
    print 'generateing', len(events_wo_lbls), 'labels:',
    for e in events_wo_lbls:
        events.append(ulabels[label_event(uprops)])
    print zip(events_wo_lbls, events)
    for i in xrange(len(urates)):
        nobs = len(filter(lambda x: x == ulabels[i], events))
        print ulabels[i], 'observed:', nobs, ', expected:', nsmpls / srate * urates[i]

    print
    print '## CLUSTER PROCESSING ##'
    print 'testing cluster process with [rates, samples, samplerate]:',
    print urates, nsmpls, srate
    cdyn = cluster_process(urates, nsmpls, srate)
    print 'events:', cdyn[0]
    print 'o2mem:', cdyn[1]
    print 'o3mem:', cdyn[2]

    print
    print '## CLUSTER DYNAMICS ##'
    class mynrn(object):
        def __init__(self, frate, name):
            self.rate_of_fire = frate
            self.name = name
        def __str__(self):
            return 'neuron%02d' % self.name
    CD = ClusterDynamics(srate)
    nrns = [mynrn(5*(i+1), i) for i in xrange(7)]
    print 'adding for no cluster:', CD.add_neuron(nrns[0])
    print 'adding for cluster 5:', CD.add_neuron(nrns[1], 5)
    print 'adding for cluster 5:', CD.add_neuron(nrns[2], 5)
    print 'adding for next cluster:',
    cls_idx = CD.add_neuron(nrns[3])
    print cls_idx
    print 'adding for that cluster, which is:', cls_idx, '->', CD.add_neuron(nrns[4], cls_idx)
    print 'adding for next cluster:', CD.add_neuron(nrns[5])
    print 'adding for next cluster(cls_idx=None):', CD.add_neuron(nrns[6], cls_idx=None)
    print CD
    print
    print 'show cluster config'
    print CD.get_clusters()
    print
    print 'generate spiketrain for', nsmpls, 'samples:'
    CD.generate(nsmpls)
    print CD
    print
    print 'query the spiketrain for:', nrns[5]
    print CD.get_spike_train(id(nrns[5]))
    print

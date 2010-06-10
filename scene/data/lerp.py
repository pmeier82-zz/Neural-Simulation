# Written by Espen Hagen, modified by Felix Franke, added to by Philipp Meier

from scipy.interpolate import interp1d, interp2d
import scipy as N
from scipy.linalg import norm


## phil linear interpolation

def LERP1(alpha, v0, v1):
    """linear interpolation for"""

    return ((1 - alpha) * v0) + (alpha * v1)

def LERP2(x, y, v00, v10, v01, v11):
    """bilinear interpolation"""

    return LERP1(
        y,
        LERP1(x, v00, v10), # lower x lerp
        LERP1(x, v01, v11)  # upper x lerp
    )

def LERP3(x, y, z, v000, v100, v010, v110, v001, v101, v011, v111):
    """trilinear interpolation"""

    return LERP1(
        z,
        LERP1(
            y,
            LERP1(x, v000, v100),
            LERP1(x, v010, v110)
        ),
        LERP1(
            y,
            LERP1(x, v001, v101),
            LERP1(x, v011, v111)
        )
    )


## felix interpolation routine

def linear3dinterp(x, y, z, v, r):
    """The easiest linear interpolation possible: calculate one minus the
    distance to all points given by x,y,z. Then set all values below zero to zero.
    Divide every value by the sum of the values and that is your final weight for
    the interpolated point."""

    d = N.empty(len(x))
    for i in xrange(len(x)):
        my_point = N.array([x[i], y[i], z[i]])
        d[i] = 1-norm(my_point - r)
    d[d<0] = 0
    d = d/d.sum()

    rval = N.zeros(v.shape[1])
    for i in xrange(len(x)):
        rval += d[i] * v[i]
    return rval


## espen trilinear interpolation

def interp3d(x, y, z, v, r_i, kind='linear'):
    """Implement trilinear interpolation as linear interpolation along z-axis
    between two bilinear interpolations in the two xy-planes

    by Espen Hagen
    """

    #find indices of bottom and top plane of cube
    r = N.where(z==z.min())
    s = N.where(z==z.max())

    if v.ndim == 2:
        c, d = v.shape
        v_i = N.empty(d)

        for i in xrange(d):

            #bilinear interpolation functions in the xy-planes
            a = interp2d(x[r], y[r], v[r,i], kind=kind)
            b = interp2d(x[s], y[s], v[s,i], kind=kind)

            #interpolate in the xy-planes
            v_i1 = a(r_i[0], r_i[1])[0]
            v_i2 = b(r_i[0], r_i[1])[0]

            #linear interpolation along z-axis, from the values determined in the xy-planes
            c = interp1d(
                N.array([z.min(), z.max()]),
                N.array([v_i1, v_i2]),
                kind='linear'
            )
            v_i[i] = c(r_i[2])

    else:
        #bilinear interpolation functions in the xy-planes
        a = interp2d(x[r], y[r], v[r], kind=kind)
        b = interp2d(x[s], y[s], v[s], kind=kind)

        #interpolate in the xy-planes
        v_i1 = a(r_i[0], r_i[1])[0]
        v_i2 = b(r_i[0], r_i[1])[0]

        #linear interpolation along z-axis, from the values determined in the xy-planes
        c = interp1d(
            N.array([z.min(), z.max()]),
            N.array([v_i1, v_i2]),
            kind=kind
        )
        v_i = c(r_i[2])

    return v_i


##---MAIN

if __name__ == '__main__':

    from pylab import array,rand,diff,where,figure,close,squeeze,shape,empty, show
    from mpl_toolkits.mplot3d import Axes3D

    close('all')

    #Grid coordinates of unit cube
    x = array([0., 0., 0., 0., 1., 1., 1., 1.])
    y = array([0., 1., 1., 0., 0., 1., 1., 0.])
    z = array([0., 0., 1., 1., 0., 0., 1., 1.])

    #random values in coordinates
    v = rand(8)

    #where to calculate v_i
    r_i = rand(3)

    v_i = interp3d(x,y,z,v,r_i)


    print('Interpolated value in position (%g,%g,%g) is:' % (r_i[0],r_i[1],r_i[2]))
    print(v_i)

    if v.ndim == 1:
        fig = figure()
        ax = Axes3D(fig)
        ax.plot(x,y,z,marker='o',markersize=5,linestyle='none')
        ax.plot([r_i[0]],[r_i[1]],[r_i[2]],marker='o',markersize=5,linestyle='none')
        for i in xrange(8):
            ax.text(x[i],y[i],z[i],r'$\psi=$%g' % v[i])
        ax.text(r_i[0],r_i[1],r_i[2],r'$\psi_i=$%g' % v_i)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        show()

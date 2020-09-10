#!/usr/bin/env python3

import sympy as sy
import matplotlib.pyplot as plt
import numpy as np
from numpy import arcsin, arctan2, cos, sin, unwrap, sqrt
from scipy.optimize import curve_fit
from skyfield.api import load, tau

def main():
    # solve_equant()
    # return

    # plot_equant()
    # return

    ts = load.timescale()

    days = 365 * 10
    t = ts.tt(2010, 1, range(days))

    # t = ts.tt(2010, 1, range(365 * 1))
    # t = ts.tt(2010, 1, range(75, 85))
    # t = ts.tt(2010, 1, 79, range(48))
    #for i, x in enumerate(t.utc_jpl()):
    # for x in t.utc_jpl():
    #     #print(('****' if i == 10 else ''), x)
    #     print(x)

    planets = load('de421.bsp')
    planet = planets['sun']
    # planet = planets['jupiter barycenter']
    earth = planets['earth']
    #lat, lon, distance = earth.at(t).observe(sun).apparent().ecliptic_latlon()
    lat, lon, distance = earth.at(t).observe(planet).ecliptic_latlon()

    #lon = lon.degrees
    longitude = unwrap(lon.radians)
    # import numpy as np
    # t = np.arange(0.0, 2.0, 0.01)
    # s = 1 + np.sin(2 * np.pi * t)

    day = t.tt - t.tt[0]

    #dt = t.tt[1:] - t.tt[:-1]

    fig, ax = plt.subplots()
    #ax.plot(t, s, label='label', linestyle='--')

    #equant = equant(T, ω, e)

    #ax.plot(day, lon)
    #ax.plot(day, degrees(equant(day, T, M0, ω, e)) - degrees(lon))
    #ax.plot(day[:-1], dt)

    #print(T, M0, e, ω)

    # (T, M0, xe, ye), covariance = curve_fit(equant, day, lon, (T, M0, ye, ye))
    T, M0, xe, ye = fit_equant(day, longitude)

    print(T, M0, xe, ye)
    print([day[0], day[1], day[2]])
    print(equant_orbit([day[0], day[1], day[2]], T, M0, xe, ye))

    # T, M0, e, ω, Tₑ, E0, r = fit_equant_and_epicycle(
    #     days, longitude, T, M0, e, ω,
    # )

    # print(T, M0, e, ω, Tₑ, E0, r)

    # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    angle = equant_orbit(day, T, M0, xe, ye)

    # ax.plot(day, degrees(longitude))
    # ax.plot(day, degrees(angle))

    residual = angle - longitude

    ax.plot(day, degrees(residual))
    # ax.plot(day, degrees(equant(day, T, M0, e, ω) + epicycle(day, Tₑ, E0, r)
    #                      - longitude))

    #ax.plot(day, degrees(equant(day, T, ω, -e)) - degrees(lon))
    #ax.plot(day, degrees(equant(day, T, ω-tau/2, -e)+tau/2) - degrees(lon))

    # ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Title')
    # ax.set_aspect(aspect=1.0)
    # ax.grid()
    # plt.legend()
    fig.savefig('tmp.png')

from scipy.optimize import fsolve

def fit_equant(day, longitude):
    days = day[-1] - day[0]
    revolutions = (longitude[-1] - longitude[0]) / tau
    T = days / revolutions
    M0 = longitude[0]
    xe = 0
    ye = 0

    # print(days)
    # print(revolutions)
    (T, M0, xe, ye), covariance = curve_fit(
        equant_orbit, day, longitude, (T, M0, xe, ye),
    )

    # # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    return T, M0, xe, ye

def fit_equant_and_epicycle(day, longitude, T, M0, e, ω):
    Tₑ = 300
    E0 = 0
    r = 0.5

    def f(t, Tₑ, E0, r):
        return equant(t, T, M0, e, ω) + epicycle(t, Tₑ, E0, r)

    (Tₑ, E0, r), covariance = curve_fit(f, day, longitude, (Tₑ, E0, r))

    # def f(t, T, M0, e, ω, Tₑ, E0, r):
    #     return equant(t, T, M0, e, ω) + epicycle(t, Tₑ, E0, r)

    # Normalize negative e by rotating the orbit 180°.
    if e < 0:
        e = -e
        ω += tau/2
        M0 -= tau/2

    # Normalize ω.
    offset, ω = divmod(ω, tau)
    M0 += offset * tau

    return T, M0, e, ω, Tₑ, E0, r

def degrees(radians):
    return radians / tau * 360.0

def plot_equant():
    M = np.linspace(0, tau * 50.0 / 60.0, 60)
    x, y = equant(M, 0.5, 0.0)
    # print(M)
    # print(x)
    # print(y)
    # print(1 - x*x - y*y)

    fig, ax = plt.subplots()
    ax.plot(x, y, 'o')
    ax.set_aspect(aspect=1.0)
    ax.grid()
    fig.savefig('equant.png')

def equant_orbit(t, T, M0, xe, ye):
    M = M0 + t / T * tau
    x, y = equant(M, xe, ye)
    return unwrap(arctan2(y + ye, x + xe) % tau)

def equant(M, xe, ye):
    offset = arctan2(ye, xe)
    Mo = M - offset
    e = sqrt(xe*xe + ye*ye)
    a = Mo - arcsin(e * sin(Mo))
    a += offset
    return cos(a), sin(a)

def epicycle(t, Tₑ, E0, r):
    E = E0 + t / Tₑ * tau
    return r * sin(E)

if __name__ == '__main__':
    main()
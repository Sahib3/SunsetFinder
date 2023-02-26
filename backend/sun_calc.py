# %%
import base64
import requests
import pandas as pd
import numpy as np
import math
from datetime import date, datetime
from dateutil import tz

# Allow us to see more clearly the output
pd.set_option('float_format', '{:f}'.format)


# %%
# Here is the basic request if we know the lat and longitude
# We can dynamically generate this endpoint to get this data
response = requests.get(
    "https://api.sunrisesunset.io/json?lat=38.907192&lng=-77.036873&timezone=UTC&date=today")

print(response._content)

# %%
# As we can see from the response from that API, we do not know the position of the sun. I found this site:
# https://gml.noaa.gov/grad/solcalc/calcdetails.html which has an excel sheet that takes the following inputs:
# latitude, longitude, time zone and date. I suggest we adapt this to a python script that can take those as inputs
# and then we can return the sunrise, sunset, and solar position without talking to an API.

# The rest of this script is converting the math that they used and recreate the calculator

# %%
# Inputs from the user. TODO Probably will come via frontend HTTP request so will need to be adapted
Date = pd.to_datetime('6/21/2010')
latitude = 40
longitude = -105
time_zone_object = tz.gettz('UTC')
time_zone = 0


# %%
# Create an empty dataframe to populate with our important information
pd.DataFrame(columns=['Date', 'Time (past local midnight)'])

# %%
# Create an empty np array and set the first time to be six minutes past midnight, as they do in the spreadsheet
#
local_times = np.empty(240, dtype=float, order='C', like=None)
local_times[0] = 0.004166666666666667

# %%
# Populate the local_times list with times six minutes apart
for idx, item in enumerate(local_times[1:]):
    local_times[idx+1] = local_times[idx] + (0.1/24)

# %%
# add local_time to our df
df = pd.DataFrame(local_times, columns=["local_time"])
local_times


# %%

my_date = datetime(2010, 6, 21, tzinfo=time_zone_object)
my_date = my_date.toordinal()

# %%
# 6/21/2010

# %%
# from datetime import datetime, timedelta


# def datetime_range(start, end, delta):
#     current = start
#     while current < end:
#         yield current
#         current += delta

# dts = [pd.to_datetime(dt.strftime('%Y-%m-%d T%H:%M Z')) for dt in
#        datetime_range(datetime(2010, 6, 21, 0), datetime(2010, 6, 21, 9+12),
#        timedelta(minutes=6))]

# print(dts)

# %%
# Conver date to Julian Day
# =D2+2415018.5+E2-$B$5/24
julian_day_list = [(my_date + 1721424.5 + lt) for lt in local_times]
julian_day_list

# %%
df['Julian Day'] = np.float64(julian_day_list)

# %%
# Find Julian Century
df['Julian Century'] = (df['Julian Day'] - 2451545.0) / 36525.0

# %%
# The following sections are conversions of the excel formulas to calculate the other values in the table
df['Geom Mean Long Sun (deg)'] = (280.46646 + df['Julian Century'] * (
    36000.76983 + df['Julian Century']*0.0003032
)) % 360
df['Geom Mean Anom Sun (deg)'] = (357.52911 + df['Julian Century'] * (
    35999.05029 - 0.0001537 * df['Julian Century']))
df['Eccent Earth Orbit'] = 0.016708634 - df['Julian Century'] * (
    0.000042037+0.0000001267*df['Julian Century'])
df['Sun Eq of Ctr'] = np.sin(
    np.radians(df['Geom Mean Anom Sun (deg)'])
) * (
    1.914602-df['Julian Century']*(0.004817+0.000014*df['Julian Century'])
) + np.sin(
    np.radians(2 * df['Geom Mean Anom Sun (deg)'])
) * (
    0.019993 - 0.000101 * df['Julian Century']
) + np.sin(
    np.radians(3*df['Geom Mean Anom Sun (deg)'])
) * 0.000289
df['Sun True Long (deg)'] = df['Geom Mean Long Sun (deg)'] + \
    df['Sun Eq of Ctr']
df['Sun True Anom (deg)'] = df['Geom Mean Anom Sun (deg)'] + \
    df['Sun Eq of Ctr']
df['Sun Rad Vector (AUs)'] = (
    1.000001018 * (
        1 - df['Eccent Earth Orbit'] * df['Eccent Earth Orbit'])
) / (
    1 + df['Eccent Earth Orbit']*np.cos(np.radians(df['Sun True Anom (deg)'])))
df['Sun App Long (deg)'] = df['Sun True Long (deg)'] - 0.00569 - 0.00478\
    * np.sin(
    np.radians(125.04 - 1934.136 * df['Julian Century'])
)
df['Mean Obliq Ecliptic (deg)'] = 23 + (
    26 + (
        (21.448 - df['Julian Century'] * (
            46.815 + df['Julian Century'] * (
                0.00059 - df['Julian Century'] * 0.001813))))
    / 60)/60

df['Obliq Corr (deg)'] = df['Mean Obliq Ecliptic (deg)'] + 0.00256 * np.cos(
    np.radians(125.04 - 1934.136 * df['Julian Century']))

# some of the operations need to be applied to the df as a lambda, they are only used once
# thats why I they are declared the functions here. Could be optimized


def calc_sun_rt_acen_deg(sun_app_long, oblique):
    return np.degrees(
        math.atan2(
            (np.cos(np.radians(oblique))*np.sin(np.radians(sun_app_long))), (np.cos(np.radians(sun_app_long)))))


df['Sun Rt Ascen (deg)'] = df.apply(
    lambda x: calc_sun_rt_acen_deg(x['Sun App Long (deg)'], x['Obliq Corr (deg)']), axis=1)


def calc_sun_decline_deg(obliq, sun_app):
    return np.degrees(math.asin(np.sin(np.radians(obliq))*np.sin(np.radians(sun_app))))


df['Sun Declin (deg)'] = df.apply(
    lambda x: calc_sun_decline_deg(x['Obliq Corr (deg)'], x['Sun App Long (deg)']), axis=1)

df['var y'] = np.tan(np.radians(df['Obliq Corr (deg)'] / 2)) * \
    np.tan(np.radians(df['Obliq Corr (deg)'] / 2))

df['Eq of Time (minutes)'] = 4 * np.degrees(
    df['var y'] * np.sin(
        2 * np.radians(
            df['Geom Mean Long Sun (deg)'])
    ) - 2 * df['Eccent Earth Orbit'] * np.sin(
        np.radians(
            df['Geom Mean Anom Sun (deg)'])
    ) + 4 * df['Eccent Earth Orbit'] * df['var y'] * np.sin(np.radians(df['Geom Mean Anom Sun (deg)']))
    * np.cos(2 * np.radians(df['Geom Mean Long Sun (deg)'])) - 0.5 * df['var y'] * df['var y']
    * np.sin(
        4 * np.radians(df['Geom Mean Long Sun (deg)'])
    ) - 1.25 * df['Eccent Earth Orbit'] * df['Eccent Earth Orbit'] * np.sin(
        2 * np.radians(df['Geom Mean Anom Sun (deg)'])))


def calc_ha_sunrise_deg(latitude, sun_decline):
    return np.degrees(
        math.acos(
            np.cos(np.radians(90.833)) / (np.cos(np.radians(latitude)
                                                 ) * np.cos(np.radians(sun_decline))) - np.tan(
                np.radians(latitude)) * np.tan(np.radians(sun_decline))))


df['HA Sunrise (deg)'] = df.apply(lambda x: calc_ha_sunrise_deg(
    latitude, x['Sun Declin (deg)']), axis=1)

df['Solar Noon (LST)'] = (720 - 4 * longitude -
                          df['Eq of Time (minutes)'] + time_zone * 60) / 1440

df['Sunrise Time (LST)'] = df['Solar Noon (LST)'] - \
    df['HA Sunrise (deg)'] * 4 / 1440

df['Sunset Time (LST)'] = df['Solar Noon (LST)'] + \
    df['HA Sunrise (deg)'] * 4 / 1440

df['Sunlight Duration'] = 8 * df['HA Sunrise (deg)']

df['True Solar Time (min)'] = df['local_time'] * 1440 + df['Eq of Time (minutes)'] + 4\
    * longitude - 60 * time_zone % 1440


def calc_hour_angle_deg(true_solar_time):
    if true_solar_time / 4 < 0:
        return true_solar_time / 4 + 180
    else:
        return true_solar_time / 4 - 180


df['Hour Angle (deg)'] = df.apply(
    lambda x: calc_hour_angle_deg(x['True Solar Time (min)']), axis=1)


def calc_solar_zeith(latitude, sun_declin_deg, hour_angle):
    return np.degrees(
        math.acos(np.sin(np.radians(latitude)) * np.sin(
            np.radians(sun_declin_deg)) + np.cos(np.radians(latitude)) * np.cos(
            np.radians(sun_declin_deg)) * np.cos(np.radians(hour_angle))))


df['Solar Zenith Angle (deg)'] = df.apply(
    lambda x: calc_solar_zeith(latitude, x['Sun Declin (deg)'], x['Hour Angle (deg)']), axis=1)

df['Solar Elevation Angle (deg)'] = 90 - df['Solar Zenith Angle (deg)']


def calc_approx_atm(solar_elevation):
    if solar_elevation > 85:
        temp = 0
    elif solar_elevation > 5:
        temp = 58.1/np.tan(np.radians(solar_elevation))-0.07/np.power(np.tan(np.radians(solar_elevation)), 3)\
            + 0.000086 / np.power(np.tan(np.radians(solar_elevation)), 5)
    elif solar_elevation > -0.575:
        temp = 1735+solar_elevation * \
            (-518.2+solar_elevation *
             (103.4+solar_elevation*(-12.79+solar_elevation*0.711)))
    else:
        temp = -20.772/np.tan(np.radians(solar_elevation))
    return temp / 3600


df['Approx Atmospheric Refraction (deg)'] = df.apply(
    lambda x: calc_approx_atm(x['Solar Elevation Angle (deg)']), axis=1)

df['Solar Elevation corrected for atm refraction (deg)'] = df['Solar Elevation Angle (deg)'] + \
    df['Approx Atmospheric Refraction (deg)']


def calc_azimuth_angle(sun_decline, hour_angle, solar_zenith_angle):
    if hour_angle > 0:
        return np.degrees(
            math.acos(
                ((np.sin(np.radians(latitude))*np.cos(np.radians(solar_zenith_angle)))-np.sin(np.radians(sun_decline))
                 )/(np.cos(np.radians(latitude))*np.sin(np.radians(solar_zenith_angle))))) + 180 % 360
    else:
        return 540 - np.degrees(
            math.acos(((np.sin(np.radians(latitude)) * np.cos(np.radians(solar_zenith_angle))
                        ) - np.sin(np.radians(sun_decline))
                       ) /
                      (np.cos(np.radians(latitude)) * np.sin(np.radians(solar_zenith_angle))))) % 360


df['Solar Azimuth Angle (deg cw from N)'] = df.apply(
    lambda x: calc_azimuth_angle(x['Sun Declin (deg)'], x['Hour Angle (deg)'], x['Solar Zenith Angle (deg)']), axis=1)

# %%
df

# %%
df.info()

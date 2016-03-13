"""
This module is used to fake the original hyperion functions

Created on 27.11.2014

@author: Fabian Hertwig
"""
import imp
from json_client import JsonClient

ledCount = 0

# the data as set in the hypercon application
# horizontal = 0
# vertical = 0
# first_led_offset = 0
# clockwise_direction = False
# corner_leds = False
leds = None
leds_top = None
leds_right = None
leds_bottom = None
leds_left = None
clockwise = False

hyperion_json = None
proto_client = None

# the dictionary the hyperion effect will access
args = {}

_ledData = None
_abort = False

""" helper functions """

def init(_leds, _leds_top, _leds_right, _leds_bottom, _leds_left, proto, json, host, port):
    """
    Initialise the fake hyperion configuration. The values should be identical to your hyperion configuration.
    :param horizontal_led_num: the number of your horizontal leds
    :param vertical_led_num: the number of your vertical leds
    :param first_led_offset_num: the offset value
    :param leds_in_clockwise_direction: boolean: are your leds set up clockwise or not
    :param has_corner_leds: boolean: are there corner leds
    """
    # global ledCount, _ledData, horizontal, vertical, first_led_offset, clockwise_direction, corner_leds, led_array
    global ledCount, leds, leds_top, leds_right, leds_bottom, leds_left, clockwise, hyperion_json, proto_client

    ledCount = len(_leds)
    leds = _leds
    leds_top = _leds_top
    leds_right = _leds_right
    leds_bottom = _leds_bottom
    leds_left = _leds_left

    if proto and not json:
        from lib.hyperion.Hyperion import Hyperion
        proto_client = Hyperion(host, port)

    if json:
        from devkit.JsonClient import JsonClient
        hyperion_json = JsonClient(host, port, 10)
        hyperion_json.connect()


    # horizontal = horizontal_led_num
    # vertical = vertical_led_num
    # first_led_offset = first_led_offset_num
    # clockwise_direction = leds_in_clockwise_direction
    # corner_leds = has_corner_leds
    # led_array = leds

    _ledData = bytearray()
    for x in range(ledCount * 3):
        _ledData.append(0)


def set_abort(abort_hyperion):
    global _abort
    _abort = abort_hyperion


def get_led_data():
    led_data_copy = bytearray()
    if _ledData:
        imp.acquire_lock()
        led_data_copy = bytearray(_ledData)
        imp.release_lock()

    return led_data_copy

def set_args(_args):
    global args
    args = _args


""" fake hyperion functions """


def abort():
    return _abort

def send_data(data):
    global hyperion_json, proto_client
    if hyperion_json is not None:
        hyperion_json.send_led_data(data)

def set_color_led_data(led_data):
    global _ledData
    imp.acquire_lock()
    _ledData = bytearray(led_data)
    imp.release_lock()
    send_data(_ledData)


def set_color_rgb(red, green, blue):
    global _ledData
    imp.acquire_lock()
    for i in range(len(_ledData) / 3):
        _ledData[3*i] = red
        _ledData[3*i + 1] = green
        _ledData[3*i + 2] = blue
    imp.release_lock()
    send_data(_ledData)

def setColor(*args):
    if len(args) == 1:
        set_color_led_data(args[0])
    elif len(args) == 3:
        set_color_rgb(args[0], args[1], args[2])
    else:
        raise TypeError('setColor takes 1 or 3 arguments')
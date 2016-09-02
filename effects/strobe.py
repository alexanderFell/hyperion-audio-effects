""" Strobe effect """
""" written by Alexander Fell (alexanderfell@gmx.de) """

from app import hyperion
import time
from random import randint

from effects.spectrum_dump import GstSpectrumDump


BLACK = (0, 0, 0)

class Effect(object):
    def __init__(self):

        self.processing = False
        self._leds_data = bytearray(hyperion.ledCount * (0, 0, 0))

        args = hyperion.args

        self.magnitude_min = int(args.get('magnitude-min', 0))
        self.magnitude_max = int(args.get('magnitude-max', 100))
        self.magnitude_th = int(args.get('magnitude-threshold', 60))
        self.magnitude_oct = int(args.get('magnitude-octaves', 4))
        self.interval = int(args.get('interval', 100))

        self.leds_left = hyperion.leds_left
        self.leds_right = hyperion.leds_right
        self.leds_right.reverse()

        self._magnitudes = None


        print 'Effect: Strobe'
        print '----------------'
	print 'Note: with alsamixer you can adjust the mic levels, if one is attached.'

	mixBands = 4

        self._spectrum = GstSpectrumDump(
            source=hyperion.args.get('audiosrc','autoaudiosrc'),
            vumeter=False,
            interval=self.interval,
            quiet=True,
            bands=mixBands,
            callback=self.receive_magnitudes
            )
        self._spectrum.start()

	if self.magnitude_oct > mixBands:
		self.magnitude_oct = mixBands

        print 'Effect started, waiting for gstreamer messages...'

    def __del__(self):
        self.stop()

    def stop(self):
        self._spectrum.stop()

    def receive_magnitudes(self, magnitudes):

        # Don't update when processing
        if self.processing:
            return
        else:
            self._magnitudes = magnitudes
            self.update_leds()
            hyperion.setColor(self._leds_data)



    def get_led_color(self):
	red = randint(0, 255)
	green = randint(0, 255)
	blue = randint (0, 255)

	color = randint(0, 16777215)
	blue = color & 255
	color >>= 8
	green = color & 255
	color >>= 8
	red = color & 255

	return (red, green, blue)


    def update_leds(self):

        self.processing = True

	magnitude = 0
	for i in range(0, self.magnitude_oct):
		magnitude += self._magnitudes[i]

	magnitude /= self.magnitude_oct

	magnitude = self._magnitudes[0] #+ self._magnitudes[1])/2;

	#print magnitude

	if magnitude > self.magnitude_th:
		self._leds_data[0:hyperion.ledCount] = self.get_led_color()
	else:
		self._leds_data[0:hyperion.ledCount] = BLACK


        self.processing = False


def run():
    """ Run this effect until hyperion aborts. """
    effect = Effect()

    # Keep this thread alive
    while not hyperion.abort():
        time.sleep(1)

    effect.stop()

if __name__ == "<run_path>":
	run()

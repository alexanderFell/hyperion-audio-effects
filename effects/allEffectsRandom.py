"""All effects randomly selected"""

from app import hyperion
import time
import json
import importlib
from random import randint


class AllEffects(object):
	def __init__(self):
		self.effect = None
		self.args = hyperion.args
		self.minTime = int(self.args.get('minTime', 10))
		self.maxTime = int(self.args.get('maxTime', 300))

		temp = self.args.get('effects', None)

		if len(temp) == 0:
			print "No effects configured!"
			exit(-1)

		self.effectArray = []
		print "Effects found: "
		for i in range(0, len(temp)):
			self.effectArray.append(temp[i].values()[0])
			print self.effectArray[i]


	def rereadArgs(self, effectTitle):
		with open('effects/' + effectTitle + '.json') as effect_json:
			effectConfig = json.load(effect_json)
			effect_args = effectConfig.get('args', {})
			effect_args['audiosrc'] = self.args.get('audiosrc')
			effect_args['matrix'] = self.args.get('matrix')
			hyperion.set_args(effect_args)


	def startEffect(self):
		if self.effect != None:
			self.effect.stop()

		effectIndex = randint(0, len(self.effectArray)-1)

		print 'Next effect starting:', self.effectArray[effectIndex]
		self.rereadArgs(self.effectArray[effectIndex])

		#-- dynamically load the new class, create an instance and start it
		NewEffectClass = getattr(importlib.import_module("effects." + self.effectArray[effectIndex]), "Effect")
		self.effect = NewEffectClass();


	def newRandomTime(self):
		randomSleepTime = randint(self.minTime, self.maxTime)
		print 'Time till next effect: ', randomSleepTime, 's'
		return randomSleepTime




def run():

	allEffects = AllEffects()
	randomSleepTime = allEffects.newRandomTime()
	allEffects.startEffect()


	# Keep this thread alive
	while not hyperion.abort():
		time.sleep(1)
		randomSleepTime -= 1
		if randomSleepTime <= 0:
			randomSleepTime = allEffects.newRandomTime()
		        allEffects.startEffect()

	allEffects.effect.stop()

run()

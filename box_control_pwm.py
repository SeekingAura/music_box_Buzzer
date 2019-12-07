# Import standard python modules
import time
import sys
import argparse

# Import RPi.GPIO library
import RPi.GPIO as GPIO

# Beats
# https://ainolnaim.wordpress.com/2b-tempo-beats-and-ties/

# Compresion how to write a pentagram respective to Beats
# https://www.musicnotes.com/now/tips/a-complete-guide-to-time-signatures-in-music/

# Time values notes with preview
# https://www.mymusictheory.com/learn-music-theory/reference/605-the-time-values-of-notes

# Notes names
# https://en.wikipedia.org/wiki/Note_value

# Tempo is the number of Quarter notes or crotchet per minute, for example
# Tempo 60 indicates are 60 beats or crotchet or quarter notes in one minute

class MusicBox:

	def __init__(self, pin_num, dutyCycle=50, tempo=151):
		# Number of Pin where are connected a buzzer
		self.pin_num=pin_num
		
		# Duty cycle must be 50 for square signals
		self.dutyCycle=dutyCycle

		# Tempo defines speed of song or frequency (time base crotchet)
		self.tempo=tempo

		# Start time the note or silence
		self.noteTimeStart=time.time()

		# Flag for check stop pwm
		self.is_stop=True

		# Dict of notes with respective frequency
		self.notes_dict={
		
			# level 3
			"c3":	130.813,	# Do
			"c#3":	138.591,	# Do sostenido
			"d3":	146.832,	# Re
			"d#3":	155.563,	# Re sostenido
			"e3":	164.814,	# Mi
			"f3":	174.614,	# Fa
			"f#3":	184.997,	# Fa sostenido
			"g3":	195.998,	# Sol
			"g#3":	207.652,	# Sol sostenido
			"a3":	220,		# La
			"a#3":	233.082,	# La sostenido
			"b3":	246.942,	# Si
			"c4":	261.626,
			"c#4":	277.183,
			"d4":	293.665,
			"d#4":	311.127,
			"e4":	329.628,
			"f4":	349.228,
			"f#4":	369.994,
			"g4":	391.995,
			"g#4":	415.305,
			"a4":	440,
			"a#4":	446.164,
			"b4":	493.883,
			"c5":	523.251,
			"c#5":	554.365,
			"d5":	587.330,
			"d#5":	622.254,
			"e5":	659.255,
			"f5":	698.456,
			"f#5":	739.989,
			"g5":	783.991,
			"g#5":	830.609,
			"a5":	880,
			"a#5":	932.328,
			"b5":	987.767,
			"c6":	1046.502,
			"c#6":	1108.731,
			"d6":	1174.659,
			"d#6":	1244.508,
			"e6":	1318.510,
			"f6":	1396.913,
			"f#6":	1479.978,
			"g6":	1567.982,
			"g#6":	1661.219,
			"a6":	1760,
			"a#6":	1864.655,
			"b6":	1975.533

		
		}

		self.songContent=""
		
		# PWM object observer, default note 'c3'
		self.pwmNote=GPIO.PWM(self.pin_num, self.notes_dict.get("c3"))
		
	
	def setNote(self, note):
		print("'{}'".format(note)) 
		note=float(self.notes_dict.get(note))
		self.pwmNote.ChangeFrequency(note)
		if(self.is_stop):
			self.is_stop=False
			self.pwmNote.start(self.dutyCycle)
		self.noteTimeStart=time.time()
	
	def setSilence(self):
		if(not self.is_stop):
			self.is_stop=True
			self.pwmNote.stop()
		self.noteTimeStart=time.time()

	def loadSongFile(self, file_name):
		"""
		Song format is
		note,duration

		Notes are write in english name for example, c3, d3, e3, f3, etc

		Durations are write in numbers, for example, 4 is semibreve, 2 is minim,
		1 is crotchet, 0.5 is quaver, 0.25 is semiquaver

		Then notes are separated by \n
		note, time,   indexRepeat,    RepeatTimes
		"e5", 1,      0,    1
		"""
		# Create instance file and open
		fileOpen=open(file_name, "r", encoding="utf8")

		# Load file from Disk to Ram (in var type string)
		self.songContent=fileOpen.read()

		# Close file
		fileOpen.close()

	def playNote(self, note, duration):
		# Check if are silence
		if(note=="s"):
			self.setSilence()
		else:
			self.setNote(note)
		# Time for note, tempo is number of 
		time.sleep(duration*(60/self.tempo))

		# Extra time beetwhen notes
		# time.sleep(duration*(1/self.tempo)*0.1)

	def repeatPart(self, indexStart, indexTo, times):
		if(times==0):
			return
		# Update repeat times
		times=times-1
		for enum, noteI in enumerate(self.songContent.split("\n")[indexStart:indexTo+1]):
			note, duration, repeatIndexStart, repeatTimes=eval("["+noteI+"]")

			self.playNote(note, duration)

			# Check if are the note base of repeat
			if(enum+indexStart==indexTo):
				self.repeatPart(indexStart, indexTo, times)
			else:
				self.repeatPart(repeatIndexStart, enum, repeatTimes)
				



	def playSong(self):
		# Play Song from file
		for enum, noteI in enumerate(self.songContent.split("\n")):
			note, duration, repeatIndexStart, repeatTimes=eval("["+noteI+"]")

			self.playNote(note, duration)

			self.repeatPart(repeatIndexStart, enum, repeatTimes)
				

			




# Define Function "main", way to manage errors
def main():
	# Construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-dc", "--dutyCycle", type=float, required=False, default=50.0,
		help="dutycyle for pwm, makes effects on song")
	ap.add_argument("-t", "--tempo", type=int, required=False, default=200,
		help="value for tempo of song (speed of song, more higher, more speed)")
	ap.add_argument("-pp", "--pinPWM", type=int, required=False, default=4,
		help="value for tempo of song (speed of song, more higher, more speed)")
	ap.add_argument("-sf", "--songFile", type=str, required=True,
		help="file to read for play with buzzer")
	args = vars(ap.parse_args())
	# GPIO pin for control music box
	buzzer_pin=args["pinPWM"]

	# Set GPIO pin mode
	GPIO.setmode(GPIO.BCM)
	# Set GPIO pin direction and initial in Off
	GPIO.setup(buzzer_pin, GPIO.OUT, initial=GPIO.LOW)   
	
	# Create instance MusicBox in music_box
	music_box=MusicBox(buzzer_pin, dutyCycle=args["dutyCycle"], tempo=args["tempo"])

	# Load song from file
	music_box.loadSongFile(args["songFile"])

	# Play the last loaded song in to respective buzzer pin
	music_box.playSong()
	
	
	# Clean
	GPIO.cleanup()

if __name__ == "__main__":
	try:
		main()
	except:
		print("{} line {}".format(sys.exc_info()[0], sys.exc_info()[-1].tb_lineno))
		GPIO.cleanup()
	
	

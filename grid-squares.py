#!/usr/bin/env python
#
# gridsquares viewer v0.0.1
# Copyright 2015 Marcus Berglund
# All unauthorised use and access of this file is strictly prohibited 
# and will be prosecuted to the fullest extent of the law
#

import cgi, sqlite3, sys

# debug mode:
import cgitb
cgitb.enable()

form = cgi.FieldStorage()

myname = "grid-squares.py"

# headers
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head><title>Grid Squares Leaderboard</title>"
print "<link rel='stylesheet' type='text/css' href='gsc.css'>"
print "</head><body>"

# errors to std out
sys.stderr = sys.stdout

# connect to database
conn = sqlite3.connect("/opt/gsc/gsc.db")
c = conn.cursor()

class Bands(object):
	""" A class to handle band data
		For now, stores band information, order and generates html links

		Can be extended in the future to take a frequency and return band
	"""

	# Variables:
	bandList = {'6': '6m',
				'2': '2m',
				'70': '70cm',
				'23': '23cm',
				'13': '2.4GHz',
				'9': '3.4GHz',
				'5': '5.8GHz',
				'10': '10GHz',
				'24': '24GHz',
				'47': '47GHz'}

	bandOrder = ['6', '2', '70', '23', '13', '9', '5', '10', '24', '47']

	viewActivator = "banda"
	viewChaser = "bandc"

	bands = []

	def __init__(self):
		pass # nothing yet

	@staticmethod
	def activatorHTML():
		for band in Bands.bandOrder:
			print "<li><a href='grid-squares.py?view=%s&band=%s'>%s</a></li>" % (Bands.viewActivator, band, Bands.getBand(band))

	#def toActivatorHTML(self, band):
	#	self.toHTML(self.viewActivator, band)

	@staticmethod
	def chaserHTML():
		for band in Bands.bandOrder:
			print "<li><a href='grid-squares.py?view=%s&band=%s'>%s</a></li>" % (Bands.viewChaser, band, Bands.getBand(band))

	#def toChaserHTML(self, band):
	#	self.toHTML(self.viewChaser, band)

	#def toHTML(self, view):
	#	for key in bandOrder:
	#		self.toHTML(view, key)

	#def toHTML(self, view, band):
	#	print "<a href='grid-squares.py?view=%s&band=%s'>%s</a>" % (view, band, self.bandList[band])

	def isBand(band):
		if band in Bands.bandOrder:
			return True
		else:
			return False

	@staticmethod
	def getBand(band):
		return Bands.bandList[band]

	def addBand(self, band):
		if band in bandOrder:
			bands.append(band)
			return True
		else:
			return False

	@staticmethod
	def getBands(call=None):
		if call == None:
			bands = []
			for row in c.execute("SELECT DISTINCT band FROM gsc"):
				bands.append(row[0])
		else:
			bands = []
			for row in c.execute("SELECT DISTINCT band FROM gsc WHERE callfrom=?", (call, )):
				bands.append(row[0])

	@staticmethod
	def getAllBands():
		return Bands.bandOrder

	@staticmethod
	def getName(band):
		return Bands.bandList[band]

	@staticmethod
	def getBandsHead():
		header = ""
		for band in Bands.getAllBands():
			header = header + "<th class='band'>%s</th>" % (Bands.getName(band))
		return header


class Call(object):
	""" Object for aceessing callsigns and callsign data
	"""

	call = ""

	def __init__(self, callsign):
		self.call = callsign

	@staticmethod
	def getCalls(band=0):
		calls = []
		if band == 0:
			# XXX needs to be fixed to sort for chaser and activator
			for row in c.execute("SELECT callfrom, COUNT(*) FROM gsc GROUP BY callfrom ORDER BY COUNT(*) DESC"):
				calls.append(row[0])
		else:
			for row in c.execute("SELECT callfrom, COUNT(*) FROM gsc WHERE band=? GROUP BY callfrom ORDER BY COUNT(*) DESC", (band, )):
				calls.append(row[0])
		return calls

	@staticmethod
	def callHTML(call):
		return "<a href='%s?view=call&call=%s'>%s</a>" % (myname, call, call)

	def getBandChaseStats(self):
		stats = []
		for band in Bands.getAllBands():
			c.execute("SELECT COUNT(DISTINCT(gridto)) FROM gsc WHERE callfrom=? AND band=?", (self.call, band))
			stats.append(c.fetchone()[0])
		return stats

	def getBandActivStats(self):
		stats = []
		for band in Bands.getAllBands():
			c.execute("SELECT COUNT(DISTINCT(gridfrom)) FROM gsc WHERE callfrom=? AND band=?", (self.call, band))
			stats.append(c.fetchone()[0])
		return stats

# debug display of log
def showLog():
	print "<header>Full Log</header>"
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr><th>From</th><th>Grid</th><th>To</th><th>Grid</th><th>band</th><th>mode</th></tr>"

	for row in c.execute("SELECT callfrom, gridfrom, callto, gridto, band, mode FROM gsc"):
		print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (Call.callHTML(row[0]), row[1], row[2], row[3], Bands.getBand(str(row[4])), row[5])
	print "</table></article>"

def showBandChaser(band):
	print "<header>Chaser Leaderboard for %s</header>" % (Bands.getBand(band))
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr><th>Callsign</th><th class='band'>Grids</th></tr>"
	#try:
	calls = Call.getCalls(band)

	for call in calls:
		c.execute("SELECT COUNT(DISTINCT(gridto)) FROM gsc WHERE band=? AND callfrom=?", (band, call))
		print "<tr><td>%s</td><td class='band'>%s</td></tr>" % (Call.callHTML(call), c.fetchone()[0])
	print "</table></article>"

def showBandActivator(band):
	print "<header>Activator Leaderboard for %s</header>" % (Bands.getBand(band))
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr><th>Callsign</th><th class='band'>Grids</th></tr>"

	calls = Call.getCalls(band)

	for call in calls:
		c.execute("SELECT COUNT(DISTINCT(gridfrom)) FROM gsc WHERE band=? AND callfrom=?", (band, call))
		print "<tr><td>%s</td><td class='band'>%s</td></tr>" % (Call.callHTML(call), c.fetchone()[0])
	print "</table></article>"

def showChaser():
	print "<header>Chaser Leaderboard</header>"
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr><th>Callsign</th><th class='band'>Grids</th></tr>"

	calls = Call.getCalls()

	for call in calls:
		c.execute("SELECT COUNT(DISTINCT(gridto)) FROM gsc WHERE callfrom=?", (call, ))
		print "<tr><td>%s</td><td>%s</td></tr>" % (Call.callHTML(call), c.fetchone()[0])
	print "</table></article>"

def showActivator():
	print "<header>Activator Leaderboard</header>"
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr><th>Callsign</th><th class='band'>Grids</th></tr>"

	calls = Call.getCalls()

	for call in calls:
		c.execute("SELECT COUNT(DISTINCT(gridfrom)) FROM gsc WHERE callfrom=?", (call, ))
		print "<tr><td>%s</td><td>%s</td></tr>" % (Call.callHTML(call), c.fetchone()[0])
	print "</table></article>"

def showCallStats(call):
	print "<header>Callsign Stats</header>"
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr><th>Chase/Act</th>"
	print Bands.getBandsHead()
	print "<th class='band'>Total</th></tr>"

	callObject = Call(call)

	total = 0
	print "<tr><td>Chaser</td>"
	for band in callObject.getBandChaseStats():
		total = total + int(band)
		print "<td class='band'>%s</td>" % (band)
	print "<td class='band'>%s</td></tr>" % (total)
	print "</tr>"

	total = 0
	print "<tr><td>Activator</td>"
	for band in callObject.getBandActivStats():
		total = total + int(band)
		print "<td class='band'>%s</td>" % (band)
	print "<td class='band'>%s</td></tr>" % (total)
	print "</tr>"

	print "</table></article>"

def showChaseGrid():
	print "<header>Chaser Grid</header>"
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr>"
	print "<th>Callsign</th>"

	print Bands.getBandsHead()

	print "<th class='band'>Total</th></tr>"
	for call in Call.getCalls():
		callObject = Call(call)
		total = 0
		print "<tr><td>%s</td>" % (Call.callHTML(call))
		for band in callObject.getBandChaseStats():
			total = total + int(band)
			print "<td class='band'>%s</td>" % (band)
		print "<td class='band'>%s</td></tr>" % (total)

	print "</table></article>"

def showActivGrid():
	print "<header>Activator Grid</header>"
	navHTML()
	print "<article class='article'>"
	print "<table border='1'>"
	print "<tr>"
	print "<th>Callsign</th>"

	print Bands.getBandsHead()

	print "<th class='band'>Total</th></tr>"
	for call in Call.getCalls():
		callObject = Call(call)
		total = 0
		print "<tr><td>%s</td>" % (Call.callHTML(call))
		for band in callObject.getBandActivStats():
			total = total + int(band)
			print "<td class='band'>%s</td>" % (band)
		print "<td class='band'>%s</td></tr>" % (total)

	print "</table></article>"

def navHTML():
	# different display options
	print "<nav class='nav'>"
	print "<div>Leaderboards:</div>"
	print "<ul><li><a href='grid-squares.py?view=chaser'>Chaser</a></li>"
	Bands.chaserHTML()
	print "</ul>"
	print "<ul><li><a href='grid-squares.py?view=activator'>Activator</a></li>"
	Bands.activatorHTML()
	print "</ul>"
	print "<ul><li><a href='grid-squares.py'>Home</a></li><li><a href='grid-squares.py?view=all'>Show Full Log</a></li>"
	print "</ul>"
	print "</nav>"

print "<div class='flex-container'>"
if "view" in form:
	if form["view"].value == Bands.viewChaser:
		showBandChaser(form["band"].value)
	elif form["view"].value == Bands.viewActivator:
		showBandActivator(form["band"].value)
	elif form["view"].value == "all":
		showLog()
	elif form["view"].value == "chaser":
		showChaseGrid()
	elif form["view"].value == "activator":
		showActivGrid()
	elif form["view"].value == "call":
		showCallStats(form["call"].value)
else:
	showChaseGrid()
print "<footer>Copyright &copy; Marcus B</footer>"
print "</div>"

conn.commit()
conn.close()

print "</body></html>"


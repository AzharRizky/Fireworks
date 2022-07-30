from ansi import cursor
from ansi.color import fg, fx
import numpy as np
import math
import random
import time
import threading

# constant for Cartesian
CARTESIAN_X_0 = 40	# screen coordinates of x axis cartesian
CARTESIAN_Y_0 = 11	# screen coordinates of y axis cartesian 
YRATIO = 1/3		# Y ratio to make it proportional to x width
MAXWIDTH = 25		# maximum width of particles explode


# constant for LargeDigits
# change X with chr(0x2588)
MAPDIGITS = '''
.XX....X..XXXX.XXXX.X..X.XXXX..XXX.XXXX.XXXX.XXXX..........
X..X..XX.....X....X.X..X.X....X.......X.X..X.X..X..XX......
X..X...X....X...XXX.XXXX.XXXX.XXXX....X..XX..XXXX..........
X..X...X..X.......X....X....X.X..X...X..X..X....X..XX......
.XX..XXXX.XXXX.XXXX....X.XXXX.XXXX..X...XXXX.XXX...........
'''
KEYDIGITS = '0123456789: '

class LargeDigits:

	aMapDigits = dict()
	posDigit = lambda self, i: i * 5

	def __init__(self):
		for d in MAPDIGITS.split('\n'):
			newd = d.replace(' ', '')
			newd = newd.replace('X', chr(0x2588))
			newd = newd.replace('.', ' ')
			if len(d)==0: continue
			for i,c in enumerate(KEYDIGITS):
				#print('i,c=',i,c)
				if self.aMapDigits.get(c,None) is None:
					self.aMapDigits[c] = []
				s = self.posDigit(i)
				self.aMapDigits[c].append(newd[s:s+5])
		#print(self.aMapDigits)

	def print(self, s, *, row=None, col=None):
		txt = []
		for c in s:
			txt.append(self.aMapDigits.get(c,''))

		#print('txt=',txt)
		for i in range(len(txt[0])):
			if all([row, col]):
				print(cursor.goto(row+i, col), end='')
			for c in txt:
				print(c[i], end=' ')
			print()
			

class Firework:

	delta_xy = (0,0)

	def fire(self):
		# start to fire
		self.shoot()
		self.explode()

	def shoot(self):
		# shoot fireworks

		# target
		dx = random.gauss(0, 12)
		dy = random.gauss(0, 3.5)
		self.delta_xy = (dx, dy)

		xfrom = 1
		yfrom = 1
		x0, y0 = cartesianToScreen((0,0), self.delta_xy)
		m = (yfrom - y0)/(xfrom - x0)
		for c in [chr(0x387), ' ']:
			x = xfrom
			while x < x0:
				y = m * x
				print(cursor.goto(round(y), round(x)), end='')
				print(c, end='', flush=True)
				x += 1.3
				time.sleep(0.01)

	def explode(self):
		# explode fireworks
		th = []
		for deg in range(0, 360, random.sample(range(20,50,5), 1)[0]):
			t = threading.Thread(target=self.particle, args=(deg,))
			t.start()
			th.append(t)

		for t in th:
			t.join()

	def particle(self, angle=0):
		# show particles

		maxwidth = MAXWIDTH * random.gauss(0.9,0.15)
		xpos = self.scatter(teta=angle, maxwidth=maxwidth)
		#print(xpos)

		for c in [chr(0x25A1), chr(0x25A0), chr(0x2591), ' ']:
			for i, (x,y) in enumerate(xpos):
				x = round(x)
				y = round(y)
				if i < 2/5 * maxwidth:
					print(fg.red, end='')
				elif i < 3/5 * maxwidth:
					print(fg.yellow, end='')
				else:
					print(fg.white, end='')
				xt, yt = cartesianToScreen((x,y), self.delta_xy)
				#print(f'## {yt} ##')
				print(cursor.goto(yt, xt),end='')
				print(c, end='', flush=True)
				print(fx.reset,end='')
				time.sleep(0.02)
			time.sleep(0.3)

	def scatter(self, *, tmax=20, maxwidth=20, teta=0):
		# calculate position of particle at time t

		# matrix of rotation based on teta angle
		teta = math.radians(teta)
		mrotate = np.matrix([[math.cos(teta), -math.sin(teta)],
					[math.sin(teta), math.cos(teta)]])

		# assume particle explode along x axis
		# x distance is proportional to maxwidth
		xpos = []
		for t in range(tmax, 0, -1):
			x = 5 * t**2
			if t == tmax: xmax = x
			xpos.append((int(x / xmax * maxwidth), 0))
		xpos.reverse()

		# then rotate
		mxpos = np.matrix(xpos) * mrotate
		return mxpos.tolist()


def clearScreen():
	print(fx.reset, 
		cursor.erase(2),
		cursor.goto(1,1), end='', flush=True)

def cartesianToScreen( coord, delta=(0,0)):
	x, y = coord
	dx, dy = delta
	xr = round(CARTESIAN_X_0 + (x + dx) )
	yr = round(CARTESIAN_Y_0 - (y + dy)*YRATIO )
	return (xr, yr)
	

# main program -----------------------------------
clearScreen()

nextYear = time.localtime().tm_year+1
print('CountDown to NewYear', nextYear)

print('\nInput berapa detik lagi ke tahun baru, ')
print('atau [Enter] blank untuk hitung otomatis.')
inp = input('> ')

print('\nBerapa kembang api yang akan diluncurkan?')
nfire = int(input('> '))


if inp == '':
	tYEnd = time.mktime((nextYear,1,1,0,0,0,0,0,0))
	inputCountDown = round(tYEnd - time.time())
else:
	inputCountDown = int(inp)
	tYEnd = round(time.time() + inputCountDown)

if inputCountDown > 60*60*24: # more than 1 day
	print('Tahun baru masih lama. Oleh karena itu yang')
	print('akan ditampilkan adalah jam bukan countdown.')
	input('-- Enter untuk lanjut')


# display countdown waiting for new year..
clearScreen()
print('CountDown to NewYear', nextYear)

labelCountDown = LargeDigits()
prev = ''
while True :
	delta = int(round(tYEnd - time.time()))
	if delta < 0: break

	if delta > 60*60*24:
		prev = 'clock'
		timestr = time.strftime('%H:%M:%S')
	else:
		timestr = str(delta)
		# if previouse mode is clock
		if prev == 'clock':
			clearScreen()
			prev = ''

	labelCountDown.print(f'{timestr} ', row=5, col=20)
	time.sleep(0.1)	


# start firework -------
fwork = Firework()

clearScreen()
thfw = []
while True:
	f = Firework()
	fw = threading.Thread(target=f.fire)
	fw.start()
	thfw.append(fw)
	time.sleep(random.randint(1,3))
	if len(thfw) > nfire:
		break

for f in thfw:
	f.join()

clearScreen()
print(cursor.goto(CARTESIAN_Y_0, CARTESIAN_X_0-10), end='')
print('SELAMAT TAHUN BARU', nextYear)
input()

exit()


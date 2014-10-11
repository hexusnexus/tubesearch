#!/usr/bin/python

import subprocess, sys, os, re
import time, threading
import tempfile
from glob import glob

import Tkinter
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
import urllib2


class video:
	name = ''
	description = ''
	thumbnail = ''
	duration = ''
	filename = ''
	number = 0

class myTimer():
   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = threading.Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = threading.Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

class button_press:
	def __init__(self, address, filename):
		self.address = address
		self.filename = ""
		self.file_exists = False
		self.proc = None
		self.init_filename = filename
		self.auto = False
	def download(self):
		if not self.filename:
			print "Downloading from " + self.address + "..."
			self.proc = subprocess.Popen(['youtube-dl', self.address, '-f', '5/18/22'], stdout=subprocess.PIPE, shell=False)
			self.filename = self.init_filename
	def play(self):
		if self.file_exists:
			print "Playing " + self.filename + "..."
			#video file has problems with quotes?
			subprocess.Popen(['vlc', self.filename], stdout=subprocess.PIPE, shell=False)
		else:
			print "File can't be played yet."
	def autoplay(self):
		self.download()
		self.auto = True
	

def rm_dup(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def click(event):
    w = event.widget
    x, y = event.x, event.y
    tags = w.tag_names("@%d,%d" % (x, y))
    for t in tags:
        if t.startswith("href:"):
	    subprocess.Popen(['firefox', t[5:]], stdout=subprocess.PIPE, shell=False)
            break
    else:
        print "clicked without href"
    return "break"


def show_hand_cursor(event):
    event.widget.configure(cursor="hand1")
def show_arrow_cursor(event):
    event.widget.configure(cursor="xterm")
    
def check_downloads():
	for i in range(len(button_cl)):
		if button_cl[i].filename:
			if os.path.isfile(button_cl[i].filename) and not button_cl[i].file_exists:
				print "Done downloading " + button_cl[i].filename
				button_cl[i].file_exists = True
				if button_cl[i].auto:
					button_cl[i].play()

temp_directory = tempfile.gettempdir()

links = []
search_terms = raw_input("Search YouTube: ")
print "Searching..."
search = re.sub(r"\s+", '+', search_terms)
pageFile = urllib2.urlopen("https://duckduckgo.com/html/?q=site%3Ayoutube.com+"+search)
pageHtml = pageFile.read()
pageFile.close()
soup = BeautifulSoup("".join(pageHtml))

for tag in soup.findAll('a', href=True):
    links.append(tag['href'])

temp_nf = [value for value in links if 'http://www.youtube.com' in value and 'watch?v' in value]
temp_nodup = rm_dup(temp_nf)
links = temp_nodup[0:10]


Video = []
print "Downloading video info..."
temp_links = links
enum = 0
temp_proc = []
for link in temp_links:
	temp_proc.append(subprocess.Popen(['youtube-dl', '-e', '--write-thumbnail', '--get-description', '--get-duration', '--get-filename', link, '-f', '5/18/22'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False))
	enum += 1

for i in range(enum):
	output, error = temp_proc[i].communicate()
	if error[:6] == "ERROR:":  #list is now less than 10 links
		links.pop(i)
		continue
	info = output.split('\n')
	temp_nf = [value for value in info if value != '']
	info = temp_nf
	next_vid = video()
	next_vid.name = info[0]
	next_vid.thumbnail = glob(info[0]+'*.jpg')
	next_vid.description = info[1]
	next_vid.filename = info[-2]
	next_vid.duration = info[-1]
	Video.append(next_vid)

print "Done."
	
app = Tkinter.Tk()
app.title('Tube Search')
text = Tkinter.Text(app)
scrollbar = Tkinter.Scrollbar(app, command=text.yview)
scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
text.config(yscrollcommand=scrollbar.set)
text.pack()



text.tag_config("a", foreground="blue", underline=1)
text.tag_bind("a", "<Enter>", show_hand_cursor)
text.tag_bind("a", "<Leave>", show_arrow_cursor)
text.tag_bind("a", "<Button-1>", click)

size = 128, 128
img = []
youtube_button = []
download_button = []
play_button = []
autoplay_button = []
button_cl = []

i = 0
text.tag_config("title", font=('times', 15, 'bold'))
text.tag_config("duration", font=('times', 10, 'bold'))


for about in Video:
	text.insert(Tkinter.END, about.name, "title")
	text.insert(Tkinter.END, '\n')
	text.insert(Tkinter.END, about.description)
	text.insert(Tkinter.END, '\n')
	if about.thumbnail:
		if len(about.thumbnail) > 1:
			about.thumbnail = about.thumbnail[:1]
		im = Image.open(''.join(about.thumbnail))
		im.thumbnail(size, Image.ANTIALIAS)
		img.append(ImageTk.PhotoImage(im))
		text.image_create(Tkinter.END, image = img[-1])
		text.insert(Tkinter.END, '\n')
	link = links[i]
	text.insert(Tkinter.END, link, ("a", "href:"+link))
	text.insert(Tkinter.END, "\n")
	text.insert(Tkinter.END, about.duration, "duration")
	text.insert(Tkinter.END, " ")
	button_cl.append(button_press(link, about.filename))
	download_button.append(Tkinter.Button(text, text="Download", command=button_cl[-1].download, cursor="left_ptr"))
	play_button.append(Tkinter.Button(text, text="Play", command=button_cl[-1].play, cursor="left_ptr"))
	autoplay_button.append(Tkinter.Button(text, text="Download + Play", command=button_cl[-1].autoplay, cursor="left_ptr"))
	text.window_create(Tkinter.END, window=download_button[i])
	text.insert(Tkinter.END, ' ')
	text.window_create(Tkinter.END, window=play_button[i])
	text.insert(Tkinter.END, ' ')
	text.window_create(Tkinter.END, window=autoplay_button[i])
	text.insert(Tkinter.END, '\n')
	text.insert(Tkinter.END, '\n')
	i += 1
					
timer = myTimer(2, check_downloads)
timer.start()	
app.mainloop()

#remove thumbanils from system
r = glob('*.jpg')
for i in r:
   os.remove(i)

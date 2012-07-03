#!/usr/bin/env python

import os,sys
from pylab import *
from numpy import *

from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib
import math
import string

class AnnoteFinder:
  """
  callback for matplotlib to display an annotation when points are clicked on.  The
  point which is closest to the click and within xtol and ytol is identified.

  Register this function like this:

  scatter(xdata, ydata)
  af = AnnoteFinder(xdata, ydata, annotes)
  connect('button_press_event', af)
  """

  def __init__(self, xdata, ydata, annotes, axis=None, xtol=None, ytol=None):
    self.data = zip(xdata, ydata, annotes)
    if xtol is None:
      xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
    if ytol is None:
      ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
    self.xtol = xtol
    self.ytol = ytol
    if axis is None:
      self.axis = gca()
    else:
      self.axis= axis
    self.drawnAnnotations = {}
    self.links = []

  def distance(self, x1, x2, y1, y2):
    """
    return the distance between two points
    """
    return(math.sqrt( (x1 - x2)**2 + (y1 - y2)**2 ))

  def __call__(self, event):
    '''
    this is where you would do things related to the type of event
    '''
    if event.inaxes:
      clickX = event.xdata
      clickY = event.ydata
      if (self.axis is None) or (self.axis==event.inaxes):
        annotes = []
        for x,y,a in self.data:
          if  (clickX-self.xtol < x < clickX+self.xtol) and  (clickY-self.ytol < y < clickY+self.ytol) :
            annotes.append((self.distance(x,clickX,y,clickY),x,y, a) )
        if annotes:
          annotes.sort()
          distance, x, y, annote = annotes[0]

          self.HandleEvent(event, x, y, annote)

          #self.drawAnnote(event.inaxes, x, y, annote)
          #for l in self.links:
            #l.drawSpecificAnnote(annote)

  def HandleEvent(self,event,x,y,annote):

    if isinstance(event,matplotlib.backend_bases.MouseEvent):
      # plot the label on the figure
      self.drawAnnote(event.inaxes, x, y, annote)
    elif isinstance(event,matplotlib.backend_bases.KeyEvent):

      if event.key in ('h','H'):
        self.Hpressed(annote)
      elif event.key in ('c','C'):
        self.Cpressed(annote)

  def Hpressed(self,annote):
    #print the heat of formation in the terminal
    f = open('%s/energy' % annote)
    hf = float(f.readline())
    f.close()
    print '%5i Heat of Formation = %1.3f eV' % (annote,hf)

  def Cpressed(self,annote):
    #print configuration
    f = open('%s/str.out' % annote)
    for line in f:
      print line.strip()
    f.close()


  def drawAnnote(self, axis, x, y, annote):
    """
    Draw the annotation on the plot

    axis is the axis to draw the annote on.
    x,y are the coordinates of where the annotation will be drawn
    annote is the piece of data that is associated with the point found at x,y

    we first see if the annotation has already been drawn, and remove it if it has
    """


    if self.drawnAnnotations.has_key((x,y)):
      markers = self.drawnAnnotations[(x,y)]
      for m in markers:
        m.set_visible(not m.get_visible())
      self.axis.figure.canvas.draw()
      # delete the record that it was drawn
      del self.drawnAnnotations[(x,y)]

    else:
      ''' this is where the string gets put on the graph.
      I want to print some stuff to stdout too. since the annote is the configuration
      I can print the file contents
      '''
      t = axis.text(x,y, " %s"%(annote), )
      m = axis.scatter([x],[y], marker='d', c='r', zorder=100)
      self.drawnAnnotations[(x,y)] =(t,m)
      self.axis.figure.canvas.draw()

  def drawSpecificAnnote(self, annote):
    annotesToDraw = [(x,y,a) for x,y,a in self.data if a==annote]
    for x,y,a in annotesToDraw:
      self.drawAnnote(self.axis, x, y, a)



##################################################################
##################################################################
##################################################################


occupants = []
f = open('atoms.out','r')
for line in f:
    if len(line) > 0:
        occupant = line.strip()
        occupants.append(occupant)
f.close()

#these commands refresh some of the files and give status
os.system('cat maps.log')

# this file contains the results of the fit
#each line contains this information
#'concentration energy fittedenergy error weight index'

f = open('fit.out','r')
data = f.readlines()
f.close()

concentration=[]
energy=[]
fitenergy = []
error = []
weight = []
index = []
for line in data:
    ca,cb,cc,e,fe,err,w,i = line.split()
    concentration.append([float(x) for x in (ca,cb,cc)])
    energy.append(float(e))
    fitenergy.append(float(fe))
    error.append(float(err))
    weight.append(float(w))
    index.append(int(i))
concentration = array(concentration)

# get the Groundstate curve
# concentration energy fitenergy,index
f = open('gs.out','r')
lines = f.readlines()
f.close()

gs_concentration,gs_energy,gs_fitenergy,gs_index = [],[],[],[]
for line in lines:
    ca,cb,cc,e,fe,u,i = line.split()
    gs_concentration.append([float(x) for x in [ca,cb,cc]])
    gs_energy.append(float(e))
    gs_fitenergy.append(float(fe))
    gs_index.append(int(i))
gs_concentration = array(gs_concentration)


# find new predicted groundstates
if os.path.exists('newgs.out'): os.unlink('newgs.out')
os.system('grep g predstr.out > newgs.out')

# check if there are any predicted new groundstates
if os.path.exists('newgs.out'):
    f = open('newgs.out','r')
    lines = f.readlines()
    f.close()
else:
    lines = []

ngs_concentration, ngs_predictedenergy, ngs_index = [],[],[]
if len(lines) != 0:
    for line in lines:
        ca,cb,cc,preden,ind,stat = line.split()
        ngs_concentration.append([float(x) for x in (ca,cb,cc)])
        ngs_predictedenergy.append(float(preden))
        if ind != '?':
            ngs_index.append(int(ind))
        else:
            ngs_index.append(-1)
ngs_concentration = array(ngs_concentration)

'''
make a list of data to plot, this makes it easy to conditionally add
the new gs if it exists.
'''

figure(1)
plot(concentration[:,0],energy,
     'ro',label="DFT Energies")
plot(gs_concentration[:,0],gs_energy,
     'ko-',label='Known Ground State',markersize=4,
     markerfacecolor='blue',markeredgecolor='black')

if len(ngs_concentration) > 0:
    plot(ngs_concentration[:,0],ngs_predictedenergy,
         'ks',label='Predicted GroundStates')
    af_ngs = AnnoteFinder(ngs_concentration[:,0],ngs_predictedenergy,ngs_index)
    connect('button_press_event', af_ngs)

xlabel('x_%s' % occupants[1])
ylabel('Heat Of Formation (eV/atom)')
title('Calculated energies')
legend(loc='best')

af = AnnoteFinder(concentration[:,0],energy,index)
connect('button_press_event', af)
connect('key_press_event', af)


figure(2)
plot(range(len(error)),error,'bo-')
xlabel('Configuration')
ylabel('Fit error (eV)')
title('Residual error of the fit')
ax = gca()
ax.yaxis.set_major_formatter(FormatStrFormatter('%1.3f'))


af = AnnoteFinder(range(len(error)),error,index)
connect('button_press_event', af)

# examine trends in the eci
'''
getclus -e | grep -v '^0' | grep -v '^1' >! clusinfo.out

from grep page
       -v, --invert-match
              Invert the sense of matching, to select non-matching lines.

Syntax: getclus [-e]
extracts, from clusters.out, the cluster sizes, lengths an multiplicities
if -e is specified, also prints eci from eci.out

this gets the clusters that do not start with 0 or 1. in otherwords,
it avoids the point and empty cluster. otherwise, it creates a file
called clusinfo.out that contains the cluster size, length, multiplicity
and eci from clusters.out and eci.out

'''
if os.path.exists('clusinfo.out'): os.unlink('clusinfo.out')
os.system('''getclus.py clusters.out | grep -v '^0' | grep -v '^1' > clusinfo.out''')

cluseci = []
clusradii = []
f = open('clusinfo.out','r')
for line in f:
    if line.startswith('#'):
        continue
    try:
        n,radius,df,eci = line.split()
    except ValueError:
        break
    cluseci.append(float(eci))
    clusradii.append(float(radius))
f.close()


figure(3)
plot(clusradii,cluseci,'ko')
xlabel('Cluster radius')
ylabel('ECI')
title('ECI vs. cluster radius')
show()


#raw_input("Enter to continue")





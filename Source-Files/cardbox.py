#!/usr/bin/python

# cardboard box maker
# 
# this one uses a really weird recursive logo style weld paradigm
# don't ask me how it works , i'm not sure it does yet 
# it does ! 
# 20090414
# Simon Kirkby
# tigger@interthingy.com
# GPL
# posted on thingiverse.com

import os,string,math
from sdxf import *
from optparse import OptionParser
import ConfigParser

# global draw cursor pos
global cx,cy,count,cstack
cx = 0 
cy = 0
count = 0
cstack = []
# global option 
global option

def pushc():
	global cstack,cx,xy
	cstack.append((cx,cy))

def popc():
	global cstack,cx,cy
	(cx,cy) = cstack.pop()

class box:
	" default box class " 
	def __init__(self,opt):
		self.opt = opt
		self.length = opt.length
		self.width = opt.width
		self.depth = opt.depth
		
	def set_root(self,face):
		self.root_face = face

	def build(self):
		" override this to build your own box"
		x = self.length
		y = self.width
		z = self.depth
		p = option.proportion
		print 'make box'
		print x,y,z
		" testing basic box"

		# basic sides
		bottom = face('bottom',x,y)
		self.set_root(bottom)
		front = face('front',x,z)
		back = face('back',x,z)
		left = face('left',z,y)
		right = face('right',z,y)
		top = face('top',x,y)

		# tabs
		flt = fold_tab('front_left tab',y*p,z)
		frt = fold_tab('front_right_tab',y*p,z)
		blt = fold_tab('back_left_tab',y*p,z)
		brt = fold_tab('back_right_tab',y*p,z)
		
		# covers
		lcover = face('left_cover',z,y)
		rcover = face('right_cover',z,y)
		fcover = face('fron_cover',x,z)
		
		# tuck tops 
		ttuck = tuck('top_tuck',x,z*p)
		ttuck.set_short_edge(2)
		ltuck = tuck('left_tuck',z*p,y)
		ltuck.set_short_edge(3)
		rtuck = tuck('right_tuck',z*p,y)
		rtuck.set_short_edge(1)

		# make the special edges
		rcover.edges[1] = tab(1,0,y)
		lcover.edges[3] = tab(3,0,-y)
		fcover.edges[0] = tab(0,x,0)	
		bottom.edges[1] = slot(1,0,y)
		bottom.edges[3] = slot(3,0,-y)
		bottom.edges[0] = slot(0,x,0)

		# chamfer the tabs
		flt.set_chamfer_edge(3)
		frt.set_chamfer_edge(0)
		blt.set_chamfer_edge(2)
		brt.set_chamfer_edge(1)

		# now to weld all the panels together
		bottom.weld(0,front)
		bottom.weld(1,right)
		bottom.weld(2,back)
		bottom.weld(3,left)
		back.weld(2,top)

		# weld on the tabs
		front.weld(1,frt)
		front.weld(3,flt)
		back.weld(1,brt)
		back.weld(3,blt)

		# weld covers
		left.weld(3,lcover)
		right.weld(1,rcover)
		front.weld(0,fcover)

		# weld the tucks
		top.weld(1,rtuck)
		top.weld(2,ttuck)
		top.weld(3,ltuck)

	def gen(self,d):
		self.root_face.gen(d)

class box2(box):
	def build(self):
                x = self.length
                y = self.width
                z = self.depth
		p = option.proportion
                print 'make box'
                print x,y,z
                " testing basic box"
                # basic sides
                bottom = face('bottom',x,y)
                self.set_root(bottom)
                front = face('front',x,z)
                back = face('back',x,z)
                left = face('left',z,y)
                right = face('right',z,y)

                # tabs
                flt = fold_tab('front_left tab',y*p,z)
                frt = fold_tab('front_right_tab',y*p,z)
                blt = fold_tab('back_left_tab',y*p,z)
                brt = fold_tab('back_right_tab',y*p,z)

		# chamfer the tabs
		flt.set_chamfer_edge(3)
		frt.set_chamfer_edge(0)
		blt.set_chamfer_edge(2)
		brt.set_chamfer_edge(1)

                # covers
                lcover = face('left_cover',z,y)
                rcover = face('right_cover',z,y)
                fcover = face('fron_cover',x,z)
                bcover = face('back_cover',x,z)

                # tuck tops 
                ttuck = tuck('top_tuck',x,z*p)
                ttuck.set_short_edge(2)
                ltuck = tuck('left_tuck',z*p,y)
                ltuck.set_short_edge(3)
                rtuck = tuck('right_tuck',z*p,y)
                rtuck.set_short_edge(1)

                # make the special edges
                rcover.edges[1] = tab(1,0,y)
                lcover.edges[3] = tab(3,0,-y)
                fcover.edges[0] = tab(0,x,0)   
                bcover.edges[2] = tab(2,-x,0)   

                bottom.edges[0] = slot(0,x,0)
                bottom.edges[1] = slot(1,0,y)
                bottom.edges[2] = slot(2,-x,0)
                bottom.edges[3] = slot(3,0,-y)

                # now to weld all the panels together
                bottom.weld(0,front)
                bottom.weld(1,right)
                bottom.weld(2,back)
                bottom.weld(3,left)

                # weld on the tabs
                front.weld(1,frt)
                front.weld(3,flt)
                back.weld(1,brt)
                back.weld(3,blt)

                # weld covers
                left.weld(3,lcover)
                right.weld(1,rcover)
                front.weld(0,fcover)
		back.weld(2,bcover)



class face:
	# faces are generated anticlockwise from bottom left
	# basic square face
	def __init__(self,name,x,y):
		self.name = name
		self.x = x
		self.y = y
		self.edges = []
		self.inset = option.inset
		self.edges.append(edge(0,x,0))
		self.edges.append(edge(1,0,y))
		self.edges.append(edge(2,-x,0))
		self.edges.append(edge(3,0,-y))

	def weld(self,num,face):
		edge = self.edges[num]
		print 'welding edge '+str(num) + ' of '+self.name
		if num == 0:
			face.edges[2].done = 1 
		if num == 1:
			face.edges[3].done = 1 
		if num == 2:
			face.edges[0].done = 1
		if num == 3:
			face.edges[1].done = 1
		edge.type = 'FOLDS'
		edge.child = face
	
	def gen(self,d):
		global cx,cy
		print '\tgen face ' + self.name + ' ('+str(self.x)+','+str(self.y)+')'
                #d.append(Text(self.name,point=(cx+10,cy+10,0),layer="TEXT",height=5))
		#d.append(Circle(center=(cx,cy),radius=3,layer="CONSTRUCTION"))
		for i in self.edges:
			i.gen(d)	
		print '\tend face '+ self.name

class tuck(face):
	def __init__(self,name,x,y):
		face.__init__(self,name,x,y)
		
	def set_short_edge(self,number):
		i = option.inset
		x = self.x
		y = self.y
		self.edges = []
		if number == 1:
			self.edges.append(edge(0,x,i))
			self.edges.append(edge(1,0,y-2*i))
			self.edges.append(edge(2,-x,i))
			self.edges.append(edge(3,0,-y))
		if number == 2:
			self.edges.append(edge(0,x,0))
			self.edges.append(edge(1,-i,y))
			self.edges.append(edge(2,-x+2*i,0))
			self.edges.append(edge(3,-i,-y))
		if number == 3:
			self.edges.append(edge(0,x,-i))
			self.edges.append(edge(1,0,y))
			self.edges.append(edge(2,-x,-i))
			self.edges.append(edge(3,0,-y+2*i))
			self.y = self.y - i
			
		
class fold_tab(face):
	def __init__(self,name,x,y):
		face.__init__(self,name,x,y)
	
	def set_chamfer_edge(self,number):
		x = self.x
		y = self.y
		c = option.chamfer
		if number == 0:
			self.edges[0] = chamfer(0,x,0)
			self.edges[1] = chamfer(1,0,y)
			self.edges[1].cutaway = 1
		if number == 1:
			self.edges[1] = chamfer(1,0,y)
			self.edges[2] = chamfer(2,-x,0)
			self.edges[2].cutaway = 1
		if number == 2:
			self.edges[2] = chamfer(2,-x,0)
			self.edges[3] = chamfer(3,0,-y)
			self.edges[3].cutaway = 1
		if number == 3:
			self.edges[3] = chamfer(3,0,-y)
			self.edges[0] = chamfer(0,x,0)
			self.edges[0].cutaway = 1

class edge:
	def __init__(self,number,distx,disty):
		# 0 = bottom edge
		# 1 = right edge 
		# 2 = top edge
		# 3 = left edge
		self.number = number
		self.distx = distx
		self.disty = disty
		self.child = None
		self.type = 'CUTS'
		self.done = 0 
		
	def gen_child(self,num,d):
		global cx,cy
		# store the cursor position
		pushc()
		if self.child != None:
			# move to deal with the child offset
			if num == 0:
				cy = cy - self.child.y
			#if num == 1:
			#	pass
			if num == 2:
				cx = cx - self.child.x
			if num == 3:
				cx = cx - self.child.x 
				cy = cy - self.child.y 
			self.child.gen(d)
		# move back to original position
		popc()
	
	# functions to override for special edges
	def side0(self,d,type,x1,y1,x2,y2):
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))
		
	def side1(self,d,type,x1,y1,x2,y2):
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))

	def side2(self,d,type,x1,y1,x2,y2):
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))

	def side3(self,d,type,x1,y1,x2,y2):
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))

	def gen(self,d):
		global cx,cy,count
		count = count + 1 
		n = self.number
		distx = self.distx
		disty = self.disty
		type = self.type
		#cs = str(count) + ':' +str(self.number)+':'+str(self.distx)
                #d.append(Text(cs,point=(cx,cy,0),layer="TEXT",height=5))
		if self.done == 0:
			self.done = 1
			self.gen_child(n,d)
			print '\t\tgen edge '+ '= ' + str(self.number)+ ' x' + str(distx)+ ' y'+str(disty) ,
			if n == 0:
				print 'bottom'
				self.side0(d,type,cx,cy,cx+distx,cy+disty)
				cx = cx + distx
				cy = cy + disty
			if n == 1:
				print 'right'
				self.side1(d,type,cx,cy,cx+distx,cy+disty)
				cx = cx + distx
				cy = cy + disty
			if n == 2:
				print 'top'
				self.side2(d,type,cx,cy,cx+distx,cy+disty)
				cx = cx + distx
				cy = cy + disty
			if n == 3:
				print 'left'
				self.side3(d,type,cx,cy,cx+distx,cy+disty)
				cx = cx + distx
				cy = cy + disty
		else:
			print '\t\t',
			if n == 0:
				print 'skip bottom'
				cx = cx + distx
				cy = cy + disty
			if n == 1:
				print 'skip right'
				cx = cx + distx
				cy = cy + disty
			if n == 2:
				print 'skip top'
				cx = cx + distx
				cy = cy + disty
			if n == 3:
				print 'skip left'
				cx = cx + distx
				cy = cy + disty
		
class tab(edge):

	def side0(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		sl = option.slot_length
		hsl = option.slot_length/2.0
		d.append(Line(points=[(x1,y1),(x2/2.0-hsl,y2)],layer=type))
		d.append(Line(points=[(x2/2.0-hsl,y1),(x2/2.0-hsl,y2-t)],layer=type))
		d.append(Line(points=[(x2/2.0-hsl,y1-t),(x2/2.0+hsl,y2-t)],layer=type))
		d.append(Line(points=[(x2/2.0+hsl,y1-t),(x2/2.0+hsl,y2)],layer=type))
		d.append(Line(points=[(x2/2.0+hsl,y1),(x2,y2)],layer=type))

	def side1(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		sl = option.slot_length/2.0
		d.append(Line(points=[(x1,y1),(x2,y1+y2/2.0-sl)],layer=type))
		d.append(Line(points=[(x1,y1+y2/2.0-sl),(x2+t,y1+y2/2.0-sl)],layer=type))
		d.append(Line(points=[(x1+t,y1+y2/2.0-sl),(x2+t,y2/2.0+sl)],layer=type))
		d.append(Line(points=[(x1+t,y2/2.0+sl),(x2,y2/2.0+sl)],layer=type))
		d.append(Line(points=[(x1,y2/2+sl),(x2,y2)],layer=type))

	def side2(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		sl = option.slot_length
		hsl = option.slot_length/2.0
		d.append(Line(points=[(x1,y1),(x1/2.0+hsl,y2)],layer=type))
		d.append(Line(points=[(x1/2+hsl,y1),(x1/2.0+hsl,y2+t)],layer=type))
		d.append(Line(points=[(x1/2+hsl,y1+t),(x1/2.0-hsl,y2+t)],layer=type))
		d.append(Line(points=[(x1/2-hsl,y1+t),(x1/2.0-hsl,y2)],layer=type))
		d.append(Line(points=[(x1/2-hsl,y1),(x2,y2)],layer=type))

	def side3(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		hsl = option.slot_length/2.0
		sl = option.slot_length
		d.append(Line(points=[(x1,y1),(x2,y2+y1/2.0+hsl)],layer=type))
		d.append(Line(points=[(x1-t,y2+y1/2.0+hsl),(x2,y2+y1/2.0+hsl)],layer=type))
		d.append(Line(points=[(x1-t,y2+y1/2.0-hsl),(x2-t,y2+y1/2+hsl)],layer=type))
		d.append(Line(points=[(x1,y2+y1/2.0-hsl),(x2-t,y2+y1/2.0-hsl)],layer=type))
		d.append(Line(points=[(x1,y2+y1/2.0-hsl),(x2,y2)],layer=type))

class slot(edge):
	
	def side0(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		sl = option.slot_length
		hsl = option.slot_length/2.0
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))
		d.append(Line(points=[(x2/2.0-hsl,y1),(x2/2.0-hsl,y2+t)],layer="CUTS"))
		d.append(Line(points=[(x2/2.0-hsl,y1+t),(x2/2.0+hsl,y2+t)],layer="CUTS"))
		d.append(Line(points=[(x2/2.0+hsl,y1+t),(x2/2.0+hsl,y2)],layer="CUTS"))

	def side1(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		hsl = option.slot_length/2.0
		sl = option.slot_length
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))
		d.append(Line(points=[(x1-t,y1+y2/2.0-hsl),(x1,y1+y2/2-hsl)],layer="CUTS"))
		d.append(Line(points=[(x1-t,y1+y2/2.0-hsl),(x1-t,y2/2+hsl)],layer="CUTS"))
		d.append(Line(points=[(x1,y2/2.0+hsl),(x1-t,y2/2+hsl)],layer="CUTS"))

	def side2(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		sl = option.slot_length
		hsl = option.slot_length/2.0
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))
		d.append(Line(points=[(x1/2+hsl,y1),(x1/2.0+hsl,y2-t)],layer="CUTS"))
		d.append(Line(points=[(x1/2+hsl,y1-t),(x1/2.0-hsl,y2-t)],layer="CUTS"))
		d.append(Line(points=[(x1/2-hsl,y1-t),(x1/2.0-hsl,y2)],layer="CUTS"))

	def side3(self,d,type,x1,y1,x2,y2):
		t = option.thickness
		hsl = option.slot_length/2.0
		sl = option.slot_length
		d.append(Line(points=[(x1,y1),(x2,y2)],layer=type))
		d.append(Line(points=[(x1+t,y2+y1/2.0+hsl),(x1,y2+y1/2.0+hsl)],layer="CUTS"))
		d.append(Line(points=[(x1+t,y2+y1/2.0-hsl),(x1+t,y2+y1/2+hsl)],layer="CUTS"))
		d.append(Line(points=[(x1,y2+y1/2.0-hsl),(x1+t,y2+y1/2.0-hsl)],layer="CUTS"))
		

class chamfer(edge):

	def __init__(self,number,distx,disty):
		edge.__init__(self,number,distx,disty)
		self.cutaway = 0

	def side0(self,d,type,x1,y1,x2,y2):
		c = option.chamfer
		if self.cutaway:
			d.append(Line(points=[(x1+c,y1),(x2,y2)],layer=type))
		else:
			d.append(Line(points=[(x1,y1),(x2-c,y2)],layer=type))
			d.append(Line(points=[(x2-c,y1),(x2,y2+c)],layer=type))

	def side1(self,d,type,x1,y1,x2,y2):
		c = option.chamfer
		if self.cutaway:
			d.append(Line(points=[(x1,y1+c),(x2,y2)],layer=type))
		else:
			d.append(Line(points=[(x1,y1),(x2,y2-c)],layer=type))
			d.append(Line(points=[(x1,y2-c),(x2-c,y2)],layer=type))
			

	def side2(self,d,type,x1,y1,x2,y2):
		c = option.chamfer
		if self.cutaway:
			d.append(Line(points=[(x1-c,y1),(x2,y2)],layer=type))
		else:
			d.append(Line(points=[(x1,y1),(x2+c,y2)],layer=type))
			d.append(Line(points=[(x2+c,y1),(x2,y2-c)],layer=type))

	def side3(self,d,type,x1,y1,x2,y2):
		c = option.chamfer
		if self.cutaway:
			d.append(Line(points=[(x1,y1-c),(x2,y2)],layer=type))
		else:
			d.append(Line(points=[(x1,y1),(x2,y2+c)],layer=type))
			d.append(Line(points=[(x2,y2+c),(x2+c,y2)],layer=type))
		
		

def conffile(opt,config_file):
	c = ConfigParser.ConfigParser()
	try:
		os.stat(config_file)
		# read the configs
		c.readfp(open(config_file))
		items = c.options('default')
		# scan through the options
		for i in items:
			value = c.get('default',i)
			# cast as float if you can
			try:
				value = float(value)
			except:
				pass
			vars(opt)[i] = value 
	except:
		# no config file, strip out defaults and write to config.
		print 'no such config , populating default '
		c.add_section('default')
		k = vars(opt).keys()
		k.sort()
		for i in k:
			c.set('default',i,vars(opt)[i])
		c.write(open(config_file,'w'))
		
def parse(parser):
	# parse the command line options
	print 'Options'
	# define the command line variables
	parser.add_option("-l","--length",dest="length",help="Length of box in mm",type=float,default=100.0)
	parser.add_option("-w","--width",dest="width",help="width of box in mm",type=float,default=100.0)
	parser.add_option("-d","--depth",dest="depth",help="depth of box in mm",type=float,default=50.0)
	parser.add_option("-t","--thickness",dest="thickness",help="thickness of material in mm",type=float,default=2.0)
	parser.add_option("-f","--file_name",dest="filename",help="file_name",default="card.dxf")
        parser.add_option("-s","--slot_length",dest="slot_length",help="length of slot in mm",type=float,default=20.0)
        parser.add_option("-i","--inset",dest="inset",help="tuck inset in mm",type=float,default=10.0)
        parser.add_option("-c","--chamfer",dest="chamfer",help="corner chamfer in mm",type=float,default=10.0)
        parser.add_option("-p","--proportion",dest="proportion",help="tab and tuck reduction as ratio ",type=float,default=0.4)
		
def main():
	op = OptionParser()
	parse(op)
	global option
	(option,args) = op.parse_args()
	if len(args) == 1:
		if args[0][-3:] == 'cfg':
			print "using " + args[0]	
			conffile(option,args[0])
		else:
			print 'config file name must end in .cfg'
	# create the drawing
	d = Drawing()
	# generate the box object
	#d.layers.append(Layer(name="TEXT",color=2))
	#d.layers.append(Layer(name="CONSTRUCTION",color=1))
	d.layers.append(Layer(name="CUTS",color=0))
	d.layers.append(Layer(name="FOLDS",color=3))

	the_box  = box(option)
	the_box.build()
	# generage the dxf file
	the_box.gen(d)
	d.saveas(option.filename)

if __name__ == '__main__' : main()


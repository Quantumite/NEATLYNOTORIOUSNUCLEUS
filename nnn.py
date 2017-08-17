#!/usr/bin/python

from PIL import Image
import argparse, sys

def encode(infile, outfile, width, height):
	#Process arguments
	if infile is None:
		print "[!!] No input file specified!"
		quit(1)
	if outfile is None:
		print "[!!] No output file selected!"
	if width is None:
		print "[**] No img width specified, using default."
		width=100
	if height is None:
		print "[**] No img height specified, using default."
		height=100
	

	#Build IMG
	img = Image.new('RGB', (width,height), "black")
	pixels = img.load()

	#read in file data
	temp=''
	with open(infile, 'rb') as f:
		temp=f.read()

	#print len(temp)
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			if i*img.size[0]+j > len(temp)-1:
				c = 0
			else:
				#print "index: "+str(i*img.size[0]+j)
				#print "str[index]: "+str(temp[i*img.size[0]+j])
				#print "ord(str[index]): " + str(ord(temp[i*img.size[0]+j]))
				c = ord(temp[i*img.size[0]+j])
			pixels[i,j] = (c,c,c)
			

	#write pixels to image
	img.save(outfile,"PNG")

def decode(infile, outfile):
	
	#print "Infile: " + infile
	#print "Outfile: " + outfile	
	#Process arguments
	if infile is None:
		print "[!!] No input file specified!"
		quit(1)
	if outfile is None:
		print "[!!] No output file selected!"
	

	#Build IMG
	img = Image.open(infile)
	pixels = img.load()

	temp=''
	#get data from img
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			t=pixels[i,j][0]
			temp += chr(t)

	with open(outfile, 'wb') as f:
		f.write(temp)

def main():
	#ArgParse section
	parser = argparse.ArgumentParser(description='Save your data as an image to be uploaded to Amazon!')
	parser.add_argument('--infile', action='store', nargs='?', type=str, default=sys.stdin,help='Input file name.')
	parser.add_argument('--outfile', action='store', nargs='?', type=str, default=sys.stdout, help="Output file name.")
	parser.add_argument('--img-width', action='store', nargs='?', type=int, default=100, help="Specify an image width, default=100.")
	parser.add_argument('--img-height', action='store', nargs='?', type=int, default=100, help="Specify an image height, default=100.")
	parser.add_argument('--encode', action='store_true', help="Used to encode the data into an image.")
	parser.add_argument('--decode', action='store_true', help="Used to decode the data into text.")
	args = parser.parse_args()
	
	#print "Encode: " + str(args.encode)
	#print "Decode: "+ str(args.decode)
			
	if args.encode:
		encode(args.infile, args.outfile, args.img_width, args.img_height)
		quit(0)
	elif args.decode:
		decode(args.infile, args.outfile)
		quit(0)
	else:
		print "[!!] Not sure what to do, specify encode or decode!"
		quit(1)
	
	
if __name__=='__main__':
	main()

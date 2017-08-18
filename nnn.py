#!/usr/bin/python

from PIL import Image
import argparse, sys, os, tempfile, math, struct

def readFileSize(myFile, size, start=0, verbose=False):
	temp=''
	if verbose:
		print "[readFileSize][DEBUG] Expecting to read " + str(size) + " bytes."
		print "[readFileSize][DEBUG] Starting " + str(start) + " bytes in."	
	MAX = 1024**3
	if size > MAX:
		if verbose:
			print "[readFileSize][DEBUG] Size was larger than MAX, setting to MAX."
		size = MAX
	
	if verbose:
		print "[readFileSize][DEBUG] Reading file: " + str(myFile)	
	with open(myFile, 'rb') as f:
		f.seek(start)
		count = 0
		while count < size:
			temp += f.read(1)
			count += 1
	if verbose:
		print "[readFileSize][DEBUG] First chunk of f.readlines: " + str(temp[0])
	return ''.join(temp)

def encodeText(text, outfile, width, height, imageType, verbose=False):
	t = "/tmp/tmp.tmp"
	with open(t, 'wb') as f:
		f.write(text)
	if verbose:
		print "[encodeText][DEBUG] Created temporary file: " + str(t)
	encode(t, outfile, width, height, imageType, verbose)
	try:
		if verbose:
			print "[encodeText][DEBUG] Attempting to remove temporary file."
		os.remove(t)
	except OSError, ose:
		if ose.errno != errno.ENOENT:
			raise
	if verbose:
		print "[encodeText][DEBUG] File was encoded and temporary file removed, if existed."

def encode(infile, outfile, width, height, imageType, verbose=False):
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
	
	if verbose:
		print "[encode][DEBUG] Width: " + str(width) + ", Height: " + str(height)
	#Build IMG
	img = Image.new('RGB', (width,height), "black")
	pixels = img.load()

	if verbose:
		print "[encode][DEBUG] About to open file: " + str(infile)
	#read in file data
	temp=''
	with open(infile, 'rb') as f:
		temp=f.read()
	if verbose:
		print "[encode][DEBUG] Finished reading in file, first 10 bytes: " + str(temp[:10])

	count = 0
	tempLen = len(temp)
	lenArray = struct.unpack('4B', struct.pack('>I', tempLen))
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			if count < tempLen:
				c = ord(temp[i*img.size[0]+j])
				if count < 4:
					pixels[i,j] = (c,c,lenArray[count])			
				else:
					pixels[i,j] = (c,c,c)
				count +=1
			
	if verbose:
		print "[encode][DEBUG] Finished copying chars to image."
		print "[encode][DEBUG] Going to save image as: " + str(outfile)+", type: " + str(imageType)
	#write pixels to image
	img.save(outfile,imageType)

def decode(infile, outfile, imageType, verbose=False):
	
	if infile is None:
		print "[!!] No input file specified!"
		quit(1)
	if outfile is None:
		print "[!!] No output file selected!"
	

	if verbose:
		print "[decode][DEBUG] About to open: " + str(infile)
	#Build IMG
	try:	
		img = Image.open(infile)
	except IOError, ioe:
		print "The python image library this script uses could not identify the file type."
		print "This probably means something got messed up..."
		print "Go ahead and check that everything is correct with the image you're loading and try again."
		quit(1)
	pixels = img.load()

	temp=''
	count = 0
	#get data from img
	tempLen = pixels[0,3][2] + 256*(pixels[0,2][2]+256*(pixels[0,1][2] + 256*pixels[0,0][2]))
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			if count < tempLen:			
				t=pixels[i,j][0]
				temp += chr(t)
				count += 1

	if verbose:
		print "[decode][DEBUG] Finished pulling data from image. First 10 chars: " + str(temp[:10])
		print "[decode][DEBUG] Output file is: " + str(outfile)	
	if outfile is sys.stdout:
		outfile.write(str(temp))
	else:
		with open(outfile, 'wb') as f:
			f.write(str(temp))

def main():
	#ArgParse section
	parser = argparse.ArgumentParser(description='Save your data as an image to be uploaded to Amazon!')
	parser.add_argument('--infile', action='store', nargs='?', type=str, default=sys.stdin,help='Input file name.')
	parser.add_argument('--outfile', action='store', nargs='?', type=str, default=sys.stdout, help="Output file name.")
	parser.add_argument('--img-width', action='store', nargs='?', type=int, default=100, help="Specify an image width, default=100.")
	parser.add_argument('--img-height', action='store', nargs='?', type=int, default=100, help="Specify an image height, default=100.")
	parser.add_argument('--encode', action='store_true', help="Used to encode the data into an image.")
	parser.add_argument('--decode', action='store_true', help="Used to decode the data into text.")
	parser.add_argument('--img-type', action='store', nargs='?', type=str, default="PNG", help="Declare which type of image you are using. The default is PNG. Use three capital letters to specifiy format (BMP, TIF, GIF, PNG are supported). Others may or may not work...")
	parser.add_argument('--split', action='store_true', help="Use this flag when the file is larger that 1GB. The script will not work if the file is larger than 1GB and this flag is not used.")
	parser.add_argument('--split-size', action='store', nargs='?', type=int, default=1024, help='Use this to specify what size you would like to split your file into. Default 1024 bytes.')
	parser.add_argument('-v', '--verbose', action='store_true', help='Use to display debugging information.')
	args = parser.parse_args()

	#Determining which image type to use
	imageType = args.img_type.upper()
	if args.verbose:
		print "[DEBUG] imageType: " + str(imageType)
	if imageType != 'PNG':
		if imageType == 'BMP' or imageType == 'TIF' or imageType == 'GIF':
			print "Image Type is " + str(imageType) + " ."
		else:
			print "Sorry, that file type does not make sense."
			print "We'll use PNG instead!"
			imageType = 'PNG'

	#Calculating file size before going further...
	infileSize = os.stat(args.infile).st_size
	if args.verbose:
		print "[DEBUG] Input File Size: " + str(infileSize)
	if infileSize > 1024**3 and not args.split:
		print "Hey, the file is pretty large and you did not use the split flag."
		print "Would you mind trying again with the split flag so we don't make HUGE IMAGES!!"
		quit(2)

	if args.split:
		size = args.split_size
		count = int(math.ceil(infileSize/size))
		if args.verbose:
			print "[DEBUG] Split Size: " + str(size)
			print "[DEBUG] Count of files: " + str(count)
		for i in range(count):
			if args.verbose:
				print "[DEBUG] Input File Name: " + str(args.infile)
				print "[DEBUG] Starting to read at byte: " + str(i*size)
				print "[DEBUG] Output file name(s): " + args.outfile + "_" + str(i)
			encodeText(readFileSize(args.infile, size, i*size, args.verbose), str(args.outfile+"_"+str(i)), args.img_width, args.img_height, imageType, args.verbose)
		quit(0)
	
	if args.encode:
		if args.verbose:
			print "[DEBUG] Input File Name: " + str(args.infile)
			print "[DEBUG] Output File Name: " + str(args.outfile)
		encode(args.infile, args.outfile, args.img_width, args.img_height, imageType, args.verbose)
		quit(0)
	elif args.decode:
		if args.verbose:
			print "[DEBUG] Input File Name: " + str(args.infile)
			print "[DEBUG] Output File Name: " + str(args.outfile)
		decode(args.infile, args.outfile, imageType, args.verbose)
		quit(0)
	else:
		print "[!!] Not sure what to do, specify encode or decode!"
		quit(1)
	
	
if __name__=='__main__':
	main()

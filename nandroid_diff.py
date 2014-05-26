#!/usr/bin/env python

# build a timeline of changes between 2 or more Nandroid backups
# Izar Tarandach, May/2014 - GPLv2 but really, feel free to do whatever with it
#


import tarfile
import os
import sys
import argparse
import re
import hashlib
from itertools import izip

verbose = False
hash_verify = False
bag_of_dicts = dict()
out_fn = "output.csv"

def verb(msg,cr=True):
	global verbose

	if verbose:
		if cr is True:
			print msg
		else:
			sys.stdout.write(msg)
			sys.stdout.flush()


def build_file_timeline(fn):
	timeline = dict()
	ping = 0

	if not tarfile.is_tarfile(fn):
		print "{} is not a valid tarfile.".format(fn)
		# TODO: implement boot.img parsing
		return {}
	
	verb("Building a timeline for {}".format(fn))
	try:		
		tar_fd = tarfile.open(fn,"r:*")
		for fn in tar_fd:
			ping += 1
			# write out a dot every 100 files
			if not (ping % 100):
				verb(".",False) 
			file_tuple = fn.name, fn.size, fn.mtime, oct(fn.mode), fn.uid,fn.gid,fn.uname,fn.gname
			timeline[fn.name] = file_tuple
		tar_fd.close()
		verb("\n")
		return timeline

	except tarfile.TarError as e:
		print "An error occurred reading file {}".format(fn)
		sys.exit(-1)

def verify_md5(fn_md5):
	fn=re.sub('\.md5$','',fn_md5)
	verb("Checking MD5 checksum for {}".format(fn))
	# get the expected MD5
	with open(fn_md5,'r') as f:
		emd5 = f.readline().split(' ')[0]
	verb("Expecting  {}".format(emd5))
	h = hashlib.md5()
	with open(fn,'r') as f:
		# will try to glob the whole file in one swoop - memory constraints?
		h.update(f.read())
	md5 = h.hexdigest()
	verb("Calculated {}".format(md5))
	if md5 != emd5:
		print "Hash verification for {} did not succeed.".format(fn)
		sys.exit(-1)

def is_file_uniq(out,d1,d2,which_dir):
	global bag_of_dicts

	# files that are in the 1st backup but not in the 2nd
	uniq = bag_of_dicts[d1].viewkeys() - bag_of_dicts[d2].viewkeys()

	for x in uniq:
		entry = bag_of_dicts[d1][x]
		verb("File {} exists only on {}".format(
			entry[0],d1))
		out.write("{},{},{},{},{},{},{},{},{}\n".format(entry[0],which_dir,entry[1],entry[2],entry[3],entry[4],entry[5],entry[6],entry[7]))
	return uniq

def traverse_directory(dn):
	global hash_verify
	global bag_of_dicts 

	# first verify MD5s - not much point in doing everything if the hashes don't match to begin with
	for fn in os.listdir(dn):
		if re.match('.*\.md5$',fn) and hash_verify is True:
			verify_md5(dn+os.sep+fn)

	# now build the file values for each directory
	bag_of_dicts[dn] = dict()
	for fn in os.listdir(dn):
		if not re.match('.*\.md5$',fn):	
			 bag_of_dicts[dn].update(build_file_timeline(dn+os.sep+fn))


def main(dirs):
	global bag_of_dicts
	global out_fn
	ping = 0

	for dir in dirs:
		traverse_directory(dir)

	verb("Comparing both timelines.")
	# now compare the file lists looking for what's been changed
	# each directory is a key to an entry in bag_of_dicts that 
	# contains the full file names as keys for a tuple with the 
	# file stats
	d1,d2 = bag_of_dicts.keys()
	out = open(out_fn,'w')
	out.write("FILENAME,"+d1+","+d2+",SIZE,MTIME,MODE,UID,GID,UNAME,GNAME\n")

	uniq_first = is_file_uniq(out,d1,d2,"X,")
	uniq_second = is_file_uniq(out,d2,d1,",X")

	for f1,f2 in izip(bag_of_dicts[d1].keys(),bag_of_dicts[d2].keys()):
		ping += 1
		if not (ping % 100):
			verb(".",False)
		# no point in comparing files that are only in one set
		if f1 in uniq_first or f2 in uniq_second:
			continue

		try:
			if bag_of_dicts[d1][f1] != bag_of_dicts[d2][f1]:
				b1 = bag_of_dicts[d1][f1]
				b2 = bag_of_dicts[d2][f2]
				out.write(f1+",X,X,")
				for n in range(1,8):
					# write only the changed values
					if b1[n] != b2[n]:
						out.write("{} != {},".format(b1[n],b2[n]))
					else:
						out.write(",")
				out.write('\n')
		except KeyError as e:
			print e.args

	out.close()

if __name__ == '__main__':
	prsr = argparse.ArgumentParser()
	prsr.add_argument('dirs',metavar='D',nargs="+",
						help='a directory used for comparison')
	prsr.add_argument('-v',dest='verbose',action='store_true',help='verbose')
	prsr.add_argument('--hash',dest='hash_verify',action='store_true',help='verify MD5 hashes')
	prsr.add_argument('-o',dest='output_file',help='file to output to - defaults to output.csv')
	args = prsr.parse_args()
	verbose = args.verbose
	hash_verify = args.hash_verify
	if args.output_file:
		out_fn = args.output_file
	verb("Output to {} ".format(out_fn))
	if hash_verify is False:
		verb("Not checking hashes.")
	main(args.dirs)
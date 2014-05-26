nandroid_diff
=============
(Izar Tarandach, May/2014)

A small tool to create diff timelines of two Nandroid (http://forum.xda-developers.com/wiki/NANDroid) backup directories 

USAGE
=====

    usage: nandroid_diff.py [-h] [-v] [--hash] [-o OUTPUT_FILE] D1 D2

    positional arguments:
      D1, D2          a directory used for comparison

	optional arguments:
	  -h, --help      show this help message and exit
	  -v              verbose
	  --hash          verify MD5 hashes
	  -o OUTPUT_FILE  file to output to - defaults to output.csv


This will create a CSV output file (defaults to output.csv) containing:

FILENAME, DIR1_NAME, DIR2_NAME, SIZE, MTIME, MODE, UID, GID, UNAME, GNAME

Files that appear only on one of the directories will appear with a "X" under the respective directory name (2nd and 3rd column).

Each value that is different between the directories will show as "val1 != val2":

    /data/data/com.google.android.gm/lib,X,X,0 != 508,1398532142 != 1217592000,0120777 != 0100644,1012 != 0,1012 != 0,install != root,install != root



""" pagelist2.py  Parses the information gathered by pagelist,
  to get a single unified file showing correspondence between
  pageids and titles.
  Aug 7, 2015
"""

import codecs,re,sys
import os
import json

def pagelist2(directory,fileout):
 d = {}
 for filename in os.listdir(directory):
  print filename
  file1 = "%s/%s" %(directory,filename)
  with open(file1,"r") as f:
   data = json.load(f)
  datalist = data['query']['prefixsearch']
  for item in datalist:
   title = item['title']
   pageid = item['pageid']
   # parse title to get a sort key
   m = re.search(r'([0-9]+)$',title)
   if not m:
    print "Wrong title=",title
    continue
   key = int(m.group(1))
   if key in d:
    print "duplicate",title
   else:
    d[key]=(title,pageid)
 keys = d.keys()
 keys1 = sorted(keys)
 f = codecs.open(fileout,"w","utf-8")
 for key in keys1:
  (title,pageid)=d[key]
  # use comma as separator. title is like:
  # Page:Sanskrit Grammar by Whitney p1.djvu/580
  f.write("%s,%s\n" %(title,pageid))
 print len(keys),"records written to",fileout
 f.close()

if __name__ == "__main__":
 directory=sys.argv[1]
 fileout = sys.argv[2]
 pagelist2(directory,fileout)

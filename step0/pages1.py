""" pages.py  Get part of the 
  pages from Whitney's Grammar
  Aug 7, 2015
"""

import requests
import codecs,re,sys

def get_pageids(n1,n2,recs):
 pageids=[]
 for n in xrange(n1,n2+1):  # inclusive
  (title,pageid) = recs[n-1] # n1,n2 start at 1
  pageids.append(pageid)
 return pageids

def pages1(n1,n2,recs,fileout):
 baseurl = "https://en.wikisource.org/w/api.php"
 pageids=get_pageids(n1,n2,recs)
 pageids_str = '|'.join(pageids)  # form expected by api is '|' separated
 payload = {'format':'json',
  'action':'query',
  'prop':'revisions',
  'rvprop':'content',
  'pageids':pageids_str
 }
 r = requests.get(baseurl,params=payload)
 f = codecs.open(fileout,"w","utf-8")
 f.write(r.text)
 print len(r.text),"text size written to",fileout
 f.close()

def init_pagelist2(filein):
 with open(filein,'r') as f:
  recs = []
  for line in f:
   line = line.rstrip('\r\n')
   (title,pageid) = re.split(',',line)
   recs.append((title,pageid))
 return recs

if __name__ == "__main__":
 n1 = int(sys.argv[1])
 n2 = int(sys.argv[2])
 filein = sys.argv[3]
 fileout = sys.argv[4]
 recs = init_pagelist2(filein)
 pages1(n1,n2,recs,fileout)

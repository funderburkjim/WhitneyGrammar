""" pagelist.py  Get part of the 
  list of Whitney grammar pages from wikisource
  Aug 7, 2015
"""

import requests
import codecs,re,sys

def pagelist(psoffset,pslimit,fileout):
 baseurl = "https://en.wikisource.org/w/api.php"
 payload = {'format':'json',
  'action':'query',
  'list':'prefixsearch',
  'pssearch':'Page:Sanskrit_Grammar_by_Whitney_p1.djvu', # whitney grammar
  'psoffset':psoffset,
  'pslimit':pslimit
 }
 r = requests.get(baseurl,params=payload)
 f = codecs.open(fileout,"w","utf-8")
 f.write(r.text)
 f.close()

if __name__ == "__main__":
 psoffset = sys.argv[1]
 pslimit = sys.argv[2]
 fileout = sys.argv[3]
 pagelist(psoffset,pslimit,fileout)

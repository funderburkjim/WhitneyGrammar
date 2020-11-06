""" pages2.py  Parses the information gathered by pages,
 .
  Aug 8, 2015
"""

import codecs,re,sys
import os
import json

def pages2(directory,fileout):
 pagedata = {} 
 for filename in os.listdir(directory):
  print (filename)
  file1 = "%s/%s" %(directory,filename)
  with codecs.open(file1,"r") as f:
   data = json.load(f)
  # unpack json
  query = data['query']
  pages = query['pages'] # a dict with pageids as keys
  pageids = pages.keys()
  # pageids not in same order as appears in file
  # must resort using title
  for pageid in pageids:
   page = pages[pageid]
   title = page['title']
   revisions = page['revisions']
   latest = revisions[0]  # in this case, only 1 revision, the latest
   content = latest['*']
   m = re.search('([0-9]+)$',title)  # ...djvu/<number>
   if not m:
    print("ERROR 1",title)
    exit(1)
   key = int(m.group(1))
   pagedatum = (pageid,title,content)
   pagedata[key]=pagedatum
 f = codecs.open(fileout,"w","utf-8")
 pagekeys = sorted(pagedata.keys())
 for key in pagekeys:
  (pageid,title,content) = pagedata[key]
  f.write('\n[%s,%s]\n' % (pageid,title))
  f.write('%s\n'%content)
 print(len(pagedata),"records written to",fileout)
 f.close()

if __name__ == "__main__":
 directory=sys.argv[1]
 fileout = sys.argv[2]
 pages2(directory,fileout)

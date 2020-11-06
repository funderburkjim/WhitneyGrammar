""" parse1.py
    Parse data in the files of pages1 directory.
    Sep 29, 2015
"""
import codecs, sys, json, re

def parsepage(page):
 """ page is a dictionary. We use the two keys
  title  : a string of form "Page:Sanskrit Grammar by Whitney p1.djvu/<n>"
     where n is the scan page number
  revisions : An array, with one element, a dictionary containing a few
    keys. The  key '*' has value a string which is the content
 """
 title = page['title']
 revisions = page['revisions']
 if len(revisions)> 1:
  print "title has > 1 revision",title.encode('utf-8')
 m = re.search(r'Page:Sanskrit Grammar by Whitney p1.djvu/([0-9])+$',title)
 scanpagenum=m.group(1)
 scanpageurl="https://en.wikisource.org/wiki/%s" % title
 content = revisions[0]['*']
 print "Scan page",scanpagenum,"contentlength=",len(content)
 

if __name__ == "__main__":
 print "hello"
 filein = sys.argv[1] 
 f = codecs.open(filein,"r","utf-8")
 jdata = json.load(f)
 f.close()
 pages = jdata['query']['pages']
 pageskeys = sorted(pages.keys())
 print len(pageskeys)
 for pageskey in pageskeys:
  parsepage(pages[pageskey])
 print "done"

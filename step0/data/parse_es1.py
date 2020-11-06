""" parse_es1.py
    Parse data in the files of pages1 directory.
    Sep 30, 2015
    Generate output appropriate for an elasticsearch bulk indexing
    input file.
"""
import codecs, sys, json, re

def parsepage(page,fout):
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
 m = re.search(r'Page:Sanskrit Grammar by Whitney p1.djvu/([0-9]+)$',title)
 scanpagenum=m.group(1)
 scanpageurl="https://en.wikisource.org/wiki/%s" % title
 content = revisions[0]['*']
 print "Scan page",scanpagenum,"contentlength=",len(content)
 # make first record, as dict
 # { "index" : { "_index" : "<index_name>", "_type" : "<type_name>", "_id" : "1" } }
 a = {"index" :{ "_index" : "test-index" , "_type":"wg" , "_id" : scanpagenum}}
 # make second record, as dict
 b = {"page":scanpagenum , "content":content}
 ## Now, serialize both records, and print to output on two \n terminated 
 #  lines
 for x in [a,b]:
  s = json.dumps(x)
  fout.write("%s\n" % s)

if __name__ == "__main__":
 filein = sys.argv[1] 
 fileout = sys.argv[2]
 f = codecs.open(filein,"r","utf-8")
 jdata = json.load(f)
 f.close()
 pages = jdata['query']['pages']
 pageskeys = sorted(pages.keys())
 print len(pageskeys)
 fout = codecs.open(fileout,"w","utf-8")
 for pageskey in pageskeys:
  parsepage(pages[pageskey],fout)
 fout.close()
 print "done"

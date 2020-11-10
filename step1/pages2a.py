""" pages2a.py  
  Nov 5, 2020
"""

import codecs,re,sys
import os

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

def init_lines(filein):
 with codecs.open(filein,"r","utf-8") as f:
  lines = [x.rstrip('\r\n') for x in f]
 print(len(lines),"lines read from",filein)
 return lines

def int_to_Roman(num):
 """ Ref: https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-1.php
 """
 val = [
  1000, 900, 500, 400,
  100, 90, 50, 40,
  10, 9, 5, 4,
  1
  ]
 syb = [
  "M", "CM", "D", "CD",
  "C", "XC", "L", "XL",
  "X", "IX", "V", "IV",
  "I"
  ]
 roman_num = ''
 i = 0
 while  num > 0:
  for _ in range(num // val[i]):
   roman_num += syb[i]
   num -= val[i]
  i += 1
 return roman_num

def adjust_pages(lines):
 nchg = 0
 for iline,line in enumerate(lines):
  m = re.search(r'^\[[0-9]+,Page:Sanskrit Grammar by Whitney p1.djvu/([0-9]+)\]$',line)
  if not m:
   continue
  djvu = m.group(1)
  ndjvu = int(djvu)
  if ndjvu >= 29:
   npage = ndjvu - 28
   page = '%03d'%npage
  elif 7<=ndjvu<=28:
   roman = int_to_Roman(ndjvu - 2)
   page = roman.lower()
   #print(ndjvu,'->',page)
  newline = '[Page=%s djvu=%s]'%(page,djvu)
  lines[iline] = newline
  nchg = nchg + 1
 print('adjust_pages',nchg,'lines changed')

def dropPreface(lines):
 """ drop lines until 'djvu/7'
 """
 newlines = []
 flag = False
 for iline,line in enumerate(lines):
  if flag:
   newlines.append(line)
   continue
  m = re.search(r'^\[[0-9]+,Page:Sanskrit Grammar by Whitney p1.djvu/([0-9]+)\]$',line)
  if m:
   ndjvu = int(m.group(1))
   if ndjvu == 7:
    # include this line, and set flag so subsequent lines include
    newlines.append(line)
    flag = True
 print(len(newlines),"lines kept by dropPreface")
 return newlines

def adjust_markup_xml(lines):
 """  remove xml markup:
  
  
  
 """
 remove_xml = [
  "<noinclude>","</noinclude>","<pagequality.*?/>","<references/>",
  "<includeonly>","</includeonly>",
  '<div align="right">\[-169</div>', #once . The '\' is for regex
  '<div class="pagetext">','<div align="center">',
   "</div>", "</div >",
   "<p>","</p>",
   "{{blank line}}",
   '<section begin=[^>]*>',  # 14, For chapters beginning in middle of page
   '<section end=[^>]*>',
   '57<center>{{sc|Final S and T.}}</center>', # once
   '{{rh.*}}', # 5 times
 ]
 replaces = [
  ('<tt>','**'),  # bold text.  ** is markdown.  Note '*' not used in pages2.txt
  ('</tt>','**'),
  ("''","*"),     # italic text. * is markdown
  ('<br />','<br>'),('<br/>','<br>'),  # remove some irregularities
  ('<br>','~'),  # temporary.  No ~ in pages2.txt
  #('<center><big>','<H1>'), # chapter titles, except at lines 662, 672
  #('',''),
 ]
 subs = [
  (r'^<center><big>(.*?)</big>(.*?)</center> *$',r'<H1>\1\2</H1>'),
  (r'^<center><big>(.*?)</big> *$',r'<H1>\1'),
  (r'^<center>(.*?)</center> *$',r'<H2>\1</H2>'),
  (r'^{\| *class="?prettytable"?',r'{|prettytable'),
  #('',''),
 ]
 # Alphabet differences
 # Diphthong āi (312)  <-> ai
 # Diphthong āu (201)  <-> au
 # anusvara ṅ (276) ṁ (322) ṃ (3) <-> ṃ
 # guttural nasal n̄ (160)  <-> ṅ 
 # palatal sibilant ç (1271) <-> ś 
 #    ś occurs in #748 incorrectly for accent over long 'i'

 nchg = 0
 for iline,line in enumerate(lines):
  oldline = line
  for regex in remove_xml:
   line = re.sub(regex,'',line)
  for old,new in replaces:
   line = line.replace(old,new)
  for old,new in subs:
   line = re.sub(old,new,line)
  if line != oldline:
   lines[iline] = line
   nchg = nchg + 1
 print('adjust_markup_xml',nchg,'lines changed')

def mark_sections(lines):
 # Mark the numeric sections
 # These occur for chapters I to 18 (<H1>CHAPTER nnn.)
 # 
 nchg = 0
 curpage = None
 curchapter = None
 for iline,line in enumerate(lines):
  m = re.search(r'^\[Page=([0-9][0-9][0-9]) ',line)
  if m:
   curpage = m.group(1)
   continue
  m = re.search(r'^<H1>(.*?)</H1>',line)
  if m:
   title = m.group(1)
   if title.startswith('CHAPTER'):
    m = re.search(r'^CHAPTER (.*?)[.]',title)
    if not m:
     print('CHAPTER error',line)
     exit(1)
    curchapter = m.group(1)  # the chapter number in roman numerals
   else:
    curchapter = None
   continue
  # line is neither a page break nor a chapter break
  if (curpage == None) or (curchapter == None):
   continue
  m = re.search(r'^([0-9]+[.])',line)
  if not m:
   continue
  # If line starts with a sequence of digits followed by a period,
  # then it is a section number.
  # add markup  <section n="x,y,z"/>  
  # x = section number, y = curpage, z=curchapter
  cursection = m.group(1)
  temp = '<section n="%s,%s,%s"/>' %(cursection,curpage,curchapter)
  line = re.sub('^([0-9]+[.])',temp,line)
  lines[iline] = line
  nchg = nchg + 1
  #print(nchg,temp)  # for debugging
 print(nchg,"lines marked as sections")

def tempwrite(lines):
 for iline,line in enumerate(lines):
  if line.startswith(('<H1>','<H2>','<section ')):
   line = re.sub(r'^(<section.*?>)(.*)$',r'\1',line)
   print(line)
if __name__ == "__main__":
 filein = sys.argv[1]
 fileout = sys.argv[2]
 lines = init_lines(filein)
 lines = dropPreface(lines)
 adjust_pages(lines) # lines adjusted in place
 adjust_markup_xml(lines)
 mark_sections(lines)
 tempwrite(lines)
 # write lines
 with codecs.open(fileout,"w","utf-8") as f:
  for line in lines:
   f.write(line+'\n')
 print(len(lines),"written to",fileout)


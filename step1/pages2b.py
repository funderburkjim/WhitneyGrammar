""" pages2b.py  
  Nov 9, 2020
"""

import codecs,re,sys
import os


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

class Table(object):
 def __init__(self,page,lines,idx1,idx2):
  self.page = page
  self.lines = lines
  self.iline1 = idx1 + 1
  self.iline2 = idx2 + 1  # last line (included)
  self.html = None

def tablesfind(lines):
 tables = []
 intable = False
 nlines = len(lines)
 iline = 0
 page = None
 while (iline < nlines):
  line = lines[iline]
  if not line.startswith('{|'):
   m = re.search(r'\[Page=(.*?) ',line)
   if m:
    page = m.group(1)
   iline = iline + 1
   continue
  itable1 = iline
  while True:
   iline = iline + 1
   if iline > nlines:
    print('error 1 tempwrite',len(tables),itable1)
    exit(1)
   line = lines[iline]
   if line.startswith('{|'):
    print('error 2 tempwrite',len(tables),itable1,iline)
    exit(1)
   if line.startswith('|}'):
    itable2 = iline
    tablelines = lines[itable1:itable2+1]
    table = Table(page,tablelines,itable1,itable2)
    tables.append(table)
    break  # while True
 print(len(tables),'tables found')
 return tables

html_header = """
<!DOCTYPE html>
<html>
<head>
<style>
.flex-container {
  display: flex;
  flex-wrap: nowrap;
  background-color: DodgerBlue;
}

.flex-container > div {
  background-color: #f1f1f1;
  width: 50%% ;
  margin: 10px;
  text-align: center;
  /*line-height: 75px;*/
  font-size: 12px;
  overflow:auto;
}
table, th, td {
  border: 1px solid black;
}

</style>
</head>
<body>
"""
def print_html1(tabnum,table):
 tablestring = '<br/>\n'.join(table.lines)
 out = """
<h1>Table %s at page %s, line %s</h1>

<div class="flex-container">
  <div>%s</div>
  <div>%s</div>
</div>
</body>
</html>
 """%(tabnum,table.page,table.iline1,tablestring,table.html)
 return out

def table_html_media(tabnum,table):
 tablestring = '<br/>\n'.join(table.lines)
 out = """
<h1>Table %s at page %s, line %s</h1>
%s
 """%(tabnum,table.page,table.iline1,tablestring)
 return out

def table_html_html(tabnum,table):
 tablestring = '<br/>\n'.join(table.lines)
 out = """
<h1>Table %s at page %s, line %s</h1>
%s
 """%(tabnum,table.page,table.iline1,table.html)
 return out

def htmltables(tables):
 # use py-wikimarkup
 from wikimarkup.parser import Parser
 parser = Parser()
 for table in tables:
  tablelines = table.lines
  tablestring = '\n'.join(tablelines)
  tablestring = re.sub(r'[*][*](.*?)[*][*]',r'<b>\1</b>',tablestring)
  html = parser.parse(tablestring)
  html = html.replace('~','<br/>')
  #html = adjust_html(html)
  table.html = html

def calc_tables_media(tables):
 allout = []
 allout.append(html_header)
 for itab,table in enumerate(tables):
  jtab = itab+1
  if True: #(itab1<=jtab<=itab2):
   out = table_html_media(jtab,table)
   allout.append(out)
 allout.append('</body>')
 allout.append('</html>')
 return allout

def calc_tables_html(tables):
 allout = []
 allout.append(html_header)
 for itab,table in enumerate(tables):
  jtab = itab+1
  if True: #(itab1<=jtab<=itab2):
   out = table_html_html(jtab,table)
   allout.append(out)
 return allout

def calc_tables_html(tables):
 allout = []
 for itab,table in enumerate(tables):
  #allout = []
  #allout.append(html_header)
  jtab = itab+1
  out = table_html_html(jtab,table)
  allout.append(out)
 return allout

def read_table(itable,dirin):
 jtable = itable + 1
 filename = '%s/table_%03d.html' %(dirin,jtable)
 with codecs.open(filename,"r","utf-8") as f:
  tablines = [x.rstrip('\r\n') for x in f]
 # keep only the lines of interest
 # look for line: <h1>Table %s at page %s, line %s</h1>
 tabid = None
 iline0 = None
 for iline,line in enumerate(tablines):
  m = re.search(r'^<h1>Table (.*?) at page (.*?), line (.*?)</h1>$',line)
  if m:
   tabid = int(m.group(1))
   tabpage = m.group(2)
   tabline = m.group(3)  # the line number in pages2a.txt
   iline0 = iline
   #line0 = line
   break
 if tabid == None:
  print('read_table: Error 1.',jtable)
  exit(1)
 if tabid != jtable:
  print('read_table: Error 2.',jtable,tabid)
  exit(1)
 # get lines <table>...</table>
 table_lines = []
 bodyflag = False
 for line in tablines[iline0+1:]:
  if line == '</body>':
   bodyflag = True
   break
  table_lines.append(line)
  #print('dbg:',j,line)
 if not bodyflag:
  print('read_table: Error 3.',jtable)
  exit(1)
 return (tabid,tabpage,tabline,table_lines)

if __name__ == "__main__":
 filein = sys.argv[1]
 dirin = sys.argv[2]  # html tables directory
 fileout = sys.argv[3]  # 
 lines = init_lines(filein)
 tables = tablesfind(lines)
 # modify lines in reverse order of tables
 ntables = len(tables)
 itable = ntables - 1
 while (itable >= 0):
  table = tables[itable]
  (tabid,tabpage,tabline,table_lines) = read_table(itable,dirin)
  assert tabpage == table.page
  assert int(tabline) == table.iline1
  idx1 = table.iline1 - 1
  idx2 = table.iline2 - 1
  before = lines[0:idx1]
  after  = lines[idx2+1:]
  insert0 = '<!-- Table %s at page %s -->' %(tabid,tabpage)
  insertlines = [insert0] + table_lines
  lines = before + insertlines + after
  itable = itable - 1
 # print the new lines
 with codecs.open(fileout,"w","utf-8") as f:
  for out in lines:
   f.write(out+'\n')
 print(len(lines),"written to",fileout)
 exit(1)
 # html format for tables
 arr = calc_tables_html(tables)
 for itab,out in enumerate(arr):
  jtab = itab+1
  filename = 'table_%03d.html' %jtab
  fileout = '%s/%s' %(dirout,filename)
  with codecs.open(fileout,"w","utf-8") as f:
   f.write(html_header+'\n')
   f.write(out+'\n')
   f.write('</body>\n')
   f.write('</html>\n')
 exit(1)
 write_tables_media(tables,fileout)
 print_tables(tables,1,10)
 #print_html1(tables[25])
 #wikitable_2_html(tables[5])
 # write lines
 with codecs.open(fileout,"w","utf-8") as f:
  for line in lines:
   f.write(line+'\n')
 print(len(lines),"written to",fileout)


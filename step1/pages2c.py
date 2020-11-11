""" pages2c.py  
  Nov 9, 2020
"""

import codecs,re,sys
import os

def init_lines(filein):
 with codecs.open(filein,"r","utf-8") as f:
  lines = [x.rstrip('\r\n') for x in f]
 print(len(lines),"lines read from",filein)
 return lines

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


def adjust_lines(lines):
 removals = [
  '<p>{{hline\|4em}}</p>',
  '<p>{{div col\|2}}</p>',
  '<p>{{div col end}}</p>'
 ]
 replaces = [
  ('{{Self reference|54|../Chapter II|Page:Sanskrit Grammar by Whitney p1.djvu/47|54}}','54'),
  ('~</p>','</p>'), # ~ is our temp markup for <br/>.
  ('~','<br/>'),
  ('mānasam<tt?','mānasam</b>'),
  #('<b>jújoṣate<tt/>); and the 3d pl. </b>cākánanta, tatánanta<i></i>',
  # '<b>jújoṣate</b>); and the 3d pl. </b>cākánanta, tatánanta</b>'),
  ('ate<tt/>','ate</b>'),
  ('the 3d pl. </b>','the 3d pl. <b>'),
  ('nanta<i></i>','nanta</b>'),
  #('<i></i>dṛç<tt/>', '<b>dṛç</b>'),
  ('the gods said to him: Vrātya, why do you stand?"',
   'the gods said to him: "Vrātya, why do you stand?"'),
  ('<i></i>yadbhaviṣya<tt/>',
   '<b>yadbhaviṣya</b>'),
 ]
 subs = [
  (r'[*][*](.*?)[*][*]',r'<b>\1</b>'),
  (r'[*](.*?)[*]',r'<i>\1</i>'),
  (r'{{[hH]yphenated word start\|.*?\|(.*?)}}',r'\1'),
  (r'{{[hH]yphenated word end.*?}}',''),
  (r'{{[hH]ws\|.*?\|(.*?)}}',r'\1'),
  (r'{{[hH]we.*?}}',''),
  (r'{{sc\|(.*?)}}',r'<span style="font-variant:small-caps; font-family:serif;">\1</span>'),
  (r'{{SIC\|.*?\|(.*?)}}',r'\1'),
  (r'<ref>(.*?)</ref>',r' [* Footnote: \1] '),
  (r'<i></i>(.*?)<tt/>',r'<b>\1</b>'),
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
  for regex in removals:
   line = re.sub(regex,'',line)
  for old,new in replaces:
   line = line.replace(old,new)
  for old,new in subs:
   line = re.sub(old,new,line)
  if line != oldline:
   lines[iline] = line
   nchg = nchg + 1
 print('adjust_markup_xml',nchg,'lines changed')

def init_chapters(lines):
 chapters = []
 ichapter = 0
 pchapter = 0  # preface 'chapters'
 achapter = 0
 for iline,line in enumerate(lines):
  m = re.search(r'^\[Page=(.*?) ',line)
  if m:
   page = m.group(1)
   newline = '<a id="page_%s"></a>Page %s' %(page,page)
   lines[iline] = "<br/>%s<br/>" % newline
   continue
  m = re.search(r'^<H1>(.*)</H1>',line)
  if m:
   name=m.group(1)
   ichapter = ichapter + 1
   #linkid = 'chapter_%s' %ichapter
   if (ichapter < 6):
    linkid = 'chapter_p%s' %ichapter
   elif (ichapter < 24):
    jchapter = ichapter - 5
    linkid = 'chapter_%s' %jchapter
   else:
    jchapter = ichapter - 23
    linkid = 'chapter_a%s' %jchapter
    
   newline = '<a id="%s"></a>%s' %(linkid,line)
   lines[iline]=newline
   name = re.sub('^CHAPTER ','',name)
   chapters.append((linkid,name))
   continue
  m = re.search(r'^<section n="(.*?)"/>(.*)$',line)
  if m:
   n = m.group(1)
   rest = m.group(2)
   m = re.search(r'([0-9]+)[.]?,',n)
   name=m.group(1)
   linkid = 'section_%s' % name
   #newline = '<a id="%s"></a><p>%s. %s</p>' %(linkid,name,line)
   newline = '<a id="%s"></a><section n="%s">%s. %s</section>' %(linkid,n,name,rest)
   lines[iline]=newline
   continue
  if line.strip() == '':
   continue
  if line.startswith('<'):
   continue
  newline = '<p>%s</p>' % line
  lines[iline]=newline

 return chapters

def init_nav(chapters):
 a = [] 
 a.append('<div id="navbar">')
 a.append('<ul>')
 for linkid,name in chapters:
  x = '<a href="#%s" class="navitem">%s</a>' %(linkid,name)
  y = '<li>%s</li>' %x
  a.append(y)
 a.append('</ul>')
 a.append('</div>')
 return a

html_header = """
<!DOCTYPE html>
<html>
<head>
<style>

table, th, td {
  border: 1px solid black;
}
#navbar {
 position:fixed;
 top: 40px;
 left: 5px;
 width: 300px;
 height: 90%;
 overflow: auto;
}
#text {
position:absolute;
 top: 40px;
 left: 320px;
 right: 5px;
 height: 90%;
 overflow: auto;
}
.header {
 font-variant:small-caps;
 position:fixed;
 margin-top:0px;
 top:5px;
 left:5px;
 width: 100%;
}
ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
  font-size: 14px;
  overflow-x: auto;
  line-height: 1.5;
}
li a {
  display: block;
  font-family: sans-serif;
  text-decoration: none;
  color: black;
  width:380px;
}

</style>
</head>
<body>

"""

def init_html(navhtmlarr,lines):
 a = []
 a = html_header.splitlines()
 a.append("<H3 class='header'>Whitney's Sanskrit Grammar</H3>")
 a = a + navhtmlarr
 a.append('<div id="text">')
 a = a + lines
 a.append('</div>')
 a.append('</body>')
 a.append('</html>')
 return a

if __name__ == "__main__":
 filein = sys.argv[1]
 fileout = sys.argv[2]  # 
 lines = init_lines(filein)
 chapters = init_chapters(lines)
 navhtmlarr = init_nav(chapters)
 adjust_lines(lines)
 htmlarr = init_html(navhtmlarr,lines)

 # print the new lines
 with codecs.open(fileout,"w","utf-8") as f:
  for out in htmlarr:
   f.write(out+'\n')
 print(len(htmlarr),"lines written to",fileout)

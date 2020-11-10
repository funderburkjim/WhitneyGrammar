
## step1/pages2.txt
This has some manual adjustments to step0/pages2.txt.

## step2/pages2.txt
Programmatic adjustments to pages2.txt

python pages2a.py pages2.txt pages2a.txt

## wikimarkup and bleach projects used
Tables in pages2a.txt are in the mediawiki table format.
  Ref: https://www.mediawiki.org/wiki/Help:Tables

We use the py-wikimarkup repository to get a FIRST transformation
to html tables.

## installation of wikimarup and bleach
https://github.com/dgilman/py-wikimarkup
 download zip, extract to py-wikimarkup-master,
 cp -r py-wikimarkup-master/wikimarkup .

$ pip install bleach

## extract tables
python pages2a_tables.py pages2a.txt pages2a_tables_media.html tables0

Tables in pages2a.txt are in identified by '{|...|}'  (mediawiki table format)
There are 178 tables.

The first file, pages2a_tables_media.html, is for possible reference.
It contains all the tables in the original mediawiki format.

The tables0 directory contains 178 html files, named as table_001.html thru
table_178.html.

Each of these files contains an html table, generated programmatically
by the wikimarkup software from the corresponding '{|...|}' mediawiki
table.


## manually adjust tables
It is soon apparent that some adjustments are needed to the wikimarkup generated
html tables.
This is done manually.
First, we get a copy of the tables0 directory.
```
cp -r tables0 tables
```

Then, we compare the browser tables (e.g., tables/table_004.html) with
the corresponding table in the printed text of Whitney.

And we make adjustments.  Mostly these are quite minor adjustments.

## pages2b.txt

Here we replace the mediawiki tables of pages2a.txt with the 
adjusted tables from the tables directory

python pages2b.py pages2a.txt  tables pages2b.txt


215 260  46
(- 260 215)

31 89   58


{{TOC .*?|.*?|.*?|\(.*?\)}} -> \1
{{sc|\(.*?\)}}  -> <span style="font-variant:small-caps;">\1</span>

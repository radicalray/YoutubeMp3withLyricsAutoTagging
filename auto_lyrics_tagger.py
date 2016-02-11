# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import glob
import os
import eyed3
import urllib2
from urllib2 import urlparse
from bs4 import BeautifulSoup
import traceback
import re
from hn2 import *

SUPPORTED_SITES = re.compile('www.metrolyrics.com|www.azlyrics.com')

def parseout_metrolyrics(lyricslink):
  lyrics_html = urllib2.urlopen(lyricslink).read()
  soup = BeautifulSoup(lyrics_html)
  raw_lyrics= (soup.findAll('p', attrs={'class' : 'verse'}))
  paras=[]
  test1=unicode.join(u'\n',map(unicode,raw_lyrics))

  test1= (test1.replace('<p class="verse">','\n'))
  test1= (test1.replace('<br/>',' '))
  test1 = test1.replace('</p>',' ')
  # print (test1)

  return test1

def parseout_arc90(lyricslink):
  lyrics_html = urllib2.urlopen(lyricslink).read()
  return extract_content_with_Arc90(lyrics_html)


def list_lyrics(lyricsList):
  for idx, (title, _) in enumerate(lyricsList):
    # lyrics = unicode(lyrics).replace("\r|\n|\t|\"", " ")
    # print lyrics, str(lyrics)
    yield '[{}] {}'.format(idx, title)


def clean_url(my_url):
  p = urlparse.urlparse(my_url, 'http')
  netloc = p.netloc or p.path
  path = p.path if p.netloc else ''
  if not netloc.startswith('www.'):
      netloc = 'www.' + netloc

  p = urlparse.ParseResult('http', netloc, path, *p[3:])
  return p.geturl()


def is_supported_site(link):
  return SUPPORTED_SITES.findall(link)


def search_google(query):
  links = []
  query  = query.replace(' ','+')

  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  ### Open page & generate soup
  ### the "start" variable will be used to iterate through 10 pages.
  print 'Searching through google for lyrics...'
  for start in range(0,1):
    print query, start
    url = u''.join(['http://www.google.com/search?q=', query, '&start=', str(start*10)])
    page = opener.open(url)
    soup = BeautifulSoup(page)

    ### Parse and find
    ### Looks like google contains URLs in <cite> tags.
    ### So for each cite tag on each page (10), print its contents (url)
    for cite in soup.findAll('cite'):
      link = cite.text
      if is_supported_site(link):
        # print 'added link', link
        links.append(link)

    return links

song_name= glob.glob("*.mp3")

for name in song_name:
  try:

    print 'tagging file', name
    # name = u'' + name
    string = name
    string = unicode(string, errors='strict')
    name = string.encode('utf-8')

    print('Test', name)


    audiofile = eyed3.load((name))
    print 'File loaded...'
    name= name.replace('.mp3','')
    print('Applying to '+name)
    query3 = name + ' lyrics'
    query2 = 'azlyrics ' + name
    query1 = 'metrolyrics ' + name


    links = search_google(query1) + search_google(query2) + search_google(query3)

    # url = 'http://www.google.com/search?q='+name

    # req = urllib2.Request(url, headers={'User-Agent' : "foobar"})

    # response = urllib2.urlopen(req)
    # str = response.read()
    # str = unicode(str, errors='replace')

    # #print(str.encode('utf8'))

    # result = str.encode('utf8')

    # link_start=result.find('www.alyrics.com')
    # link_end=result.find('html',link_start+1)
    # #print(result[link_start:link_start+57])


    # link = result[link_start:link_end+4]

    # print 'link', link, link_start, link_end
    #
    #      if re.findall('www.metrolyrics.com', link):
    #      re.findall('www.alyrics.com', link):
    # print 'links', links

    lyricsList = []


    for link in links:
      link = clean_url(link)
      if re.findall('www.youtube.com', link):
        continue
      print 'parse lyrics', link
      try:
        if re.findall('www.metrolyrics.com', link):
          lyricsList.append((link, parseout_metrolyrics(link)))
        else:
          lyricsList.append((link, parseout_arc90(link)))
      except Exception,e:
        # print (e)
        # traceback.print_exc()
        print ('This link sucked ', link)

    # print 'lyrics list', lyricsList

    notChosen = True

    while notChosen:
      print '-----------------------------------------------------------------'
      print "Found:", '\n', '\n'.join(list_lyrics(lyricsList))
      print '-----------------------------------------------------------------'

      print '\n'

      choice = ''
      while choice.strip() == '':
        choice = raw_input('Pick one: ')

      url, lyrics = lyricsList[int(choice)]
      print lyrics

      prompt = raw_input("Choose lyrics (y/n)? ")
      if prompt != "n":
        notChosen = False



        # lyrics = parseout_arc90(link)
        # print lyrics
        # prompt = raw_input("Choose lyrics (y/n)? ")
        # if prompt == "n"  or prompt == 'N':
        #     continue
        # break
        # break

    # print 'picked link', lyricslink
    print 'picked lyrics', lyrics

    tag = audiofile.tag

    name = str(name)

    if '-' in name:
      artist, title = name.split('-')
    else:
      title = name
      artist = ''
      print 'Couldn\'t parse out artist name from filename automatically'
    title = re.sub('\s\[(.*)\]', '', title)
    tag.artist = u'' + artist
    tag.title= u''+title
    tag.lyrics.set(u''+lyrics )
    tag.save()
    print '-----------------------------------------------------------------'

    print 'Title:', title.strip(), '\n'
    print 'Artiest:', artist.strip()
    print('lyrics Added! ')

    os.system('mv *.mp3 download/.')
    print 'Moved all mp3 to download folder after tagging'

  except Exception,e:
    print (e)
    traceback.print_exc()
    print ('An error occured for ', name)


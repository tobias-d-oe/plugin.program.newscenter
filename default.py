#!/usr/bin/python
# -*- coding: utf-8 -*-
###########################################################################
#
#          FILE:  plugin.program.newscenter/default.py
#
#        AUTHOR:  Tobias D. Oestreicher
#
#       LICENSE:  GPLv3 <http://www.gnu.org/licenses/gpl.txt>
#       VERSION:  0.0.1
#       CREATED:  13.02.2016
#
###########################################################################
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
#     CHANGELOG:  (13.02.2016) TDOe - First Publishing
###########################################################################


import os
import sys
import xbmc
import xbmcgui
import json
#import pprint
import urllib2
import urllib
import re
import xbmcaddon
import feedparser
import HTMLParser
from xml.dom.minidom import parse,parseString
#import xml.dom.minidom
#import xml.etree.ElementTree as ElementTree
import xbmcplugin
import datetime

NODEBUG = False




##########################################################################################################################
##
##########################################################################################################################
def debug(content):
    if (NODEBUG):
        return
    print unicode(content).encode("utf-8")


##########################################################################################################################
##
##########################################################################################################################
def getUnicodePage(url):
    req = urllib2.urlopen(url)
    content = ""
    if "content-type" in req.headers and "charset=" in req.headers['content-type']:
        encoding=req.headers['content-type'].split('charset=')[-1]
        content = unicode(req.read(), encoding)
    else:
        content = unicode(req.read(), "utf-8")
    return content

def make_unicode(input):
    if type(input) != unicode:
        input =  input.decode('utf-8')
        return input
    else:
        return input

##########################################################################################################################
##
##########################################################################################################################
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def numbers_to_weekdaystring(argument):
    num2string = {
        0: "Montag",
        1: "Dienstag",
        2: "Mittwoch",
        3: "Donnerstag",
        4: "Freitag",
        5: "Samstag",
        6: "Sonntag"
    }
    return num2string.get(argument, "nothing")




def plz2bundesland(plz):
    BundFile = xbmc.translatePath('special://home/addons/'+addonID+'/BundeslandPLZ.json')
    with open(BundFile, 'r') as PLZTrans:
        content=PLZTrans.read().rstrip('\n').decode('utf-8')
    PLZJson = json.loads(content)
    #debug('plz2bundesland')

    for i in PLZJson:
        if (plz >= i['start']) and (plz <= i['ende']):
            return i['bundesland']
    
def plz2uwzmap(plz):
    Bundesland = plz2bundesland(plz).encode('utf-8')
    #debug("Bundesland=%s" % (Bundesland) )
    if Bundesland == "Bayern":
        pic="http://www.unwetterzentrale.de/images/map/bayern_index.png"
    elif "Baden-W" in Bundesland:
        pic="http://www.unwetterzentrale.de/images/map/badenwuerttemberg_index.png"
    elif (Bundesland == "Brandenburg") or (Bundesland == "Berlin"):
        pic="http://www.unwetterzentrale.de/images/map/brandenburg_index.png"
    elif Bundesland == "Hessen":
        pic="http://www.unwetterzentrale.de/images/map/hessen_index.png"
    elif Bundesland == "Mecklenburg-Vorpommern":
        pic="http://www.unwetterzentrale.de/images/map/meckpom_index.png"
    elif (Bundesland == "Niedersachsen") or (Bundesland == "Bremen"):
        pic="http://www.unwetterzentrale.de/images/map/niedersachsen_index.png"
    elif Bundesland == "Nordrhein-Westfalen":
        pic="http://www.unwetterzentrale.de/images/map/nrw_index.png"
    elif (Bundesland == "Rheinland-Pfalz") or (Bundesland == "Saarland"):
        pic="http://www.unwetterzentrale.de/images/map/rlp_index.png"
    elif Bundesland == "Sachsen":
        pic="http://www.unwetterzentrale.de/images/map/sachsen_index.png"
    elif Bundesland == "Sachsen-Anhalt":
        pic="http://www.unwetterzentrale.de/images/map/sachsenanhalt_index.png"
    elif (Bundesland == "Schleswig-Holstein") or (Bundesland == "Hamburg"):
        pic="http://www.unwetterzentrale.de/images/map/schleswig_index.png"
    elif "ringen" in Bundesland:
        pic="http://www.unwetterzentrale.de/images/map/thueringen_index.png"
    else:
        pic="http://www.unwetterzentrale.de/images/map/deutschland_index.png"
    return pic

##########################################################################################################################
##
##########################################################################################################################
def feed2container(url,headerpic):
    if headerpic == '':
        headerpic='http://www.kokobeet.at/wp-content/uploads/logo_platzhalter.gif'
    feed = feedparser.parse( url )
    WINDOW = xbmcgui.Window( 10000 )
    x=0
    listitems = []
    for item in feed[ "items" ]:
        title = item[ "title" ]
        debug("NewsCenter: Processing Item %s" % (title))
        
        try:
            img = item[ "media_content" ][0][ "url" ]
            if img != '':
                debug("NewsCenter: Image found in media_content: %s" % (img))

        except:
            try:
                ce = item[ "content" ][0][ "value" ]
                #imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(png|gif|jpg|jpeg))[\'"]', ce)
                imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(?<!(gif|img)))[\'"]', ce)
                img = imgsrc.group(1)
                if img != '':
                    debug("NewsCenter: Image found in content: %s" % (img))
            except:
                #imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(png|gif|jpg|jpeg))[\'"]', item[ "summary" ])
                imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(?<!(gif|img)))[\'"]', item[ "summary" ])
                try:
                    img = imgsrc.group(1)
                    if img != '':
                        debug("NewsCenter: Image found in summary: %s" % (img))
                except:
                    debug("NewsCenter: Len %s" % (len(item[ 'links' ])))
                    if len(item[ 'links' ]) >= 1:
                        debug("NewsCenter: Links is array")
                        piclink = ''
                        for link in item[ 'links' ]:
                            debug("NewsCenter: Link= %s" % (link['href']))
                            if re.search('.*(png|jpg|jpeg)', link['href']):
                                debug("Link is pic %s" % (link['href']))
                                piclink = link['href']
                                break
                    if piclink != '':
                        img = str(piclink)
                    else:
                        img = 'http://dzmlsvv5f118.cloudfront.net/wp-content/uploads/2013/04/newsandblogimage.jpg?cc475f'
                    debug("NewsCenter: No Image found!")


        description = item[ "summary" ]
        description = re.sub('<p[^>\\n]*>','\n\n',description)
        description = re.sub('<br[^>\\n]*>','\n',description)
        description = re.sub('<[^>\\n]+>','',description)
        description = re.sub('\\n\\n+','\n\n',description)
        description = re.sub('(\\w+,?) *\\n(\\w+)','\\1 \\2',description)
        description = HTMLParser.HTMLParser().unescape(description).strip()

        pubdate = item[ "published" ]

        json_str = { "Logo": img, "Label": title, "Desc": description, "HeaderPic": headerpic, "Date": pubdate}
        listitems.append( json_str )

    return listitems











##########################################################################################################################
##
##########################################################################################################################
def feed2property(url,headerpic):
    if headerpic == '':
        headerpic='http://www.kokobeet.at/wp-content/uploads/logo_platzhalter.gif'
    feed = feedparser.parse( url )
    WINDOW = xbmcgui.Window( 10000 )
    x=0

    for item in feed[ "items" ]:
        title = item[ "title" ]
        debug("NewsCenter: Processing Item %s" % (title))
        
        try:
            img = item[ "media_content" ][0][ "url" ]
            if img != '':
                debug("NewsCenter: Image found in media_content: %s" % (img))

        except:
            try:
                ce = item[ "content" ][0][ "value" ]
                #imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(png|gif|jpg|jpeg))[\'"]', ce)
                imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(?<!(gif|img)))[\'"]', ce)
                img = imgsrc.group(1)
                if img != '':
                    debug("NewsCenter: Image found in content: %s" % (img))
            except:
                #imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(png|gif|jpg|jpeg))[\'"]', item[ "summary" ])
                imgsrc = re.search('img[^<>\\n]+src=[\'"]([^"\']+(?<!(gif|img)))[\'"]', item[ "summary" ])
                try:
                    img = imgsrc.group(1)
                    if img != '':
                        debug("NewsCenter: Image found in summary: %s" % (img))
                except:
                    debug("NewsCenter: Len %s" % (len(item[ 'links' ])))
                    if len(item[ 'links' ]) >= 1:
                        debug("NewsCenter: Links is array")
                        piclink = ''
                        for link in item[ 'links' ]:
                            debug("NewsCenter: Link= %s" % (link['href']))
                            if re.search('.*(png|jpg|jpeg)', link['href']):
                                debug("Link is pic %s" % (link['href']))
                                piclink = link['href']
                                break
                    if piclink != '':
                        img = str(piclink)
                    else:
                        img = 'http://dzmlsvv5f118.cloudfront.net/wp-content/uploads/2013/04/newsandblogimage.jpg?cc475f'
                    debug("NewsCenter: No Image found!")


        description = item[ "summary" ]
        description = re.sub('<p[^>\\n]*>','\n\n',description)
        description = re.sub('<br[^>\\n]*>','\n',description)
        description = re.sub('<[^>\\n]+>','',description)
        description = re.sub('\\n\\n+','\n\n',description)
        description = re.sub('(\\w+,?) *\\n(\\w+)','\\1 \\2',description)
        description = HTMLParser.HTMLParser().unescape(description).strip()

        pubdate = item[ "published" ]

        WINDOW.setProperty( "LatestNews.%s.Title" % (x), title )
        WINDOW.setProperty( "LatestNews.%s.Desc" % (x), description )
        WINDOW.setProperty( "LatestNews.%s.Logo" % (x), img )
        WINDOW.setProperty( "LatestNews.%s.Date" % (x), pubdate )
        WINDOW.setProperty( "LatestNews.%s.HeaderPic" % (x), headerpic )
        x+=1

    for i in range(x,50):
        WINDOW.clearProperty('LatestNews.%s.Title' % i)
        WINDOW.clearProperty('LatestNews.%s.Desc' % i)
        WINDOW.clearProperty('LatestNews.%s.Logo' % i)
        WINDOW.clearProperty('LatestNews.%s.Date' % i)
        WINDOW.clearProperty('LatestNews.%s.HeaderPic' % i)



##################################################################################################################################################

##########################################################################################################################
##
##########################################################################################################################
def get_ts100_url():
    url = "http://www.tagesschau.de/api/multimedia/video/ondemand100~_type-video.json"

    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data['multimedia'][1]['tsInHundredSeconds']['mediadata'][3]['h264xl']



##########################################################################################################################
##
##########################################################################################################################
def get_ts2000_url():
    url = "http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100~_type-TS2000.json"

    response = urllib.urlopen(url)
    data = json.loads(response.read())
    ts200jsonurl = str(data['latestBroadcastsPerType'][0]['details'])
    response2 = urllib.urlopen(ts200jsonurl)
    data2 = json.loads(response2.read())
    data3 = data2['fullvideo'][0]['mediadata'][5]['h264xl']
    return data3


##########################################################################################################################
##
##########################################################################################################################
def get_mdr_aktuell_130_url():
    url="http://www.ardmediathek.de/tv/MDR-aktuell-Eins30/Sendung?documentId=7545100&bcastId=7545100&rss=true"
    feed = feedparser.parse( url )
    debug("MDR aktuell 130 : %s" % (feed[ "items" ][0]['guid']))
    weblink=feed[ "items" ][0]['guid']
    videoid=re.findall('documentId=(........)',weblink)
    debug(videoid)
    videoid = videoid[0]
    url="http://www.ardmediathek.de/play/media/%s" % (videoid)
    content = getUnicodePage(url)
    mediathekjson = json.loads(content)
    medias = mediathekjson['_mediaArray'][0]['_mediaStreamArray']
    for media in medias:
        if media['_quality'] == 3:
            stream = media['_stream']
    return stream

##########################################################################################################################
##
##########################################################################################################################
def get_tagesschauwetter_url():
    url='http://www.tagesschau.de/api/multimedia/video/ondemand100~_type-video.json'
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    for vid in data['videos']:
        if vid['headline'] == "Die Wetteraussichten":
            for md in vid['mediadata']:
                try:
                    stream=md['h264xl']
                except:
                    pass
    return stream



##########################################################################################################################
##
##########################################################################################################################
def get_wetteronline_url():
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request('http://www.wetteronline.de/wetter-videos', None, headers)
    html = urllib2.urlopen(req).read()
    wetterfile = re.findall('20\d\d\d\d\d\d_...mp4',html)
    url = "rtmp://62.113.210.2/wetteronline-vod/"+wetterfile[0]
    return url

##########################################################################################################################
##
##########################################################################################################################
def get_wetterinfo_url():
    url = "http://dlc3.t-online.de/mflash/wetterstudio_prem.mp4"
    return url


##########################################################################################################################
##
##########################################################################################################################
def get_kinder_nachrichten_url():
    url="https://www.zdf.de/ZDFmediathek/podcast/222528?view=podcast"
    feed = feedparser.parse( url )
    debug("Kinder : %s" % (feed[ "items" ][0]['guid']))
    return feed[ "items" ][0]['guid']


def get_rundschau100_url():
    url="http://redirect.br-online.de/br/bayerisches-fernsehen/rundschau/rsku/rundschaukultur_XL.mp4"
    return url


def get_ndraktuellkompakt_url():
    url="http://www.ndr.de/fernsehen/sendungen/ndr_aktuell/NDR-Aktuell-kompakt-,ndraktuellkompakt110.html"
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(url, None, headers)
    html = urllib2.urlopen(req).read()
    media = re.findall('content="(.+?.hq.mp4)"',html)
    return media[0]

##################################################################################################################################################
# http://de.euronews.com/media/logo-bottom.gif
#
# http://de.euronews.com/import/reg05_summary_today.gif     - Wettervorhersage Heute
# http://de.euronews.com/import/reg05_summary_tonight.gif   - Wettervorhersage Heute Nacht
# http://de.euronews.com/import/reg05_summary_tomorrow.gif  - Wettervorhersage Morgen
# http://de.euronews.com/import/reg05_winds_today.gif       - Wind Heute
# http://de.euronews.com/import/reg05_winds_tonight.gif     - Wind Heute Nacht
# http://de.euronews.com/import/reg05_winds_tomorrow.gif    - Wind Morgen
# http://de.euronews.com/import/reg05_temp_today.gif        - Temperaturen Heute
# http://de.euronews.com/import/reg05_temp_tonight.gif      - Temperaturen Heute Nacht
# http://de.euronews.com/import/reg05_temp_tomorrow.gif     - Temperaturen Morgen
# http://de.euronews.com/import/reg05_precip_today.gif      - Regen Heute
# http://de.euronews.com/import/reg05_precip_tonight.gif    - Regen Heute Nacht
# http://de.euronews.com/import/reg05_precip_tomorrow.gif   - Regen Morgen
##################################################################################################################################################
def get_all_wetter_pic():
    plz = addon.getSetting('plz')
    Bundesland = plz2bundesland(plz).encode('utf-8')
    deutschlanduwz="http://www.unwetterzentrale.de/images/map/deutschland_index.png"
### Ab hier UWZ
    li = xbmcgui.ListItem("Unwetterkarte von %s" % (Bundesland), iconImage=plz2uwzmap(plz))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem("Unwetterkarte von Deutschland", iconImage=deutschlanduwz)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
### Bis hier UWZ
### Ab hier euronews
    li = xbmcgui.ListItem('Wettervorhersage Heute', iconImage='http://de.euronews.com/import/reg05_summary_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Wettervorhersage Heute Nacht', iconImage='http://de.euronews.com/import/reg05_summary_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Wettervorhersage Morgen', iconImage='http://de.euronews.com/import/reg05_summary_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


    li = xbmcgui.ListItem('Wind Heute', iconImage='http://de.euronews.com/import/reg05_winds_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    li = xbmcgui.ListItem('Wind Heute Nacht', iconImage='http://de.euronews.com/import/reg05_winds_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Wind Morgen', iconImage='http://de.euronews.com/import/reg05_winds_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


    li = xbmcgui.ListItem('Temperaturen Heute', iconImage='http://de.euronews.com/import/reg05_temp_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Temperaturen Heute Nacht', iconImage='http://de.euronews.com/import/reg05_temp_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Temperaturen Morgen', iconImage='http://de.euronews.com/import/reg05_temp_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


    li = xbmcgui.ListItem('Regen Heute', iconImage='http://de.euronews.com/import/reg05_precip_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Regen Heute Nacht', iconImage='http://de.euronews.com/import/reg05_precip_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Regen Morgen', iconImage='http://de.euronews.com/import/reg05_precip_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
### Bis hier euronews

    xbmcplugin.endOfDirectory(addon_handle)

    return addon_handle




def get_wetter_pic():

    li = xbmcgui.ListItem('Wettervorhersage Heute', iconImage='http://de.euronews.com/import/reg05_summary_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Wettervorhersage Heute Nacht', iconImage='http://de.euronews.com/import/reg05_summary_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Wettervorhersage Morgen', iconImage='http://de.euronews.com/import/reg05_summary_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


    li = xbmcgui.ListItem('Wind Heute', iconImage='http://de.euronews.com/import/reg05_winds_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    li = xbmcgui.ListItem('Wind Heute Nacht', iconImage='http://de.euronews.com/import/reg05_winds_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Wind Morgen', iconImage='http://de.euronews.com/import/reg05_winds_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


    li = xbmcgui.ListItem('Temperaturen Heute', iconImage='http://de.euronews.com/import/reg05_temp_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Temperaturen Heute Nacht', iconImage='http://de.euronews.com/import/reg05_temp_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Temperaturen Morgen', iconImage='http://de.euronews.com/import/reg05_temp_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


    li = xbmcgui.ListItem('Regen Heute', iconImage='http://de.euronews.com/import/reg05_precip_today.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Regen Heute Nacht', iconImage='http://de.euronews.com/import/reg05_precip_tonight.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    li = xbmcgui.ListItem('Regen Morgen', iconImage='http://de.euronews.com/import/reg05_precip_tomorrow.gif')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

    return addon_handle



def get_uwz(cc,plz):
    Country=cc
    PLZ=plz
    baseurl="http://feed.alertspro.meteogroup.com/AlertsPro/AlertsProPollService.php?method=getWarning&language=de&areaID=UWZ%s%s" % (Country,PLZ)
    req = urllib2.urlopen(baseurl)
    content = req.read().decode('cp1252').encode('utf-8')
    #print baseurl
    #print content
    #debug("addon_handle %s" % (addon_handle))
    #content = getUnicodePage(baseurl)
    UWZWarnings = json.loads(content)
    
    typenames = [{ "type":"1", "name":"unknown"},     # <===== FIX HERE
                 { "type":"2", "name":"sturm"},
                 { "type":"3", "name":"schnee"},
                 { "type":"4", "name":"regen"},
                 { "type":"5", "name":"temperatur"},
                 { "type":"6", "name":"waldbrand"},
                 { "type":"7", "name":"gewitter"},
                 { "type":"8", "name":"strassenglaette"},
                 { "type":"9", "name":"temperatur"},    # 9 = hitzewarnung
                 { "type":"10", "name":"glatteisregen"},
                 { "type":"11", "name":"temperatur"}] #bodenfrost
    severitycolor = [{ "severity":"0", "name":"green"},
                     { "severity":"1", "name":"unknown"}, # <===== FIX HERE
                     { "severity":"2", "name":"unknown"}, # <===== FIX HERE
                     { "severity":"3", "name":"unknown"}, # <===== FIX HERE
                     { "severity":"4", "name":"orange"},
                     { "severity":"5", "name":"unknown"}, # <===== FIX HERE
                     { "severity":"6", "name":"unknown"}, # <===== FIX HERE
                     { "severity":"7", "name":"orange"},
                     { "severity":"8",  "name":"gelb"},
                     { "severity":"9",  "name":"gelb"}, # <===== FIX HERE
                     { "severity":"10",  "name":"orange"},
                     { "severity":"11",  "name":"rot"},
                     { "severity":"12",  "name":"violet"}]
    df = xbmc.getRegion('dateshort')
    tf = xbmc.getRegion('time').split(':')
    DATEFORMAT = df + '  -  ' + tf[0][0:2] + ':' + tf[1] + ' Uhr'

    for UWZWarning in UWZWarnings['results']:
        for tn in typenames:
            #print "-Type %s %s" % (tn['type'],UWZWarning['type'])
            if int(tn['type']) == int(UWZWarning['type']):
                typename = tn['name']
                break
        for sc in severitycolor:
            if int(sc['severity']) == int(UWZWarning['severity']):
                severitycol = sc['name']
                break
        picurl="http://www.unwetterzentrale.de/images/icons/%s-%s.gif" % (typename,severitycol)
        #debug('BBBBBB')
        url="-"
        start = datetime.datetime.fromtimestamp( int(UWZWarning['dtgStart']) ).strftime(DATEFORMAT)
        ende = datetime.datetime.fromtimestamp( int(UWZWarning['dtgEnd']) ).strftime(DATEFORMAT)
        li = xbmcgui.ListItem(UWZWarning['payload']['translationsShortText']['DE'].encode('utf-8'), iconImage=picurl)
        li.setProperty("Start", str(start))
        li.setProperty("Ende", str(ende))
        #li.setProperty("Start", str(UWZWarning['dtgStart']))
        #li.setProperty("Ende", str(UWZWarning['dtgEnd']))
        li.setProperty("Severity", str(UWZWarning['severity']))
        li.setProperty("UWZLevel", str(UWZWarning['payload']['uwzLevel']))
        li.setProperty("Type", typename.capitalize())
        li.setProperty("LongText", UWZWarning['payload']['translationsLongText']['DE'].encode('utf-8'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

#        print "Start: %s" % (UWZWarning['dtgStart'])
#        print "Ende: %s" % (UWZWarning['dtgEnd'])
#        print "Severity: %s" % (UWZWarning['severity'])
#        print "Type: %s" % (UWZWarning['type'])
#        #print UWZWarning['payload']
#        print "UWZLevel: %s" % (UWZWarning['payload']['uwzLevel'])
#        print "LevelName: %s" % (UWZWarning['payload']['levelName'])
#        print "LongText: %s" % (UWZWarning['payload']['translationsLongText']['DE'].encode('utf-8'))
#        print "ShortText: %s" % (UWZWarning['payload']['translationsShortText']['DE'].encode('utf-8'))
#        print "Pic: %s" % (picurl)
#        print "----------"
#    li = xbmcgui.ListItem("Karte", iconImage=plz2uwzmap(addon.getSetting('plz')))
#    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
    return addon_handle


def get_uwz_maps():
    plz = addon.getSetting('plz')
    Bundesland = plz2bundesland(plz).encode('utf-8')
    li = xbmcgui.ListItem("Unwetterkarte von %s" % (Bundesland), iconImage=plz2uwzmap(plz))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    deutschlanduwz="http://www.unwetterzentrale.de/images/map/deutschland_index.png"
    li = xbmcgui.ListItem("Unwetterkarte von Deutschland", iconImage=deutschlanduwz)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)
    return addon_handle








def clear_buli_table():
    WINDOW = xbmcgui.Window( 10000 )
    for i in range(1,25):
            WINDOW.clearProperty( "NewsCenter.Buli.%s.Logo" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.Name" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.Spiele" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.SUN" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.Platz" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.Tore" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.Punkte" % (i))
            WINDOW.clearProperty( "NewsCenter.Buli.%s.StatPic" % (i))





def get_buli_table(liga):
    WINDOW = xbmcgui.Window( 10000 )
    url="http://bulibox.de/abschlusstabellen/%s-Bundesliga.html" % (liga)
    content = getUnicodePage(url)
    content = content.replace("\\","")
    BuliFile = xbmc.translatePath('special://home/addons/'+addonID+'/Buli.json')
    with open(BuliFile, 'r') as Mannschaften:
        BuliMannschaften=Mannschaften.read().rstrip('\n').decode('utf-8')
    MannschaftsID = json.loads(BuliMannschaften)
    debug('get_buli_table')
    m=0
    spl = content.split('<div id="inhalt">')
    spl2 = spl[1]
    spl2 = spl2.split('</table>')
    spl2 = spl2[1]
    spl2 = spl2.split('</tr>')
    for i in spl2:
        out = re.compile('<td>(.+?)</td>', re.DOTALL).findall(i)
        rang = ''
        name= ''
        sun = ''
        tore = ''
        punkte = ''
        spiele = ''
        pic = ''
        statpic = ''
        try:
            rang = out[0]
            debug(rang)
            name = out[1]
            spiele = out[2]
            sun = out[3]
            tore = out[4]
            punkte = out[5]
            statpic = "http://bulibox.de/%s" % (re.compile("src='../(.+?)'", re.DOTALL).findall(out[6])[0])
            for smid in MannschaftsID:
                debug(smid['name'])
                debug(name.replace('&nbsp;',' ').strip())
                if name.replace('&nbsp;',' ').strip() == smid['name']:
                    m+=1
                    debug("FOUND")

                    #pic = "http://sportbilder.t-online.de/fussball/logos/teams/145x145/%s.png" % ( smid['id'] )
                    pic = "BuliLogos/%s.png" % ( smid['id'] )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.Logo" % (m), pic.strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.Name" % (m), name.replace('&nbsp;',' ').strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.Spiele" % (m), spiele.replace('&nbsp;',' ').strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.SUN" % (m), sun.replace('&nbsp;',' ').strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.Platz" % (m), rang.replace('&nbsp;',' ').strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.Tore" % (m), tore.replace('&nbsp;',' ').strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.Punkte" % (m), punkte.replace('&nbsp;',' ').strip() )
                    WINDOW.setProperty( "NewsCenter.Buli.%s.StatPic" % (m), statpic.strip() )
        except:
            pass






def get_buli_table_items(liga):
    listitems = []
    url="http://bulibox.de/abschlusstabellen/%s-Bundesliga.html" % (liga)
    content = getUnicodePage(url)
    content = content.replace("\\","")
    BuliFile = xbmc.translatePath('special://home/addons/'+addonID+'/Buli.json')
    with open(BuliFile, 'r') as Mannschaften:
        BuliMannschaften=Mannschaften.read().rstrip('\n').decode('utf-8')
    MannschaftsID = json.loads(BuliMannschaften)
    debug('get_buli_table')
    m=0
    spl = content.split('<div id="inhalt">')
    spl2 = spl[1]
    spl2 = spl2.split('</table>')
    spl2 = spl2[1]
    spl2 = spl2.split('</tr>')
    for i in spl2:
        out = re.compile('<td>(.+?)</td>', re.DOTALL).findall(i)
        rang = ''
        name= ''
        sun = ''
        tore = ''
        punkte = ''
        spiele = ''
        pic = ''
        statpic = ''
        try:
            rang = out[0]
            debug(rang)
            name = out[1]
            spiele = out[2]
            sun = out[3]
            tore = out[4]
            punkte = out[5]
            statpic = "http://bulibox.de/%s" % (re.compile("src='../(.+?)'", re.DOTALL).findall(out[6])[0])
            for smid in MannschaftsID:
                debug("%s %s == %s" % (rang,smid['name'],name.replace('&nbsp;',' ').strip()))
                #debug(name.replace('&nbsp;',' ').strip())
                if name.replace('&nbsp;',' ').strip() == smid['name']:
                    m+=1
                    debug("FOUND")

                    #pic = "http://sportbilder.t-online.de/fussball/logos/teams/145x145/%s.png" % ( smid['id'] )
                    pic = "%sBuliLogos/%s.png" % ( mediaPath,smid['id'] )
                    debug("Bulilogo = %s" % (pic.strip()))
                    json_str = { "Logo": pic.strip(), "Label": name.replace('&nbsp;',' ').strip(), "Spiele": spiele.replace('&nbsp;',' ').strip(), "SUN": sun.replace('&nbsp;',' ').strip(), "Platz": rang.replace('&nbsp;',' ').strip(), "Tore": tore.replace('&nbsp;',' ').strip(), "Punkte": punkte.replace('&nbsp;',' ').strip(), "StatPic": statpic.strip()}
                    listitems.append( json_str )
        except:
            pass

    return listitems





def get_buli_spielplan_items(liga):
    listitems = []
    url="http://bulibox.de/abschlusstabellen/%s-Bundesliga.html" % (liga)
    content = getUnicodePage(url)
    content = content.replace("\\","")
    BuliFile = xbmc.translatePath('special://home/addons/'+addonID+'/Buli.json')
    with open(BuliFile, 'r') as Mannschaften:
        BuliMannschaften=Mannschaften.read().rstrip('\n').decode('utf-8')
    MannschaftsID = json.loads(BuliMannschaften)
    debug('get_buli_spielplan_items %s' % (liga))
    m=0
    spl = content.split('<div id="inhalt">')
    spl2 = spl[1]
    spl2 = spl2.split('</table>')
    spl2 = spl2[0]
    spl2 = spl2.split("<table border=1 align=center style='width:400; text-align: left' cellpadding='4px'>")
    spl2 = spl2[1]
    spl2 = spl2.split('</tr>')

    for i in spl2:
        out = re.compile('<td>(.+?)</td>', re.DOTALL).findall(i)
        spieldatum = ''
        mannschaft1 = ''
        mannschaft2 = ''
        ergebniss = ''
        mannschaft1logo =''
        mannschaft2logo =''
        try:
            spieldatum = out[0]
            mannschaft1 = out[1]
            mannschaft2 = out[2]
            ergebniss = out[3]
            for smid in MannschaftsID:
                #print "%s - %s" % (name,smid['name'])
                if mannschaft1.replace('&nbsp;',' ').strip() == smid['name']:
                    #mannschaft1logo = "http://sportbilder.t-online.de/fussball/logos/teams/145x145/%s.png" % ( smid['id'] )
                    mannschaft1logo = "%sBuliLogos/%s.png" % ( mediaPath,smid['id'] )
                if mannschaft2.replace('&nbsp;',' ').strip() == smid['name']:
                    mannschaft2logo = "%sBuliLogos/%s.png" % ( mediaPath,smid['id'] )

            spieldatum = spieldatum.replace('&nbsp;',' ').strip()
            mannschaft1 = mannschaft1.replace('&nbsp;',' ').strip()
            mannschaft2 = mannschaft2.replace('&nbsp;',' ').strip()
            ergebniss = ergebniss.replace('&nbsp;',' ').strip()
            json_str = { "Logo": icon, "Label": "Buli Spielplan", "Spieldatum": spieldatum, "Mannschaft1": mannschaft1, "Mannschaft2": mannschaft2, "Ergebniss": ergebniss, "Mannschaft1Logo": mannschaft1logo, "Mannschaft2Logo": mannschaft2logo}
            listitems.append( json_str )
        except:
            pass

    return listitems



def get_pollen_items():
    plz = addon.getSetting('plz')
    url="http://www.allergie.hexal.de/pollenflug/xml-interface-neu/pollen_de_7tage.php?plz=%s" % (plz)
    response = urllib.urlopen(url)
    dom = parseString(response.read())
    url='-'
    for node in dom.getElementsByTagName('pollenbelastungen'):
        Tag = node.getAttribute("tag")
        if Tag == "0":
            tagname="Heute"
        if Tag == "1":
            tagname="Morgen"
        if Tag == "2":
            tagname="Übermorgen"
        else:
            tagname=numbers_to_weekdaystring((datetime.date.today() + datetime.timedelta(int(Tag))).weekday())
        debug("Listitem - %s" % (tagname.decode('utf-8')))
        li = xbmcgui.ListItem("Tag %s" % (Tag), iconImage=icon)
        for snode in node.getElementsByTagName('pollen'):
            Name = snode.getAttribute("name").encode('utf-8').replace('ß','ss').replace('ä','ae')
            Belastung = snode.getAttribute("belastung")
            debug("Property %s - %s" % (Name,Belastung))
            li.setProperty(Name, Belastung)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
    return addon_handle





def show_bulispielplan(liga):
    debug('Set details to info screen %s' % liga)
    if liga == '':
        liga=1
    DETAILWIN = xbmcgui.WindowXMLDialog('bulilist-spielplan-DialogWindow.xml', addonDir, 'Default', '720p')
    DETAILWIN.doModal()






def show_bulilist(liga,seite):
    debug('Set details to info screen')
    clear_buli_table()
    if liga == '':
        liga=1
    if seite == '':
        seite = 1
    get_buli_table(liga)
    if seite != 1:
        #DETAILWIN = xbmcgui.WindowXMLDialog('bulilist-S2-DialogWindow.xml', addonDir, 'Default', '720p')
        DETAILWIN = xbmcgui.WindowXMLDialog('bulilist-platzierung-DialogWindow.xml', addonDir, 'Default', '720p')
    else:
#        DETAILWIN = xbmcgui.WindowXMLDialog('bulilist-S1-DialogWindow.xml', addonDir, 'Default', '720p')
        DETAILWIN = xbmcgui.WindowXMLDialog('bulilist-platzierung-DialogWindow.xml', addonDir, 'Default', '720p')
    DETAILWIN.doModal()







##########################################################################################################################
##
##########################################################################################################################
def set_LatestDokus_to_Home(url):
    WINDOW = xbmcgui.Window( 10000 )
    content = str(getUnicodePage(url))
    NewDokus = json.loads(content)
    NewDokus = NewDokus['dokus']
    x=0
    for Doku in NewDokus:
        WINDOW.setProperty( "LatestDocu.%s.Title" % (x), Doku['title'] )
        WINDOW.setProperty( "LatestDocu.%s.Thumb" % (x), Doku['cover'] )
        WINDOW.setProperty( "LatestDocu.%s.Path" % (x),  'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % (Doku['youtubeId']) )
        WINDOW.setProperty( "LatestDocu.%s.Tags" % (x),  Doku['dokuSrc'] )
        x+=1

##########################################################################################################################
##
##########################################################################################################################
def clear_LatestDokus_at_Home():
    WINDOW = xbmcgui.Window( 10000 )
    for i in range(1,25):
        WINDOW.clearProperty('LatestDocu.%s.Title' % i)
        WINDOW.clearProperty('LatestDocu.%s.Thumb' % i)
        WINDOW.clearProperty('LatestDocu.%s.Path' % i)
        WINDOW.clearProperty('LatestDocu.%s.Tags' % i)



##################################################################################################################################################

##########################################################################################################################
##########################################################################################################################
##
##                                                       M  A  I  N
##
##########################################################################################################################
##########################################################################################################################




##########################################################################################################################
## Get starting methode
##########################################################################################################################
debug("NewsCenter sysargv: "+str(sys.argv))

addon               = xbmcaddon.Addon()
addonID             = addon.getAddonInfo('id')
addonFolder         = downloadScript = xbmc.translatePath('special://home/addons/'+addonID).decode('utf-8')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID).decode('utf-8')
translation         = addon.getLocalizedString
mediaPath           = xbmc.translatePath('special://home/addons/'+addonID+'/resources/skins/Default/media/')



FeedFile = xbmc.translatePath('special://home/addons/'+addonID+'/NewsFeeds.json').decode('utf-8')
with open(FeedFile, 'r') as feeds:
    ConfigFeeds=feeds.read().rstrip('\n')

BuliFile = xbmc.translatePath('special://home/addons/'+addonID+'/Buli.json') #.decode('utf-8')
with open(BuliFile, 'r') as Mannschaften:
    BuliMannschaften=Mannschaften.read().rstrip('\n').decode('utf-8')


addonDir   = addon.getAddonInfo("path")
XBMC_SKIN  = xbmc.getSkinDir()
icon       = os.path.join(addonFolder, "icon.png")#.encode('utf-8')
WINDOW     = xbmcgui.Window( 10000 )

enableinfo  = addon.getSetting('enableinfo')
#print sys.argv[2]

if len(sys.argv)==3:
    addon_handle = int(sys.argv[1])
    params = parameters_string_to_dict(sys.argv[2])
    methode = urllib.unquote_plus(params.get('methode', ''))
    buliliga = urllib.unquote_plus(params.get('buliliga', ''))
    bulipage = urllib.unquote_plus(params.get('bulipage', ''))
    url = urllib.unquote_plus(params.get('url', ''))
    headerpic = urllib.unquote_plus(params.get('headerpic', ''))
elif len(sys.argv)>1:
    params = parameters_string_to_dict(sys.argv[1])
    methode = urllib.unquote_plus(params.get('methode', ''))
    buliliga = urllib.unquote_plus(params.get('buliliga', ''))
    bulipage = urllib.unquote_plus(params.get('bulipage', ''))
    url = urllib.unquote_plus(params.get('url', ''))
    headerpic = urllib.unquote_plus(params.get('headerpic', ''))

else:
    methode = None
    buliliga = 1
    bulipage =1

debug("Methode in Script: %s" % methode )
debug(methode)

## Service
if methode=='start_service':
        WINDOW.setProperty( "LatestNews.Service", "active" )
elif methode=='stop_service':
        WINDOW.setProperty( "LatestNews.Service", "inactive" )

## Skinmode
elif methode=='set_skinmode':
        addon.setSetting('skinnermode', 'true')
elif methode=='unset_skinmode':
        addon.setSetting('skinnermode', 'false')

## Play Videos
elif methode=='play_tagesschau':
        debug("NewsCenter: Play Tagesschau")
        url=get_ts2000_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')') 

elif methode=='play_tagesschau_100':
        debug("NewsCenter: Play Tagesschau 100s")
        url=get_ts100_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_wetteronline':
        debug("NewsCenter: Play Wetter Online")
        url=get_wetteronline_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_wetterinfo':
        debug("NewsCenter: Play Wetter Info")
        url=get_wetterinfo_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_tagesschauwetter':
        debug("NewsCenter: Play Tagesschau Wetter")
        url=get_tagesschauwetter_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_kinder_nachrichten':
        debug("NewsCenter: Play Kinder Nachrichten")
        url=get_kinder_nachrichten_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_mdr_aktuell_130':
        debug("NewsCenter: Play MDR130 Nachrichten")
        url=get_mdr_aktuell_130_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_rundschau100':
        debug("NewsCenter: Play Rundschau 100s Nachrichten")
        url=get_rundschau100_url()
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')

elif methode=='play_ndraktuellkompakt':
        debug("NewsCenter: Play NDR aktuell kompakt Nachrichten")
        url=get_ndraktuellkompakt_url()
        debug(url)
        xbmc.executebuiltin('XBMC.PlayMedia('+url+')')



# Selects
elif methode=='show_select_dialog':
    debug('Methode: show select dialog')
    allfeeds = json.loads(str(ConfigFeeds))
    feedname=[]
    for f in allfeeds:
        feedname.append(f['name'])
    dialog = xbmcgui.Dialog()
    ret = dialog.select("News Auswahl",feedname)
    headerpic=allfeeds[ret]['pic']
    url=allfeeds[ret]['url']
    notifyheader= str(translation(30010))
    xbmc.executebuiltin('XBMC.Notification('+notifyheader+', "Update Latest News Feed - Dieser Vorgang kann etwas dauern... bitte Geduld." ,8000,'+icon+')')
    feed2property(url, headerpic)

elif methode=='show_buli_select':
    debug('Methode: show select dialog bundesliga')
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Sport Auswahl", ["Tabelle 1. Bundesliga", "Tabelle 2. Bundesliga", "Ergebnisse 1. Bundesliga", "Ergebnisse 2. Bundesliga"])
    if ret == 0:
        WINDOW.setProperty("NewsCenter.Buli.LigaInfo", "1" )
        debug("Buli - 1. Button")
        show_bulilist(1,1)        
    elif ret == 1:
        WINDOW.setProperty("NewsCenter.Buli.LigaInfo", "2" )
        debug("Buli - 2. Button")
        show_bulilist(2,1)
    elif ret == 2:
        WINDOW.setProperty("NewsCenter.Buli.LigaInfo", "1" )
        debug("Buli - 3. Button")
        show_bulispielplan("1")
    elif ret == 3:
        WINDOW.setProperty("NewsCenter.Buli.LigaInfo", "2" )
        debug("Buli - 4. Button")
        show_bulispielplan(2)




elif methode=='set_default_feed':
    debug('Methode: set default feed')
    allfeeds = json.loads(str(ConfigFeeds))
    feedname=[]
    for f in allfeeds:
        feedname.append(f['name'])

    dialog = xbmcgui.Dialog()
    ret = dialog.select("Default News Auswahl",feedname)
    defaultfeedname=allfeeds[ret]['name']
    addon.setSetting('storedefault',defaultfeedname)

elif methode=='show_bulilist':
    show_bulilist(buliliga,bulipage)

# Container
elif methode=='get_buli_spielplan_items':
    debug("Buliliga = %s" % buliliga)
    spielelist = get_buli_spielplan_items(buliliga)
    url = '-'
    for sitem in spielelist:
        # 
        li = xbmcgui.ListItem(sitem['Label'], iconImage=sitem['Logo'])
        li.setProperty("Spieldatum", str(sitem['Spieldatum']))
        li.setProperty("Mannschaft1", sitem['Mannschaft1'])
        li.setProperty("Mannschaft2", sitem['Mannschaft2'])
        li.setProperty("Mannschaft1Logo", sitem['Mannschaft1Logo'])
        li.setProperty("Mannschaft2Logo", sitem['Mannschaft2Logo'])
        li.setProperty("Ergebniss", str(sitem['Ergebniss']))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)


elif methode=='get_buli_table_items':
    debug("NewsCenter: in get_buli_table_items and liga is %s" % (buliliga) )
    bulilist = get_buli_table_items(buliliga)
    #debug(bulilist)
    #addon_handle = "NewsCenter.Buli"
    url = '-'
    for sitem in bulilist:
        Logo = sitem['Logo']
        Logo = Logo.encode('utf-8')
        # { "Logo": pic, "Label": name, "Spiele": spiele, "SUN": sun, "Platz": rang, "Tore": tore, "Punkte": punkte, "StatPic": statpic }
        debug("In get_buli_table_items: PIC = %s" % (sitem['Logo']))
        li = xbmcgui.ListItem(sitem['Label'], iconImage=Logo)
        li.setProperty("Spiele", str(sitem['Spiele']))
        li.setProperty("SUN", sitem['SUN'])
        li.setProperty("Platz", str(sitem['Platz']))
        li.setProperty("Tore", str(sitem['Tore']))
        li.setProperty("Punkte", str(sitem['Punkte']))
        li.setProperty("StatPic", str(sitem['StatPic']))
        li.setProperty("Logo", str(sitem['Logo']))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)





elif methode=='get_feed_items':
    debug("NewsCenter: in get_feed_items %s - %s" % (url,headerpic) )
    # Latest News Feed
    allfeeds = json.loads(str(ConfigFeeds))
    storedefault=addon.getSetting('storedefault')
    if storedefault != '':
        for f in allfeeds:
            if f['name'] == storedefault:
                url=f['url']
                pic=f['pic']
                break
    else:
        url="http://www.kodinerds.net/index.php/BoardFeed/?at=30575-8e710f12c83d6c7f66184ca3354f2c83baf4bbed"
        pic="http://www.kodinerds.net/images/wbbLogo.png"

    feedjson = feed2container(url, pic)
    for sitem in feedjson:
        # { "Logo": img, "Label": title, "Desc": description, "HeaderPic": headerpic, "Date": pubdate}
        li = xbmcgui.ListItem(sitem['Label'], iconImage=sitem['Logo'])
        li.setProperty("Desc", sitem['Desc'])
        li.setProperty("HeaderPic", sitem['HeaderPic'])
        li.setProperty("Date", sitem['Date'])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)


elif methode=='get_wetter_pics':
        get_wetter_pic()

elif methode=='get_all_wetter_pics':
        get_all_wetter_pic()

elif methode=='get_pollen_items':
        debug("Auswahl Pollenitems")
        get_pollen_items()

elif methode=='get_unwetter_warnungen':
        if addon.getSetting('plz') != '':
            get_uwz("DE", addon.getSetting('plz'))
        else:
            notifyheader= str(translation(30010))
            xbmc.executebuiltin('XBMC.Notification('+notifyheader+', "Bitte PLZ in den Einstellungen festlegen" ,4000,'+icon+')')

elif methode=='get_uwz_maps':
        get_uwz_maps()

# Default Entry
elif methode==None:
        WINDOW.setProperty( "LatestNews.Service", "active" )
        notifyheader= str(translation(30010))
        notifytxt   = str(translation(30108))
        xbmc.executebuiltin('XBMC.Notification('+notifyheader+', '+notifytxt+' ,4000,'+icon+')')
        # Dokus
        url="http://doku.cc/api.php?get=new-dokus&page=1"
        clear_LatestDokus_at_Home()
        set_LatestDokus_to_Home(url)
 
        # Latest News Feed
        allfeeds = json.loads(str(ConfigFeeds))
        storedefault=addon.getSetting('storedefault')
        if storedefault != '':
            for f in allfeeds:
                if f['name'] == storedefault:
                    url=f['url']
                    pic=f['pic']
                    break
        else:
            url="http://www.kodinerds.net/index.php/BoardFeed/?at=30575-8e710f12c83d6c7f66184ca3354f2c83baf4bbed"
            pic="http://www.kodinerds.net/images/wbbLogo.png"
        feed2property(url, pic)
 

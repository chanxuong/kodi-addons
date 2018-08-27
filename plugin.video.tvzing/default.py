import urlparse
import urllib
import urllib2
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import urlfetch
import re
import json
from StringIO import StringIO
import gzip
from BeautifulSoup import BeautifulSoup

try:
    import json
except:
    import simplejson as json

__settings__ = xbmcaddon.Addon(id='plugin.video.phimonline')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
videoQuality = __settings__.getSetting('quality')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )




def make_request(url, headers=None):
	if headers is None:
			headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
								 'Referer' : 'http://www.google.com'}
	try:
			if 'tv.zing.vn' not in url:
				url = 'https://tv.zing.vn' + url 
			url = url.replace(' ', '+')
			req = urllib2.Request(url,headers=headers)
			response = urllib2.urlopen(req)
			if response.info().get('Content-Encoding') == 'gzip':
				buf = StringIO(response.read())
				f = gzip.GzipFile(fileobj=buf)
				data = f.read()
				return data
			else:
				body=response.read()
				return body
	except urllib2.URLError, e:
			print 'We failed to open "%s".' % url
			if hasattr(e, 'reason'):
					print 'We failed to reach a server.'
					print 'Reason: ', e.reason
			if hasattr(e, 'code'):
					print 'We failed with error code - %s.' % e.code

def get_categories():
	content = make_request('https://tv.zing.vn')
	
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	mainNav = soup.find('div', {'class' : 'main-nav'})
	if mainNav is not None:
		print 'Main Nav'
		subNavs = mainNav.findAll('div', {'class': lambda x: x 
                       and 'sub-nav' in x.split()
             })
		for subNav in subNavs:
			print 'Sub Navs'
			items = subNav.findAll('a')
			for item in items:
				try:
					add_dir(item['title'],item['href'],1,icon,1)
				except:
					pass
			
def search():
	kb =xbmc.Keyboard ('', 'Enter keyword', False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		url = 'http://www.phimmedia.tv/index.php?keyword=' + text + '&do=phim&act=search'
		content = make_request(url)
		soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
		listPhim = soup.find('ul', {'class' : 'list-film'})
		if listPhim is not None:
			items = listPhim.findAll('li')
			for item in items:
				itemDiv = item.find('div', {'class' : 'name'})
				itemImage = item.find('img')
				if itemDiv is not None:
					itemLink = itemDiv.find('a')
					try:
						add_dir(itemLink['title'],itemLink['href'],2,itemImage['src'].replace("show_image.php?file=","").replace("&w=300&h=400",""),1)
					except:
						pass

def get_category(url):
	content = make_request(url)
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	items = soup.findAll('div', {'class':'item'})
	for item in items:
		itemThumb = item.find('a', {'class':'thumb'})
		itemImage = itemThumb.find('img')
		itemTitle = item.find('h2')
		itemLink = itemTitle.find('a')
		if itemLink is not None:
			
			try:
				add_dir(itemLink['title'],itemLink['href'],2,itemImage['src'],1)
			except:
				pass
	paging = soup.find('div', {'class' : 'paging'})
	
		

	

def get_episodes(url):
	content = make_request(url)
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	divTaps = soup.findAll('div', {'itemprop' : 'episode'})
	if divTaps is not None:
		for divTap in divTaps:
			divDesc = divTap.find('div', {'class':'description'})
			link = divDesc.find('a')
			add_link(link['title'], link['href'], icon)




def add_link(name, href, thumb):
	u=sys.argv[0]+"?url="+urllib.quote_plus(href.encode('utf8'))+"&mode=3"
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={ "Title": name})
	liz.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)



def add_dir(name,url,mode,iconimage,pagenum):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url.encode('utf8'))+"&mode="+str(mode)+"&pagenum="+str(pagenum)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok
	

def resolve_url(url):
	content = make_request(url)
	ok=True
	url = None
	
	for line in content.splitlines():
		s = line.strip()
		if s.find('source:') >= 0:
			
			startIndex = s.index('"')+1
			endIndex = s.index('"', startIndex+1)
			url = s[startIndex:endIndex]
			break
		
	if url is not None:
		item = xbmcgui.ListItem(path=url)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
	return ok	

	
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]

	return param

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

params=get_params()

url=''
name=None
mode=None
pagenum=None
try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
try:
	pagenum=int(params["pagenum"])
except:
	pass


if mode==None:
	#if not login():
	#	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	#else:	
	get_categories()

elif mode==1:
	get_category(url)
elif mode==2:
	get_episodes(url)
elif mode==3:
	resolve_url(url)
elif mode==4:
	search()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
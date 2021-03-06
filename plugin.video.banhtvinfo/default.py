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
from BeautifulSoup import BeautifulSoup

try:
    import json
except:
    import simplejson as json

__settings__ = xbmcaddon.Addon(id='plugin.video.banhtvinfo')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
videoQuality = __settings__.getSetting('quality')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )




def make_request(url, headers=None):
	if headers is None:
			headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
								 'Referer' : 'http://www.google.com'}
	try:
			url = url.replace(' ', '+')
			req = urllib2.Request(url,headers=headers)
			f = urllib2.urlopen(req)
			body=f.read()
			return body
	except urllib2.URLError, e:
			print 'We failed to open "%s".' % url
			if hasattr(e, 'reason'):
					print 'We failed to reach a server.'
					print 'Reason: ', e.reason
			if hasattr(e, 'code'):
					print 'We failed with error code - %s.' % e.code

def get_categories():
	add_dir('Phim Bo', 'http://banhtv.info/phim-bo/', 1, icon, 1)
	add_dir('Phim Bo Viet Nam', 'http://banhtv.info/phim-bo/vietnam/', 1, icon, 1)
	add_dir('Phim Bo Hong Kong', 'http://banhtv.info/phim-bo/hk/', 1, icon, 1)
	add_dir('Phim Bo Trung Quoc', 'http://banhtv.info/phim-bo/cn/', 1, icon, 1)
	add_dir('Phim Bo Han Quoc', 'http://banhtv.info/phim-bo/kr/', 1, icon, 1)
	add_dir('Phim Le', 'http://banhtv.info/phim-le/', 1, icon, 1)
	add_dir('Search', '', 4, icon, 1)
	
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
	listPhim = soup.find('ul', {'class' : 'last-film-box'})
	if listPhim is not None:
		items = listPhim.findAll('li')
		for item in items:
			divImage = item.find('div', {'class': 'public-film-item-thumb ratio-content'})
			
			imageUrl = divImage['style'].split("url('")[1].split("')")[0]
			itemLink = item.find('a')
			try:
				add_dir(itemLink['title'],itemLink['href'],2,imageUrl,1)
			except:
				pass
	paging = soup.find('ul', {'class' : 'pagination pagination-lg'})
	if paging is not None:
		pages = paging.findAll('li')
		nextPage = pages[-1]
		nextPageLink = nextPage.find('a')
		add_dir('--Next--', nextPageLink['href'], 1, icon, 1)
		

	

def get_episodes(url):
	filmUrl = url + "xem-phim.html"
	
	content = make_request(filmUrl)
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	
	episodes = soup.findAll('li', {'class': lambda x: x 
                       and 'episode' in x.split()
             })
	if episodes is not None:
		for eps in episodes:
			episodeContainer = eps.parent
			serverContainer = episodeContainer.parent
			serverName = serverContainer.find("h3")
			link = eps.find('a')
			if link is not None:
				add_link(link['title'] + " (" + serverName.text + ")", link['data-id'], link['data-hash'], icon)
	




def add_link(name, id, hash, thumb):
	u=sys.argv[0]+"?id="+urllib.quote_plus(id.encode('utf8'))+"&hash="+urllib.quote_plus(hash.encode('utf8'))+"&mode=3"
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
	

def resolve_url(id, hash):
	print 'testtest'
	requestUrlHeaders = {'Content-Type':'application/x-www-form-urlencoded'}
	form_fields = {
				"id": id,
				"link": hash,
	}

	response = urlfetch.fetch(
				url = 'http://banhtv.info/ajax/player',
				method='POST',
				headers = requestUrlHeaders,
				data=form_fields,
				follow_redirects = False
	)
	data =  json.loads(response.content)
	print 'test', response.content
	ok=True
	url = None
	if data['playTech'] == 'iframe':
		if data['link'] is not None:
			content = make_request('http://banhtv.info/iframe/?link=' + data['link'])
			jsonData = content.split("JSON.parse('")[1].split("');")[0]
			links = json.loads(jsonData)
			print 'test88', jsonData
			for link in links:
				if link['type'] == "mp4":
					item = xbmcgui.ListItem(path=link['file'])
					xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
					break
	else:
		if data['link'] is not None:
			item = xbmcgui.ListItem(path=data['link'][0]['file'])
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
id=None
hash=None
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
	id=urllib.unquote_plus(params["id"])
except:
	pass
try:
	hash=urllib.unquote_plus(params["hash"])
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

	resolve_url(id, hash)
elif mode==4:
	search()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
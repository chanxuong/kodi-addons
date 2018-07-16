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

__settings__ = xbmcaddon.Addon(id='plugin.video.vntvnet')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
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

def get_channels():
	content = make_request('http://vn.tvnet.gov.vn/kenh-truyen-hinh/danh-sach')
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	channel_list = soup.find('ul', {'class' : 'listing channel clearfix'})
	if channel_list is not None:
		items = channel_list.findAll('li')
		for item in items:
			item_link = item.find('a')
			if item_link is not None:
				item_image = item_link.find('img')
				item_url = item_link['href']
				item_name = item_url[item_url.rfind('/')+1:]
				if item_image is not None:
					add_vntvnetlink(item_name, 'http://vn.tvnet.gov.vn' + item_link['href'] + '?re=1', item_image['src'])
				else:
					add_vntvnetlink(item_name, 'http://vn.tvnet.gov.vn' + item_link['href'], icon)
	add_directurl('ANTV', 'http://antvlive.ab5c6921.cdnviet.com/antvmobile/playlist.m3u8', 'http://img.hplus.com.vn/460x260/poster/2018/06/05/524177-anninh.png')
	add_hpluslink('HTV2', 'http://hplus.com.vn/xem-kenh-htv2-hd-2669.html', 'http://img.hplus.com.vn/460x260/poster/2018/06/05/857149-HTV2.png')
	add_hpluslink('HTV3', 'http://hplus.com.vn/xem-kenh-htv3-2535.html', 'http://img.hplus.com.vn/460x260/poster/2018/06/05/750643-HTV3.png')
	add_hpluslink('HTV3', 'http://hplus.com.vn/xem-kenh-htv3-2535.html', 'http://img.hplus.com.vn/460x260/poster/2018/06/05/750643-HTV3.png')

def add_directurl(name, href, thumb):
	u=sys.argv[0]+"?url="+urllib.quote_plus(href.encode('utf8'))+"&mode=2"
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={ "Title": name})
	liz.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def add_vntvnetlink(name, href, thumb):
	u=sys.argv[0]+"?url="+urllib.quote_plus(href.encode('utf8'))+"&mode=1"
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={ "Title": name})
	liz.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
def add_hpluslink(name, href, thumb):
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
	

def resolve_vntvneturl(url):
	ok=True
	content = make_request(url)
	
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	player_div = soup.find('div', {'id' : 'mediaplayer'})
	if player_div is not None:
		data_file = player_div['data-file']
		if data_file is not None:
			content = make_request(data_file)
			streams = json.loads(str(content))
			stream = streams[0]
			item = xbmcgui.ListItem(path=stream['url'])
			xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
	return ok	
def resolve_directurl(url):
	print 'resolve direct url'
	ok=True
	item = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
	return ok	
def resolve_hplusurl(url):
	ok=True
	content = make_request(url)
	
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	link_input = soup.find('input', {'id' : 'link-live'})
	if link_input is not None:
	
		video_url = link_input['value']
		if video_url is not None:
			headers = {
				'Accept':'*/*'
				
			}
			form_fields = {
				"type": 1,
				"is_mobile": 0,
				"url": video_url
			}

			
			response = urlfetch.fetch(
				url = 'http://hplus.com.vn/content/getlinkvideo/',
				method='POST',
				headers = headers,
				data=form_fields,
				follow_redirects = False
			)
			
			print 'test: ', response.content
			item = xbmcgui.ListItem(path= response.content)
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
	get_channels()

elif mode==1:
	resolve_vntvneturl(url)
elif mode==2:
	resolve_directurl(url)
elif mode==3:
	resolve_hplusurl(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
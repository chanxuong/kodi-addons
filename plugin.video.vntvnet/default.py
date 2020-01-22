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
def get_categories():
	add_dir('TV Truc Tuyen', '', 2, icon, 1);
	add_dir('Videos', '', 3, icon, 1);
	
def get_videocategories():
	content = make_request('http://au.tvnet.gov.vn/video/the-loai/1/bo-loc')
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	video_categories_select = soup.find('select', {'class' : 'form filter-cate form-select'})
	if video_categories_select is not None:
		items = video_categories_select.findAll('option')
		for item in items:
			item_option_value = item['value']
			if item_option_value != '0':
				add_dir(item.text,'http://au.tvnet.gov.vn/video/the-loai/' + item_option_value + '/bo-loc',4,icon,1)
def get_videosincategory(url, pagenum):
	content = make_request(url + '?page=' + str(pagenum))
	soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
	videos_container = soup.find('ul', {'class' : 'listing vod clearfix'})
	if videos_container is not None:
		items = videos_container.findAll('li')
		for item in items:
			item_link = item.find('a', {'class': 'thumbnail'})
			item_header = item.find('h3')
			if item_header is not None and item_link is not None:
				item_url = item_link['href']
				item_link_background = item_link['style']
				item_image = item_link_background.replace('background-image:url(', '').replace(');', '')
				item_header_link = item_header.find('a')
				add_videolink(item_header_link.text,'http://au.tvnet.gov.vn' + item_url,item_image)
	if pagenum > 1:
		add_dir('Previous Page', url,4,icon,pagenum-1)
	load_more_button = soup.find('a', {'class' : 'btn-more btn-loadmore'})
	if load_more_button is not None:
		add_dir('Next Page', url,4,icon,pagenum+1)
def get_channels():
	content = make_request('http://au.tvnet.gov.vn/kenh-truyen-hinh/danh-sach')
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
					add_vntvnetlink(item_name, 'http://au.tvnet.gov.vn' + item_link['href'] + '?re=1', item_image['src'])
				else:
					add_vntvnetlink(item_name, 'http://au.tvnet.gov.vn' + item_link['href'], icon)
	

def add_vntvnetlink(name, href, thumb):
	u=sys.argv[0]+"?url="+urllib.quote_plus(href.encode('utf8'))+"&mode=5"
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
	liz.setInfo(type="Video", infoLabels={ "Title": name})
	liz.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

def add_videolink(name, href, thumb):
	u=sys.argv[0]+"?url="+urllib.quote_plus(href.encode('utf8'))+"&mode=1"
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
def resolve_video(url):
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
	resolve_vntvneturl(url)
elif mode==2:
	get_channels()
elif mode==3:
	get_videocategories()
elif mode==4:
	get_videosincategory(url, pagenum)
elif mode==4:
	resolve_video(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
# -*- coding: utf-8 -*-
import sys
import os
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json
import hashlib 
import datetime
import re
from bs4 import BeautifulSoup
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'resources', 'lib'))

from requestutil import Request
import xbmc_helper as XbmcHelper

_baseurl_ = sys.argv[0]
_handle_ = int(sys.argv[1])
_domain_ = "http://movies.hdviet.com"
_request_header_ = {
        'Referer': _domain_,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
}
_isloggedin_ = False
_addon_ = addon = xbmcaddon.Addon()
_request_ = Request(_request_header_, session=True)


def list_categories():
	# Set plugin category. It is displayed in some skins as the name
	# of the current section.
	xbmcplugin.setPluginCategory(_handle_, 'HDViet')
	# Set plugin content. It allows Kodi to select appropriate views
	# for this type of content.
	xbmcplugin.setContent(_handle_, 'videos')
	playableMenu = 
	playableMenu.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(_handle_, get_url(action='quickplay'), xbmcgui.ListItem(label='Quick Play...'), True)
	xbmcplugin.addDirectoryItem(_handle_, get_url(action='quickplay'), xbmcgui.ListItem(label='Get Folder...'), True)
	
	xbmcplugin.endOfDirectory(_handle_)

def list_movies(url):
	if _addon_.getSetting('Username') != '' or _addon_.getSetting('Password') != '': 
		login()
	xbmcplugin.setPluginCategory(_handle_, 'HDViet')
	xbmcplugin.setContent(_handle_, 'movies')
	response = _request_.get(url)
	
	soup = BeautifulSoup(response, "html.parser")
	for item in soup.select('.box-movie-list > li'):
		print('test')
		# Create a list item with a text label and a thumbnail image.
		item_link = item.select_one('a.mv-namevn')
		list_item = xbmcgui.ListItem(label=item_link.get_text())
		# Set additional info for the list item.
		# 'mediatype' is needed for skin to display info for this ListItem correctly.
		#list_item.setInfo('video', {'title': item_link.get_text()})
		# Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
		thumb = item.select_one('img')
		list_item.setProperty('fanart_image', thumb.get('src').replace('124x184', 'origins'))
		list_item.setArt({'thumb': thumb.get('src').replace('124x184', 'origins')})
		plot = item.select_one('span.cot1')
		
		list_item.setInfo('video', {'title': item_link.get_text(), 'plot': plot.get_text(), 'mediatype': 'movie'})
		year = item.select_one('label.vl-chil-date')
		if year is not None:
			list_item.setInfo('video', {'year': year.get_text()})
			
		rating = item.select_one('span.fl-left > span')
		if rating is not None:
			rating = re.search("^(\d*\.?\d)", rating.get_text()).group(1)
			list_item.setInfo('video', {'rating': rating})
			
		directorsAndActors = item.select('span.chil-datef > label.vl-chil-date')
		if directorsAndActors is not None:
			if len(directorsAndActors) > 0:
				actors = directorsAndActors[0].select('a')
				actorNames = []
				for a in actors:
					
					actorNames.append(a.get_text())
				list_item.setInfo('video', {'cast': actorNames})
			if len(directorsAndActors) > 1:
				directors = directorsAndActors[1].select('a')
				directorNames = []
				for a in actors:
					directorNames.append(a.get_text())
				list_item.setInfo('video', {'director': directorNames})
		# Set 'IsPlayable' property to 'true'.
		# This is mandatory for playable items!
		labelchap = item.select_one('span.labelchap2')
		if labelchap is None:
			list_item.setProperty('IsPlayable', 'true')
			url = get_url(action='play', url=item_link.get('href'))
			xbmcplugin.addDirectoryItem(_handle_, url, list_item, False)
		else:
			
			list_item.setProperty('IsPlayable', 'false')
			url = get_url(action='listseasonsorepisodes', url=item_link.get('href'))
			xbmcplugin.addDirectoryItem(_handle_, url, list_item, True)
	nextPage = soup.select_one('link[rel="next"]')
	if nextPage is not None:
		list_item = xbmcgui.ListItem(label="-Next Page-")
		list_item.setProperty('IsPlayable', 'false')
		url = get_url(action='listmovies', url=nextPage.get('href'))
		xbmcplugin.addDirectoryItem(_handle_, url, list_item, True)

	xbmcplugin.endOfDirectory(_handle_)

def quick_play() 
	
	
def play_video(url):
	if _addon_.getSetting('Username') != '' or _addon_.getSetting('Password') != '': 
		login()
	response = _request_.get(url)
	mid = re.search("mid:[\s]?(.*),", response).group(1)
	sequence = re.search("CurrentEpisode:[\s]?'(.*)'", response).group(1)
	response = _request_.get(_domain_ + '/get_movie_play_json?movieid=' + mid + '&sequence=' + sequence)
	data = json.loads(response)
	url = data.get('data').get('playList') + '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
	
	play_item = xbmcgui.ListItem(path=url)
	# Pass the item to the Kodi player.
	xbmcplugin.setResolvedUrl(_handle_, True, listitem=play_item)
	
def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_baseurl_, urlencode(kwargs))
def login():
	if _addon_.getSetting('Username') == '' or _addon_.getSetting('Password') == '': 
		xbmcgui.Dialog().ok(_addon_.getAddonInfo('name'), 'This addon need a username and password from HDViet.')
		_addon_.openSettings()
	else: 
		if _request_.session is None or _request_.session.cookies is None or _request_.session.cookies.get('oauth_sessionhash_v22') is None or _request_.session.cookies.get('oauth_sessionhash_v22') == '':
			
			postdata = {
				'email': _addon_.getSetting('Username') ,
				'password': hashlib.md5(_addon_.getSetting('Password')).hexdigest(),
				'remember': '0'
			}
			response = _request_.post('http://movies.hdviet.com/dang-nhap.html', params=postdata)
			data = json.loads(response)
			if data.get('e') != 0:
				xbmcgui.Dialog().ok(_addon_.getAddonInfo('name'), 'Login failed. Please check your settings')


def search():
	xbmcplugin.setPluginCategory(_handle_, 'Search')
	xbmcplugin.setContent(_handle_, 'movies')
	url = get_url(action='dosearch')
	xbmcplugin.addDirectoryItem(_handle_, url, xbmcgui.ListItem(label="[COLOR orange][B]%s[/B][/COLOR]" % "Enter search text ..."), True)

    # Support to save search history
	contents = XbmcHelper.search_history_get()
	if contents:
		url = get_url(action= 'clearsearchhistory')
		xbmcplugin.addDirectoryItem(_handle_, url, xbmcgui.ListItem(label="[COLOR red][B]%s[/B][/COLOR]" % "Clear search text ..."), False)
		for txt in contents:
			try:
				url = get_url(action='dosearch', keyword=txt)
				xbmcplugin.addDirectoryItem(_handle_, 
				url,
				xbmcgui.ListItem(label="[COLOR blue][B]%s[/B][/COLOR]" % txt),
				True)
			except:
				pass
	xbmcplugin.endOfDirectory(_handle_)

def do_search(keyword):
	xbmcplugin.setPluginCategory(_handle_, 'Search Result')
	xbmcplugin.setContent(_handle_, 'movies')
	if not keyword:
		keyboard = xbmc.Keyboard('', 'Search iPlayer')
		keyboard.doModal()
		if keyboard.isConfirmed():
			keyword = keyboard.getText()

	if not keyword:
		return
	XbmcHelper.search_history_save(keyword)
	list_movies(_domain_ + '/tim-kiem.html?keyword=' + keyword)
			
def router(paramstring):
	
	params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
	
		
	if params:
		if params['action'] == 'listmovies':
			# Display the list of videos in a provided category.
			list_movies(params['url'])
		elif params['action'] == 'listseasonsorepisodes':
			list_seasons_or_episodes(params['url'])
		elif params['action'] == 'listseasonepisodes':
			list_season_episodes(params['movieid'])
		elif params['action'] == 'play':
			# Play a video from a provided URL.
			play_video(params['url'])
		elif params['action'] == 'search':
			search()
		elif params['action'] == 'dosearch':
			do_search(params.get('keyword'))
		elif params['action'] == 'clearsearchhistory':
			XbmcHelper.search_history_clear()
		else:
			# If the provided paramstring does not contain a supported action
			# we raise an exception. This helps to catch coding errors,
			# e.g. typos in action names.
			raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
	else:
		# If the plugin is called from Kodi UI without any parameters,
		# display the list of video categories
		list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, urllib.error
import twurl
import json
import ssl
import folium
from pprint import pprint
from geopy.geocoders import Nominatim

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
def find_json(TWITTER_URL):
    """
    srt -> dict
    Return json from url
    """
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    acct = input('Enter Twitter Account: ')
    url = twurl.augment(TWITTER_URL,
                        {'screen_name': acct, 'count': '5'})
    # print('Retrieving', url)
    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()

    js = json.loads(data)
    return js, acct
# pprint(find_json(TWITTER_URL))


def transform_data(json):
    """
    dict -> lst(tuple)
    Return list of tuples from json with name and location.

    """
    nick_pos = []
    for user in json['users']:
        nick_pos.append((user['screen_name'], user['location']))
    return nick_pos
# print(transform_data(find_json(TWITTER_URL)[0]))


def find_position(friends):
    """
    lst(tuple) -> lst(tuple)
    Find the nearest shot muvie to your location in chosen year
    Distance in km
    """
    friends_pos = []
    for friend in friends:
        try:
            geolocator = Nominatim(user_agent="specify_your_app_name_here")
            location = geolocator.geocode(friend[1])
            loc_friend = (location.latitude, location.longitude)
            friends_pos.append((friend[0], loc_friend, friend[1]))
        except:
            pass
    return friends_pos
print(find_position(transform_data(find_json(TWITTER_URL)[0])))


def generate_map(friends_pos, user):
    """
    lst, str, str -> file
    Return html with map with the nearest places where films was shoted
    """
    map = folium.Map(location=[44, 30], zoom_start=100)
    fg_marker = folium.FeatureGroup(name='friends')
    for friend in friends_pos:
        lt = friend[1][0]
        ln = friend[1][1]
        name = friend[0]
        place = friend[2]
        fg_marker.add_child(folium.Marker(location=[lt, ln], popup=name + "\n\n" + place, icon=folium.Icon()))

    map.add_child(fg_marker)
    map.add_child(folium.LayerControl())
    file = user + '_movies_map.html'
    map.save(file)
    print('Finished. Please have look at the map ' + file)


def main():
    """
    void -> file
    Take json from twitter and return map of nearest friends
    """
    TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
    js = find_json(TWITTER_URL)
    json = js[0]
    user = js[1]
    friends = transform_data(json)
    friends_pos = find_position(friends)

    generate_map(friends_pos, user)
# main()

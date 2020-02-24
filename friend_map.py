#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, urllib.error
import twurl
import json
import ssl
import folium
from pprint import pprint
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
def find_json(TWITTER_URL, acct):
    """
    srt -> dict
    Return json from url
    """
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # acct = input('Enter Twitter Account: ')
    url = twurl.augment(TWITTER_URL,
                        {'screen_name': acct, 'count': '5'})
    # print('Retrieving', url)
    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()

    js = json.loads(data)
    return js
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
# print(find_position(transform_data(find_json(TWITTER_URL)[0])))


def generate_map(friends_pos):
    """
    lst, str, str -> file
    Return html with map with the nearest places where films was shoted
    """
    map = folium.Map(location=[44, 30], zoom_start=10)
    fg_marker = folium.FeatureGroup(name='friends')
    for friend in friends_pos:
        lt = friend[1][0]
        ln = friend[1][1]
        name = friend[0]
        place = friend[2]
        fg_marker.add_child(folium.Marker(location=[lt, ln], popup=name + "\n\n" + place, icon=folium.Icon()))

    map.add_child(fg_marker)
    map.add_child(folium.LayerControl())
    # file = 'Twitter_movies_map.html'
    # map.save('templates/' + file)
    # print('Finished. Please have look at the map ' + file)
    return map._repr_html_()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/map", methods = ['POST', 'GET'])
def map():
    if request.method == "POST":
        info = request.form
        name = info.get('name','')
        TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
        try:
            json = find_json(TWITTER_URL, name)
        except:
            return render_template('error.html', error_message='User not found...')
        friends = transform_data(json)
        friends_pos = find_position(friends)
        # generate_map(friends_pos)
    # return render_template("Twitter_movies_map.html")
    else:
        return render_template('error.html', error_message="You have to give a user name")

    return generate_map(friends_pos)


if __name__ == '__main__':
    app.run(debug=True)

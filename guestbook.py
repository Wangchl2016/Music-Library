#!/usr/bin/env python
from __future__ import unicode_literals
# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
import hashlib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GENRA_NAME = 'jazz'
DEFAULT_ALBUM_NAME = ''
DEFAULT_USER_ID = ''


# We set a parent key on the 'Songs' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(genra_name=DEFAULT_GENRA_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use genra_name as the key.
    """
    return ndb.Key('addSong', genra_name)


def cart_key(user_id=DEFAULT_USER_ID):
    """Sub model for representing an author."""
    return ndb.Key('addSong2Cart', user_id)


def history_key(user_id=DEFAULT_USER_ID):
    """Sub model for representing an author."""
    return ndb.Key('checkout', user_id)

# [START song]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Song(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    uid = ndb.StringProperty(indexed=False)
    author = ndb.StructuredProperty(Author)
    artist_name = ndb.StringProperty(indexed=False)
    title = ndb.StringProperty(indexed=False)
    album_name = ndb.StringProperty(indexed=False)
    price = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END song]





# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        genra_name = self.request.get('genra_name',
                                          DEFAULT_GENRA_NAME)
        songs_query = Song.query(
            ancestor=guestbook_key(genra_name)).order(-Song.date)
        songs = songs_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            user_id = users.get_current_user().user_id()
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            user_id = ''

        template_values = {
            'user': user,
            'songs': songs,
            'genra_name': urllib.quote_plus(genra_name),
            'url': url,
            'user_id': user_id,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class addSong(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Song' to ensure each
        # Song is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        genra_name = self.request.get('genra_name',
                                          DEFAULT_GENRA_NAME)
        song = Song(parent=guestbook_key(genra_name.lower()))

        if users.get_current_user():
            song.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        song.artist_name = self.request.get('artist_name')
        #put artist name to lower case for search
        #song.artist_name = song.artist_name.lower()
        song.title = self.request.get('title')
        song.album_name = self.request.get('album_name', DEFAULT_ALBUM_NAME)
        song.price = self.request.get('price')
        m = hashlib.md5()
        m.update(song.artist_name + song.title + song.album_name)
        song.uid = m.hexdigest()
        song.put()

        query_params = {'genra_name': genra_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]


# [START guestbook]
class addSong2Cart (webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Song' to ensure each
        # Song is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        user_id = self.request.get('user_id',
                                          DEFAULT_USER_ID)
        


        # song.artist_name = self.request.get('artist_name')
        # song.title = self.request.get('title')
        # song.album_name = self.request.get('album_name', DEFAULT_ALBUM_NAME)
        # song.price = self.request.get('price')


        #add current songs in cart to list
        user = users.get_current_user()
        current_cart = []
        if user:
            url = users.create_logout_url(self.request.uri)
            user_id = users.get_current_user().user_id()
        else:
            url = users.create_login_url(self.request.uri)
            user_id = ''


        '''check for songs already bought and in current cart'''
        if user_id != '':
            songs_query = Song.query(
                ancestor= cart_key(user_id)).order(-Song.date)
            songs = songs_query.fetch(50)

        for current_song_uid in songs:
            current_cart.append(current_song_uid.uid)



        if user_id != '':
            songs_query = Song.query(
                ancestor= history_key(user_id)).order(-Song.date)
            songs = songs_query.fetch(50)

        for current_song_uid in songs:
            current_cart.append(current_song_uid.uid)


        #uids = self.request.GET['check_list']
        uids = self.request.get('check_list', allow_multiple=True)
        for uid in uids:
            # for every song, check if it's already in the cart, if not, we 
            # copy all the info and add to cart
            

            if uid not in current_cart:
                songinfo_query = Song.query()
                songinfo = songinfo_query.fetch(50)
                for single_song_info in songinfo:
                    if single_song_info.uid == uid:
                        song = Song(parent=cart_key(user_id))
                        song.artist_name = single_song_info.artist_name
                        song.album_name = single_song_info.album_name
                        song.title = single_song_info.title
                        song.uid = single_song_info.uid
                        song.price = single_song_info.price
                        song.put()
        

        query_params = {'user_id': user_id}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]


class removeSongFromCart (webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Song' to ensure each
        # Song is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        user_id = self.request.get('user_id',
                                          DEFAULT_USER_ID)



        uids = self.request.get_all('check_list')
        for uid in uids:
            # for every song, check if it's already in the cart, if not, we 
            # copy all the info and add to cart
            
            songinfo_query = Song.query(ancestor= cart_key(user_id))
            songinfo = songinfo_query.fetch(50)
            for single_song_info in songinfo:
                if single_song_info.uid == uid:
                    single_song_info.key.delete()
        

        query_params = {'user_id': user_id}
        self.redirect('/?' + urllib.urlencode(query_params))


class checkout (webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Song' to ensure each
        # Song is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        user_id = self.request.get('user_id',
                                          DEFAULT_USER_ID)


        
            
        songinfo_query = Song.query(ancestor= cart_key(user_id))
        songinfo = songinfo_query.fetch(50)
        for single_song_info in songinfo:
            song = Song(parent=history_key(user_id))
            song.artist_name = single_song_info.artist_name
            song.album_name = single_song_info.album_name
            song.title = single_song_info.title
            song.uid = single_song_info.uid
            song.price = single_song_info.price
            single_song_info.key.delete()
            song.put()
        

        query_params = {'user_id': user_id}
        self.redirect('/?' + urllib.urlencode(query_params))

class enter(webapp2.RequestHandler):

    def get(self):
        genra_name = self.request.get('genra_name',
                                          DEFAULT_GENRA_NAME)
        genra_name_lower = genra_name.lower()
        songs_query = Song.query(
            ancestor=guestbook_key(genra_name_lower)).order(-Song.date)
        songs = songs_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'songs': songs,
            'genra_name': urllib.quote_plus(genra_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('enter.html')
        self.response.write(template.render(template_values))

class display(webapp2.RequestHandler):

    def get(self):
        genra_name = self.request.get('genre_name')
        
        songs_query = Song.query(
            ancestor=guestbook_key(genra_name)).order(-Song.date)
        songs = songs_query.fetch(50)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            user_id = users.get_current_user().user_id()
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            user_id = ''

        template_values = {
            'user': user,
            'songs': songs,
            'genra_name': urllib.quote_plus(genra_name),
            'url': url,
            'url_linktext': url_linktext,
            'user_id': user_id,
        }

        template = JINJA_ENVIRONMENT.get_template('display.html')
        self.response.write(template.render(template_values))

class search(webapp2.RequestHandler):

    def get(self):
        genra_name = self.request.get('genra_name',
                                          DEFAULT_GENRA_NAME)
        artist_name = self.request.get('artist_name')

        #error handeling
        artist_name_size = len(artist_name)
        genra_name_l = genra_name.lower()

        songs_query = Song.query(
            ancestor=guestbook_key(genra_name_l)).order(-Song.date)
        songs = songs_query.fetch(50)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'songs': songs,
            'genra_name': urllib.quote_plus(genra_name),
            'artist_name': urllib.quote_plus(artist_name),
            'artist_name_size':artist_name_size,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

class view_cart(webapp2.RequestHandler):

    def get(self):        


        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            user_id = users.get_current_user().user_id()
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            user_id = ''

        if user_id != '':
            songs_query = Song.query(
                ancestor= cart_key(user_id)).order(-Song.date)
            songs = songs_query.fetch(50)




            template_values = {
                'user': user,
                'songs': songs,
                #'genra_name': genra_name,
                'url': url,
                'url_linktext': url_linktext,
                'user_id': user_id,
            }

        else:
            template_values = {
                'user': user,
                #'songs': songs,
                #'genra_name': genra_name,
                'url': url,
                'url_linktext': url_linktext,
                'user_id': user_id,
            }

        template = JINJA_ENVIRONMENT.get_template('view_cart.html')
        self.response.write(template.render(template_values))


class preview_checkout(webapp2.RequestHandler):

    def get(self):        


        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            user_id = users.get_current_user().user_id()
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            user_id = ''

        if user_id != '':
            songs_query = Song.query(
                ancestor= cart_key(user_id)).order(-Song.date)
            songs = songs_query.fetch(50)




            template_values = {
                'user': user,
                'songs': songs,
                #'genra_name': genra_name,
                'url': url,
                'url_linktext': url_linktext,
                'user_id': user_id,
            }

        else:
            template_values = {
                'user': user,
                #'songs': songs,
                #'genra_name': genra_name,
                'url': url,
                'url_linktext': url_linktext,
                'user_id': user_id,
            }

        template = JINJA_ENVIRONMENT.get_template('preview_checkout.html')
        self.response.write(template.render(template_values))




class view_history(webapp2.RequestHandler):

    def get(self):        


        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            user_id = users.get_current_user().user_id()
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            user_id = ''

        if user_id != '':
            songs_query = Song.query(
                ancestor= history_key(user_id)).order(-Song.date)
            songs = songs_query.fetch(50)




            template_values = {
                'user': user,
                'songs': songs,
                #'genra_name': genra_name,
                'url': url,
                'url_linktext': url_linktext,
                'user_id': user_id,
            }

        else:
            template_values = {
                'user': user,
                #'songs': songs,
                #'genra_name': genra_name,
                'url': url,
                'url_linktext': url_linktext,
                'user_id': user_id,
            }

        template = JINJA_ENVIRONMENT.get_template('view_history.html')
        self.response.write(template.render(template_values))



# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', addSong),
    ('/enter', enter),
    ('/display', display),
    ('/search', search),
    ('/addSong2Cart', addSong2Cart),
    ('/view_cart', view_cart),
    ('/removeSongFromCart', removeSongFromCart),
    ('/checkout', checkout),
    ('/preview_checkout', preview_checkout),
    ('/view_history', view_history)
    ], debug=True)
# [END app]

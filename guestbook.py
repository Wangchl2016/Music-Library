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

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GENRA_NAME = 'Jazz'
DEFAULT_ALBUM_NAME = ''


# We set a parent key on the 'Songs' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(genra_name=DEFAULT_GENRA_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use genra_name as the key.
    """
    return ndb.Key('Guestbook', genra_name)


# [START song]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Song(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    artist_name = ndb.StringProperty(indexed=False)
    title = ndb.StringProperty(indexed=False)
    album_name = ndb.StringProperty(indexed=False)
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

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Song' to ensure each
        # Song is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        genra_name = self.request.get('genra_name',
                                          DEFAULT_GENRA_NAME)
        song = Song(parent=guestbook_key(genra_name))

        if users.get_current_user():
            song.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        song.artist_name = self.request.get('artist_name')
        #put artist name to lower case for search
        #song.artist_name = song.artist_name.lower()
        song.title = self.request.get('title')
        song.album_name = self.request.get('album_name', DEFAULT_ALBUM_NAME)
        song.put()

        query_params = {'genra_name': genra_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]

class enter(webapp2.RequestHandler):

    def get(self):
        genra_name = self.request.get('genra_name',
                                          DEFAULT_GENRA_NAME)
        songs_query = Song.query(
            ancestor=guestbook_key(genra_name)).order(-Song.date)
        songs = songs_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Logout'

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
        genra_name = self.request.get('genre_name',
                                          DEFAULT_GENRA_NAME)
        songs_query = Song.query(
            ancestor=guestbook_key(genra_name)).order(-Song.date)
        songs = songs_query.fetch(50)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Logout'

        template_values = {
            'user': user,
            'songs': songs,
            'genra_name': urllib.quote_plus(genra_name),
            'url': url,
            'url_linktext': url_linktext,
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

        songs_query = Song.query(
            ancestor=guestbook_key(genra_name)).order(-Song.date)
        songs = songs_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Logout'

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



# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/enter', enter),
    ('/display', display),
    ('/search', search),
    ], debug=True)
# [END app]

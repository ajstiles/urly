# Copyright 2008 Adam Stiles
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy 
# of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required 
# by applicable law or agreed to in writing, software distributed under the 
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS 
# OF ANY KIND, either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

from google.appengine.ext import db
from google.appengine.api import memcache
import logging

class Urly(db.Model):
    """Our one-and-only model"""  
    href = db.LinkProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    KEY_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = 62

    def code(self):
        """Return our code, our base-62 encoded id"""
        if not self.is_saved():
            return None
        nid = self.key().id()
        s = []
        while nid:
            nid, c = divmod(nid, Urly.BASE)
            s.append(Urly.KEY_BASE[c])
        s.reverse()
        return "".join(s)
        
    def to_json(self):
        """JSON is so simple that we won't worry about a template at this point"""
        return "{\"code\":\"%s\",\"href\":%s\"}\n" % (self.code(), self.href);
    
    def to_xml(self):
        """Like JSON, XML is simple enough that we won't template now"""
        msg = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        msg += "<urly code=\"%s\" href=\"%s\" />\n" % (self.code(), self.href)
        return msg

    def save_in_cache(self):
        """We don't really care if this fails"""
        memcache.set(self.code(), self)

    @staticmethod
    def find_or_create_by_href(href):
        query = db.Query(Urly)
        query.filter('href =', href)
        u = query.get()
        if not u:
            u = Urly(href=href)
            u.put()
            u.save_in_cache()
        return u

    @staticmethod
    def code_to_id(code):
        aid = 0L
        for c in code:
            aid *= Urly.BASE 
            aid += Urly.KEY_BASE.index(c)
        return aid
    
    @staticmethod
    def find_by_code(code):
        try:
            u = memcache.get(code)
        except:
            # http://code.google.com/p/googleappengine/issues/detail?id=417
            logging.error("Urly.find_by_code() memcached error")
            u = None
        
        if u is not None:
            logging.info("Urly.find_by_code() cache HIT: %s", str(code))
            return u        

        logging.info("Urly.find_by_code() cache MISS: %s", str(code))
        aid = Urly.code_to_id(code)
        try:
            u = Urly.get_by_id(int(aid))
            if u is not None:
                u.save_in_cache()
            return u
        except db.BadValueError:
            return None
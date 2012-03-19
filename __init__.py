#!/usr/bin/python
# -*- coding: utf-8 -*-
# by Alex 'apexad' Martin
# help from: muhkuh0815 & gaVRos

import re
import urllib2, urllib
import json
import random
import math

from plugin import *

from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.systemObjects import GetRequestOrigin,Location
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.localsearchObjects import Business, MapItem, MapItemSnippet, Rating

googleplaces_api_key = APIKeyForAPI("google")

Title = None
 
class googlePlacesSearch(Plugin):
     @register("en-US", "(find|show|where).* (find|nearest|nearby|closest) (.*)")
     @register("en-GB", "(find|show|where).* (nearest|nearby|closest) (.*)")
     @register("fr-FR", "(trouves|trouve|cherche|où).* (près|proche) (.*)")
     def googleplaces_search(self, speech, language, regex):
          #added
          global Title
          #end addition
          if language == "fr-FR":
             self.say('Je recherche...',' ')
          else:
              self.say('Searching...',' ')
          
          mapGetLocation = self.getCurrentLocation()
          latitude= mapGetLocation.latitude
          longitude= mapGetLocation.longitude
          #modified
          if Title == None:
               Title = regex.group(regex.lastindex).strip()
               Query = urllib.quote_plus(str(Title.encode("utf-8")))
          else:
               Query = urllib.quote_plus(Title)
          #end modify
          random_results = random.randint(2,15)
          googleurl = "https://maps.googleapis.com/maps/api/place/search/json?location={0},{1}&radius=5000&name={2}&sensor=true&key={3}".format(latitude,longitude,str(Query),str(googleplaces_api_key))
          try:
               jsonString = urllib2.urlopen(googleurl, timeout=20).read()
          except:
               jsonString = None
          if jsonString != None:
               response = json.loads(jsonString)
               if (response['status'] == 'OK') and (len(response['results'])):
                    googleplaces_results = []
                    for result in response['results']:
                         if "rating" in result:
                              avg_rating = result["rating"]
                         else:
                              avg_rating = 0.0
                         rating = Rating(value=avg_rating, providerId='Google Places', count=0)
                         details = Business(totalNumberOfReviews=0,name=result['name'],rating=rating)
                         if (len(googleplaces_results) < random_results):
                              mapitem = MapItem(label=result['name'], street=result['vicinity'], latitude=result['geometry']['location']['lat'], longitude=result['geometry']['location']['lng'])
                              mapitem.detail = details
                              googleplaces_results.append(mapitem)
                         else:
                              break
                    mapsnippet = MapItemSnippet(items=googleplaces_results)
                    count_min = min(len(response['results']),random_results)
                    count_max = max(len(response['results']),random_results)
                    view = AddViews(self.refId, dialogPhase="Completion")
                    view.views = [AssistantUtteranceView(speakableText='I found '+str(count_max)+' '+str(Title)+' results... '+str(count_min)+' of them are fairly close to you:', dialogIdentifier="googlePlacesMap"), mapsnippet]
                    self.sendRequestWithoutAnswer(view)
               else:
                    if language == "fr-FR":
                       self.say("Je suis désolé, je n'ai pas trouvé de résultats pour "+str(Title)+" près de vous!")
                    else:
                        self.say("I'm sorry but I did not find any results for "+str(Title)+" near you!")
          else:
               if language == "fr-FR":
                       self.say("Je suis désolé, je n'ai pas trouvé de résultats pour "+str(Title)+" près de vous!")
               else:
                        self.say("I'm sorry but I did not find any results for "+str(Title)+" near you!")
          self.complete_request()
          
          
#all after is modified
#to create custom commands, copy and paste this code block
#and then change parameters like the key words, def name, and Search string
     @register('en-US', "I'm.*hungry.*")
     def search_im_hungry(self, speech, language):
          global Title
          
          #this is the string to search for
          Title = "mcdonald's"
          self.googleplaces_search(speech, language, Title)     
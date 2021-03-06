#! python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  30 21:57:00 2018
@author: Saif Kurdi-Teylouni
"""
from storer.storer import storeUser, retrieveUser, retrieveUsersByTeam, storeLaw, deleteLaw, retrieveLaw, updateLaw, storeAccount, retrieveAllAccounts
from scrapers.scraper_api import Law
from collections import namedtuple
import jsonpickle, re, json
import base64

class User( object):

    """username = ''
    identifier = ''
    password=''
    team=''
    lawnames=["Perospero", "Katakuri", "Oven", "Smoothie", "Daifuku", "Compote", "Cracker", "Snack"]"""

    def __init__(self, username, identifier, password, lawnames=[], team=None):
        self.username=username
        self.identifier=identifier
        self.team=team
        self.password=password
        self.lawnames=lawnames

    def addLaw(self, law):
        #sanitizedlaw=law.lower().split("(")[0].strip()
        sanitizedlaw=law.lower().strip()
        dummyvar=1#print(sanitizedlaw)
        self.lawnames.append(sanitizedlaw)

    def LawNamefromOfficaltoBill(self, law):
        billlawname=law.split(",")[0].strip()+" ("+law.split("(")[1].split(")")[0].lower()+")"
        #print(billlawname)
        dummyvar=1#print(billlawname)
        return billlawname

class Team( object ):

    """teamname="NONE"
    users=[]"""

    def __init__(self, users=[], teamname=None):
        self.users=users
        self.teamname=teamname

    def load_users(self):
        self.users=retrieveUsersByTeam(self.teamname)
        for user in self.users:
            for law in user.lawnames:
                dummyvar=1#print("this is it: "+law)

    def load_users_from_accounts(self):
        accounts=retrieveAllAccounts()
        for account in accounts:
            lawnameslist=account['lawnames'].strip("[]").split(",")
            lawnameslistcleansed=[]
            for i in range(len(lawnameslist)):
                try:
                    lawnameslist[i]=str(base64.b64decode(lawnameslist[i]), "utf-8")
                except:
                    lawnameslist[i]=""    
                if " - " in lawnameslist[i]:
                    lawnameslistcleansed.append(lawnameslist[i])
            for i in range(len(lawnameslistcleansed)):
                lawnameslistcleansed[i]=lawnameslistcleansed[i].strip("\"")
                lawnameslistcleansed[i]=lawnameslistcleansed[i].strip("\'").split("(")[0]
                lawnameslistcleansed[i]=lawnameslistcleansed[i].split(" - ")[1].lower()+", ("+lawnameslistcleansed[i].split(" - ")[0].replace("'", "").strip().lower()+")"
 
            user=User(account['username'], account['username'], account['password'], lawnameslistcleansed)
            self.users.append(user)

    def store_users(self):
        for user in self.users:
            storeUser(user)
            #need to update law table also
            for lawname in user.lawnames:
                law=Law(lawname, lawname)
                cachedLaw=retrieveLaw(lawname)
                if cachedLaw==None:
                    storeLaw(law)

    def store_accounts(self):
        for user in self.users:
            #need to update account table
            storeAccount(user)

    def addUser(self, user):
        self.users.append(user)

    def getUsers(self):
        return self.users

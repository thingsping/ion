'''
/*
 * Source code : all rights reserved
 * Copyright (c) 2019 onwards, 
 * Authors: Qantom Software Private Limited
 *
 * This program is free software (...)
 * You should have received a copy of the GNU Affero General Public License
 * along with this program (...)
 *
 * You must make all your source code available in case you release code
 * or any code that uses this code. You can be opt for a commercial license from  
 * Qantom software private limited, if you do not want to share your code and 
 * want a commercial license. Buying such a license is mandatory as soon as you
 * develop commercial activities involving the ionserver software without
 * disclosing the source code of your own applications (...)
 *
 */
 '''

__author__ = "raghu"
__date__ = "$June 24, 2019 "

from .constants import * 
from .userconfig import config 
import pymongo

class DBManager():

    __dbclient = None
    __dbglobalclient = None

    '''
    Effect of singleton
    '''
    @staticmethod 
    def getDB() :
        if (DBManager.__dbclient is None):
            print("Establishing DB Connection...")
            dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
            DBManager.__dbclient = dbclient[config[CKEY_DBNAME]]
        return DBManager.__dbclient

    @staticmethod 
    def getGlobalDB() :
        if (DBManager.__dbglobalclient is None):
            dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
            DBManager.__dbglobalclient = dbclient[GLOBAL_DB_NAME]
        return DBManager.__dbglobalclient
    
    @staticmethod 
    def getCollection(colname) :
        cl = DBManager.getDB() 
        return cl[colname] 
    
    @staticmethod
    def getGlobalCollection(colnname) :
        cl = DBManager.getGlobalDB() 
        return cl[colnname] 
        

    # The idea behind having wrapper methods for the pymongo api is that
    # when we are done implementing the core features, we can change this
    # implementation to use threads for writing to DB. That way the response 
    # to the caller won't have to wait till the DB write operation completes
    @staticmethod 
    def replace_one(colname, data, filter, upsert=True):
        coln = DBManager.getCollection(colname)
        coln.replace_one(filter, data, upsert=upsert)    

    @staticmethod 
    def find_one(colnname, filter):
        return DBManager.getCollection(colnname).find_one(filter)

    @staticmethod 
    def find(colnname, filter=None):
        return DBManager.getCollection(colnname).find(filter)

    @staticmethod
    def insert_one(colnname, data):
        return DBManager.getCollection(colnname).insert_one(data)
    

    @staticmethod
    def insert_many(colnname, data):
        return DBManager.getCollection(colnname).insert_many(data)

    @staticmethod
    def delete_many(colnname, filter):
        coln = DBManager.getCollection(colnname)
        res = coln.delete_many(filter)

    @staticmethod
    def drop(colnname):
        coln = DBManager.getCollection(colnname)
        return coln.drop()

    @staticmethod
    def find_first(colnname, filter):
        #print ("Filter = {}".format(filter))
        coln = DBManager.getCollection(colnname)
        res = coln.find(filter).sort(HDR_TIME, pymongo.DESCENDING)
        if (res is not None):
            return res[0]
        else:
            return None 
        
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
__date__ = "$July 5, 2019 "

from .constants import * 
from .userconfig import config
import copy, json, time, glob, pymongo

inblock_tpl = '''createInputBlock("%BLKNAME%", "%DEVID%", "%ENTITYNAME%", 
    "%LOCATION%", [%PARAMARRAY%], "%PARAMTYPE%"); '''
inblockval_tpl = '''createInputValueBlock("%BLKNAME%", "%DEVID%", "%ENTITYNAME%", 
    "%LOCATION%", [%PARAMARRAY%], "%PARAMTYPE%"); '''
outblock_tpl = '''createOutputBlock("%BLKNAME%", "%DEVID%", "%ENTITYNAME%", 
    "%LOCATION%", "%ACTION%", [%PARAMARRAY%], %PARAMTYPE%); '''

category_start_tpl = '<category name="%LOCATION%">'
blktype_tpl = '<block type="%BLOCKNAME%"></block>'
category_end_tpl = "</category>"

def fromJsonFile(jf) :
    dct = {}
    functs = []

    with open(jf) as json_file:  
        data = json.load(json_file)
        #print(data)
        parsedBlockly = blocklyFromJson(data)
    return (parsedBlockly[0], parsedBlockly[1]) 

def fromPattern(jd, target) :
    reqd_files = glob.glob(jd)
    dctAll = {}
    funcAll = []
    for f in reqd_files :
        proc = fromJsonFile(f)
        mergeDictionaries(dctAll, proc[0])
        funcAll.extend(proc[1])
    create_files(dctAll, funcAll, target)

def fromDB(target) :
    print("Establishing DB Connection from blockly...")
    dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
    db = dbclient[config[CKEY_DBNAME]]
    coln = db[DB_ADS_COLN]
    data = coln.find() 
    dctAll = {}
    funcAll = []
    for row in data:
        parsedBlockly = blocklyFromJson(row, True)
        mergeDictionaries(dctAll, parsedBlockly[0])
        funcAll.extend(parsedBlockly[1])
    #print(funcAll)
    #print("---------------")
    #print(dctAll)
    create_files(dctAll, funcAll, target)

def blocklyFromJson(jsdata, isFromDb=False):
    if (isFromDb):
        devid = jsdata[DBHDR_DEVID]
    else :
        devid = jsdata[HDR_DEVID] 
    allData = jsdata[HDR_DATA]
    dictBlocks = {}
    allFunctions = [] 
    reqblock2 = None
    for data in allData :
        nodeType = data[HDR_NODETYPE]
        entityName = data[HDR_NAME]
        entityLoc = data[HDR_LOCATION]
        blkName =  "{}_{}".format(entityName,entityLoc) 
        if nodeType == NODETYPE_SENSOR :
            dataJson = data[HDR_RETURN]
            reqblock = inblock_tpl 
            reqblock2 = inblockval_tpl 
        else :
            dataJson = data[HDR_PARAMS]
            reqblock = outblock_tpl 
            action = data[HDR_ACTION]
            reqblock = reqblock.replace("%ACTION%", action )
        
        reqblock = reqblock.replace("%DEVID%", devid)
        reqblock = reqblock.replace("%ENTITYNAME%", entityName)
        reqblock = reqblock.replace("%LOCATION%", entityLoc )
        if reqblock2 is not None:
            reqblock2 = reqblock2.replace("%DEVID%", devid)
            reqblock2 = reqblock2.replace("%ENTITYNAME%", entityName)
            reqblock2 = reqblock2.replace("%LOCATION%", entityLoc )
        
        genfunction2 = None
        if nodeType == NODETYPE_OUTPUT :
            paramNamesStr = ""
            paramTypesStr  = "["
                #Remember that the template for types does not have the array component 
                #included in it. 
            for name in dataJson.keys():
                if paramNamesStr != "" :
                    paramNamesStr += ", "
                paramNamesStr += '"' + name  + '"'
                if paramTypesStr != "[" :
                    paramTypesStr += ", "
                paramType = dataJson[name]
                if paramType == "Str" :
                    paramType = "String"
                if paramType == "Float" or paramType == "Int" or paramType == "Integer" :
                    paramType = "Number"
                paramTypesStr += '"' + paramType + '"'
            paramTypesStr += "]"  
            genfunction = reqblock.replace("%BLKNAME%", blkName) 
            genfunction = genfunction.replace("%PARAMARRAY%", paramNamesStr)
            genfunction = genfunction.replace("%PARAMTYPE%", paramTypesStr); 
            if entityLoc in dictBlocks :
                arrBlocksForLocation = dictBlocks[entityLoc]
                arrBlocksForLocation.append("BLK_OUT_" + blkName)
                dictBlocks[entityLoc] = arrBlocksForLocation
            else:
                dictBlocks[entityLoc] = ["BLK_OUT_" + blkName]
            allFunctions.append(genfunction)
        else : #If sensor
            '''
            BEGIN RETURN VALUES (NEED THIS COMMENT FOR INDENTING) 
            '''
            retValuesJson = {}
            for key, value in dataJson.items() :
                if value == "Str" :
                    value = "String"
                if value == "Float" or value == "Int" or value == "Integer" :
                    value = "Number"

                if value in retValuesJson :
                    retValuesJson[value].append(key)
                else :
                    retValuesJson[value] = [key]

            allBlocks = []
            for key, valuearr in retValuesJson.items() :
                strValArr = "" 
                for value in valuearr:
                    if (strValArr != "") :
                        strValArr += "," 
                    strValArr += '"' + value + '"'
                    genfunction = reqblock.replace("%PARAMARRAY%", strValArr) 
                    genfunction = genfunction.replace("%PARAMTYPE%", key )

                    genfunction2 = reqblock2.replace("%PARAMARRAY%", strValArr) 
                    genfunction2 = genfunction2.replace("%PARAMTYPE%", key )
                newBlkName = "{}_{}".format(blkName, key)  
                genfunction = genfunction.replace("%BLKNAME%", newBlkName) 
                genfunction2 = genfunction2.replace("%BLKNAME%", newBlkName) 

                allBlocks.append("BLK_IN_" + newBlkName)
                allBlocks.append("BLK_IN_VALUE_" + newBlkName)
                allFunctions.append(genfunction)
                if genfunction2 is not None:
                    allFunctions.append(genfunction2)

            if entityLoc in dictBlocks :
                arrBlocksForLocation = dictBlocks[entityLoc]
                arrBlocksForLocation.extend(allBlocks)
                dictBlocks[entityLoc] = arrBlocksForLocation
            else:
                dictBlocks[entityLoc] = allBlocks
            #dictBlocks[entityLoc] = allBlocks
            '''
            END RETURN VALUES (NEED THIS COMMENT FOR INDENTING) 
            '''
    return (dictBlocks, allFunctions) 

def mergeDictionaries(mainDict, addDict) :
    for key, addArray in addDict.items():
        if key in mainDict:
            #Let's just assument this method will only be called by
            #us - that is value will always be an Array
            mainArr = mainDict [key]
            for item in addArray:
                mainArr.append(item)
        else:
            mainDict[key] = addArray

def create_files(dictLocations, allFunctions, targetbase):
    jsfile = targetbase + "/generated.js"
    indextemplate = targetbase + "/index.html.template"
    indexfile = targetbase + "/index.html"
    strAll = ""
    for line in allFunctions:
        strAll += line + "\n"
    
    print ("JS = {}, IDX = {} ".format(jsfile, indexfile))

    with open(jsfile, 'w') as f:
        f.write(strAll)
        f.close()
    
    allCategories = ""
    for location, blocks in dictLocations.items() :
        #print("Loc={}, Blocks={}".format(location, blocks))
        catLoc =  category_start_tpl.replace("%LOCATION%", location) + "\n"
        for block in blocks : 
            catLoc += blktype_tpl.replace("%BLOCKNAME%", block) +"\n"
        catLoc += category_end_tpl
        allCategories += catLoc + "\n"
    
    indexfilecontent = ""
    with open (indextemplate, 'r') as ft :
        indexfilecontent = ft.read(); 
        ft.close() 
    indexfilecontent = indexfilecontent.replace("%CATEGORYWISEBLOCKS%", allCategories)
    with open(indexfile, 'w') as fi:
        fi.write(indexfilecontent)
        fi.close()

    #print(indexfilecontent)

    #print (allCategories)

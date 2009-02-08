#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Imports
import os
import re
import string
import sys

# Config
"""
# Where to put stuff:
0 = Movies
1 = Series
"""

# Variables

currentDir = os.getcwd()

mediaFolders = ['/home/joel/Videos/mediafolder/movies', '/home/joel/Videos/mediafolder/series']

reCfgMovie = re.compile("movieFolder = \"(.*)\"")
reCfgSeries = re.compile("seriesFolder = \"(.*)\"")
for line in open("/home/joel/.rarfinder/config.cfg", "r").readlines():
    mmatch = re.match(reCfgMovie, line)
    if(mmatch):
        mediaFolders.insert(0, mmatch.group(1))
        
    smatch = re.match(reCfgSeries, line)
    if(smatch):
        mediaFolders.insert(1, smatch.group(1))
    

"""
Random\ Good\ Moviepack
Dexter.s02e05.Xvid.Nisse
Dexter.S02.HDTV.Xvid.Adolf
Prison.Break.S07.HDTV.Xvid.Fisken
"""

############# Arguments #############

args = sys.argv
childFolder = ""
dirs = []
cdirs = []
flags = []

# List of flags and what in the dict they should be TRUE to.
flagList= [['pack', ['p', 'pack']], ['help', ['h', 'help']], ['keep', ['k', 'keep']], ['verbose', ['v', 'verbose']]]

if(len(args) > 1):
    i = 0
    for arg in args:
        flag = False
        if(i > 0):
            for f in flagList:
                for ff in f[1]:
                    for pre in ['-', '--']:
                        if(arg == pre+ff):
                            # One flag is true to this entry of flagList
                            flags.append(ff)
                            flag = True
                
            if(flag == False):
                # adds the foldername to the variable childFolder
                childFolder = "/"+args[i]
                # Appends the childfolder to the dirs-list
                dirs.append(currentDir+childFolder)
                cdirs.append(args[i])
        i += 1
else:
    dirs.append(currentDir)

#####################################


############## Bunch of regular expressions ###############

reCDs = re.compile("CD(\d)", re.IGNORECASE)
reCDFolder = re.compile(".*/(.+)\/CD(\d)", re.IGNORECASE)

#reEpisode = re.compile(".*/(\w+)\.S(\d{2})E(\d{2})\..*", re.IGNORECASE)
reEpisode = re.compile(".*/(.*)\.s(\d{2})e(\d{2})\..*", re.IGNORECASE)
reSeries = re.compile(".*/(.*)\.s([\d]{2})\..*", re.IGNORECASE)

reRipTypes = []

for ripType in ["DVDrip", "DVDscreener", "XviD", "DVDRip", "HDTV"]:
    reRipTypes.append(re.compile("(.+)\."+ripType+".*"))

reRarFiles = []

for rarExp in [".*part[0-9]{1,2}([0-9])\.rar",".*\.rar", ".*\.r[0-9]{1,2}&"]:
    reRarFiles.append(re.compile(rarExp))

## Unused?    
#reNameEpisode = re.compile("(\w+)\.s(\d{2})e(\d{2})\..*", re.IGNORECASE)
#reName = re.compile(".*/(.+)")


############## // Bunch of regular expressions ############

def flag(what):
    ret = False
    if(flags.__contains__(what)):
        ret = True
    
    return ret

def getChars(amount, char = "#"):
    ret = ""
    while(len(ret) <= amount and len(ret) < 150):
        ret += char
    return ret

def vPrint(msg, before = "", after = ""):
    if(flag('verbose')):
        if(before != ""):
            before =  "\n"+getChars(len(msg), before)
            
        if(after != ""):
            after = getChars(len(msg), after)
        
        print before
        print msg
        print after
        
        

def doesDirExist(dir):
    if os.path.isdir(dir):
        ret = True
    else:
        ret = False
    
    return ret

def makeDirs(pathList):
    vPrint("Checking and Making directories, we have to have a clear path now dont we")
    path = ""
    for dir in pathList:
        # Adds the path together, and adds a "/" if it is nessecery
        if(path != ""):
            path += "/"
        #dir = dir.replace(" ", "\ ")
        path += dir
        
        if(doesDirExist(path)):
            vPrint("'%s' did exist, so I did nothing." % path)
        else:
            vPrint("'%s' did not exist, so I created it." % path)
            # Creates the directory if everything is cool
            os.mkdir(path)
    
    return path

"""
gets the Mediafolder for the type
"""
def getMediaFolder(type):
    
    mediaFolder = mediaFolders[type]
    return mediaFolder

def niceName(ugly):
    nice = ""
    
    for exp in reRipTypes:
        match = re.match(exp, ugly)
        if(match):
            nice = match.group(1)
            break
    
    if(nice == ""):
        nice = ugly
        vPrint("Could not make '%s' any nicer (exept maby for some . = '')" % ugly)
    
    nice = nice.replace(".", " ")
    
    return nice
    
"""
Function that takes a string as argument and spitts back an array of what kind of directory you are dealing with.

Takes:      string
Returns:    list of lists
Contains:   type(s)
Example:    [[5, match], [3, match] ... ]

this is what it could return (maby not all of them):
0 = HUH??
2 = Filmmapp
4 = Filmpaketsmapp
5 = Seriemapp       < 1
6 = Avsnittsmapp    < 2

"""

def getDirType(dir):
    type = []
    vPrint( "Analyzing '"+dir+"'")
    # Matches agains the regexp for checking if matches with a complete Series
    match = re.match(reSeries, dir)
    if(match):
        type.append([5, match])
    
    match = re.match(reEpisode, dir)
    if(match):
        type.append([6, match])
    
    if(flag('pack')):
        # Is a moviepack.
        type = [[4], None]
    
    # If not episode or series, check if there are several folders NOT matching reCDs
    if(len(type) == 0):
        c = 0
        
        # Tries to listdir.
        for d in os.listdir(dir):
            
            thisNotAFile = True
            
            try:
                os.listdir(d)
                thisNotAFile = True
            except:
                thisNotAFile = False
            
            if(thisNotAFile):
                match = re.match(reCDs, d)
                if(match):
                    vPrint("%s - Is a CD folder" %d)
                else:
                    vPrint("%s - Is a regular folder, not a CDfolder" %d)
                    c += 1
            
        if(c >= 2):
            type = [[4, None]]
        else:
            type = [[2, None]]

    
    # If NO types were matched, say so.
    if(len(type) == 0):
        type.append([0, None])
    
    return type

def getDestinationPath(type, match):
    path = []
    
    #for g in match.group():
    # print g
    # IS a series
    if(type == 5 or type == 6):
        path.append(mediaFolders[1])
        
        #print match.group(0)
        seriesName = match.group(1)
        # Replace '.' with '\ ' (for bash purposes)
        seriesName = seriesName.replace(".", " ")
        
        path.append(seriesName)
        
        season = match.group(2)
        
        path.append("Season "+season)
    
    # MoviePack
    if(type == 4):
        path.append(mediaFolders[0])
        for m in match:
            path.append(m.replace(".", " "))
            
    # Movie
    if(type == 2):
        path.append(mediaFolders[0])
        for m in match:
            path.append(m.replace(".", " "))
        
    
    return path

"""
Finds the .rar files and returns the path to them.
"""
def findRars(path):
    ret = []
    
    for dir in os.walk(path, True):
        if(dir[2]):
            foundRar = False
            for file in dir[2]:
                # Gonna check for rarfiles
                
                i = 0
                
                for reg in reRarFiles:
                    match = re.match(reg,file)
                    if(match):
                        if(i == 0):
                            
                            # If the number of the file is 1 then it is appended
                            if(match.group(1) == "1"):
                                ret.append(dir[0]+"/"+match.group(0))
                            
                            foundRar = True
                        else:
                            if(foundRar == False):
                                ret.append(dir[0]+"/"+match.group(0))
                        # Appends the path to the rarfile
                        
                        foundRar = True
                        
                        #vPrint("Found rar file: "+dir[0]+"/"+match.group(0)+" TYPE: %s "%i)
                        
                    i += 1
    
    return ret


def getCommand(rarPaths, dir):
    cmd = ""  
 # cmd = "screen -S unrarAndDelete -d -m "
    
    # builds up the unrar part
    for rar in rarPaths:
        rar[1] = rar[1].replace(" ", "\ ")
        rar[0] = rar[0].replace(" ", "\ ")
        cmd += "unrar x -y -kb "+rar[0]+" "+rar[1]
        cmd += ";"
    
    #adds the remove dir part
    if(dir != "." and dir != "/" and flag('keep') == False):
        cmd += "sleep 5s;"
        cmd += "rm -r "+dir.replace(" ", "\ ")+"/"
        cmd += ";"
    
    #cmd += "exit;"
    #cmd += "watch beep"
    return cmd


if(flag('help')):
    h = ""
    
    for line in open('/home/joel/.rarfinder/help.txt', 'r').readlines():
        h += line
        
    print h
    
    dirs = []

"""
Starts the magic, what kind of folder is at the root?
"""

dc = 0
for dir in dirs:
    
    #dir = dir.replace(" ", "\ ")
    
    vPrint("Working on directory: "+dir+"", "# ")
    
    type = getDirType(dir)
    
    rarPaths = [];
    paths = "";
    cmd = "";
    
    # If I have no idea what you are doin...
    if(type[0][0] == 0):
        vPrint("I have no idea what this is... sorry, you have to say so manualy")
    else:
        if(type[0][0] == 5):
            
            vPrint("This is a series folder with a complete season")
            
            paths = getDestinationPath(type[0][0], type[0][1])
            
            path = makeDirs(paths)
            
            for rp in findRars(dir):
                rarPaths.append([rp, path])
            
        if(type[0][0] == 6):
            vPrint("This is an episode of a series")
            
            paths = getDestinationPath(type[0][0], type[0][1])
            
            path = makeDirs(paths)
            
            for rp in findRars(dir):
                rarPaths.append([rp, path])
        
        if(type[0][0] == 4):
            vPrint("This is a moviePack")
            for d in os.listdir(dir):
                vPrint("Working on a movie named: %s"%d, " MOVIE ")
                # Making directories....
                
                if(flag("pack")):
                    paths = getDestinationPath(type[0][0], [niceName(d)])
                else:
                    paths = getDestinationPath(type[0][0], [cdirs[dc], niceName(d)])
                
                path = makeDirs(paths)
                
                for rp in findRars(dir+"/"+d):
                    rarPaths.append([rp, path])
        
        if(type[0][0] == 2):
            
            paths = getDestinationPath(type[0][0], [niceName(cdirs[dc])])
            
            path = makeDirs(paths)
            
            for rp in findRars(dir):
                rarPaths.append([rp, path])
            
        # Makes the path
        # path is the complete path to where the all the stuff is suposed to be
        
        # Loops thru the paths to the rarfiles and builds upp the command to unrar them to the specified path.
        
        cmd = getCommand(rarPaths, dir)
        
        # # # # # # # # # # # # # EXECUTES THE COMMAND # # # # # # # # # # #
        os.popen(cmd)
        
        vPrint(cmd)
        
        #unrar x -y -kb /home/joel/Projects/rarfinder/testfolder/Dexter.S02.HDTV.Xvid.Adolf/Dexter.s02e05.Xvid.Nisse/dexter.rar /home/joel/Projects/rarfinder/testfolder/mediafolder/series/Dexter/Season\ 02
        #unrar x -y -kb /home/joel/Projects/rarfinder/testfolder/Dexter.S02.HDTV.Xvid.Adolf/Dexter.s02e05.Xvid.Nisse/dexter.rar /home/joel/Projects/rarfinder/testfolder/mediafolder/series/Dexter/Season\ 02;unrar x -y -kb /home/joel/Projects/rarfinder/testfolder/Dexter.S02.HDTV.Xvid.Adolf/Dexter.s02e01.Xvid.Nisse/dexter.rar /home/joel/Projects/rarfinder/testfolder/mediafolder/series/Dexter/Season\ 02;unrar x -y -kb /home/joel/Projects/rarfinder/testfolder/Dexter.S02.HDTV.Xvid.Adolf/Dexter.s02e04.Xvid.Nisse/dexter.rar /home/joel/Projects/rarfinder/testfolder/mediafolder/series/Dexter/Season\ 02;unrar x -y -kb /home/joel/Projects/rarfinder/testfolder/Dexter.S02.HDTV.Xvid.Adolf/Dexter.s02e02.Xvid.Nisse/dexter.rar /home/joel/Projects/rarfinder/testfolder/mediafolder/series/Dexter/Season\ 02;unrar x -y -kb /home/joel/Projects/rarfinder/testfolder/Dexter.S02.HDTV.Xvid.Adolf/Dexter.s02e03.Xvid.Nisse/dexter.rar /home/joel/Projects/rarfinder/testfolder/mediafolder/series/Dexter/Season\ 02;watch beep
        
        vPrint("Complete path: %s" % path)
    
    dc += 1

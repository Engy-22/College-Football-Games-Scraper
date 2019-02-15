# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 14:04:39 2019

@author: NATE
"""


from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
from collections import OrderedDict
from itertools import zip_longest

def tonumber(s): #turns s to number if possible, else returns s
    try:
        return(int(s))  
    except:
        return(s)
        
def isstring(s): #in a world of only strings and numbers: is it a string?
    try:
       int(s)
       return False
    except:
       return True


# URLs to Open
urldict = { \
'url2010': "https://www.masseyratings.com/scores.php?s=98700&sub=11604&all=1&mode=3&format=0", \
'url2011': "https://www.masseyratings.com/scores.php?s=107811&sub=11604&all=1&mode=3&format=0", \
'url2012': "https://www.masseyratings.com/scores.php?s=181623&sub=11604&all=1&mode=3&format=0", \
'url2013': "https://www.masseyratings.com/scores.php?s=199231&sub=11604&all=1&mode=3&format=0", \
'url2014': "https://www.masseyratings.com/scores.php?s=262657&sub=11604&all=1&mode=3&format=0", \
'url2015': "https://www.masseyratings.com/scores.php?s=279541&sub=11604&all=1&mode=3&format=0", \
'url2016': "https://www.masseyratings.com/scores.php?s=286577&sub=11604&all=1&mode=3&format=0", \
'url2017': "https://www.masseyratings.com/scores.php?s=295489&sub=11604&all=1&mode=3&format=0", \
'url2018': "https://www.masseyratings.com/scores.php?s=300937&sub=11604&all=1&mode=3&format=0", \
}


for year in range(2010,2019):
    html = urlopen(urldict['url' + str(year)]) #open the URL


    soup = BeautifulSoup(html, 'html.parser') #extracts the good stuff
    
    game_spot = soup.find('pre') #all the games are within this tag as a block of text
    
    #string with all the games, including dates, outcomes, special names, num of overtimes
    game_content = game_spot.text.strip() 
    
    game_list = game_content.split('\n') #each row is a game, makes a list from the rows
    
    game_list = list(filter(None,game_list)) #remove the empty string(s)
    
    del game_list[-1] #remove last part which just declares how many games there are
    
    #list of lists, each one being a game, separating all whitespace, then remove the date of the game
    game_list_list = [game.split()[1:] for game in game_list] 
    
    game_list_list = [[tonumber(i)  for i in game] for game in game_list_list] #turn scores to int
    
    game_list_iter = [[i  for i in game if i !="P"] for game in game_list_list] #delete the playoff tag
    
    #removes all the junk at the end of each inner list, until you get to just the second team's score
    for runthrough in range(10):
        for game in range(len(game_list_iter)):
            num_per_row = sum(1 for x in game_list_iter[game] if not isstring(x))
            if isstring(game_list_iter[game][-1]):
                game_list_iter[game] =  game_list_iter[game][:-1]
            elif num_per_row >2:
                 game_list_iter[game] =  game_list_iter[game][:-1]
    
    #iterates and adjoins adjacent strings 
    for runthrough  in range(7): #this is very inefficient but it works and isn't slow for size of data
        
        #join adajacent strings, otherwise return the two elements as a list (we are three levels deep now: inception)
        game_list_intermediate = [[i+ ' ' + j if isstring(i) & isstring(j) else [i,j]  for i,j in zip_longest(game[::2],game[1::2]) ] for game in game_list_iter]
        
        #bring the third level lists up to the second level (this creates duplicates)
        game_list_intermediate = [[i if type(j) is list else j for j in game  for i in j] for game in game_list_intermediate]
        
        #remove duplicates in the second level 
        game_list_intermediate = [list(OrderedDict.fromkeys(game)) for game in game_list_intermediate]
        
        #removes None from inner lists (these created by zip_longest)
        game_list_iter = [[i for i in game if i is not None] for game in game_list_intermediate]
     
    final_game_list = game_list_iter

    
    for game in final_game_list:
        boo = False
        for i in range(4):
            if isstring(game[i]) and boo == False:
                if game[i].startswith('@'):
                    game[i] = game[i][1:]
                    if i == 0:
                        game.append(1)
                        boo = True
                    elif i==2:
                        temp_game = [game[i], game[i+1], game[i-2], game[i-1]]
                        for j in range(4):
                            game[j] = temp_game[j]
                        game.append(1)    
                        #print(game)
                        boo = True
                elif i==2 and boo == False:
                    game.append(0)
                    boo = True
    
    print(final_game_list)
    #final_game_list[829] = final_game_list[829][:-2] #Pac 12 championship messed up a little
    
    #Export all my hard work to a csv
    with open("CFBGames" + str(year) + ".csv", "w") as outcsv:
        
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        
        #Creates Header
        writer.writerow(['Home Team', 'Home Team Score', 'Away Team', 'Away Team Score', 'Home/Away Boolean'])
        
        writer.writerows(final_game_list)

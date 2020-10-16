# Homework 04 Problems 1+
# Will Arliss

import json
import gzip
import datetime as dt
from string import punctuation

########### Functions ###########

def reader(infile):
    tweets = {}
    errors = [] # unknown errors needing inspection
    countP = 0 # entry passes
    countF = 0 # entry fails
    e1 = 0 # missing { char
    e2 = 0 # missing } char
    e3 = 0 # unknown error
    
    # iterate over every line of the twitter data file
    count = 1
    for line in infile:
        try:
            # try decoding json line
            tweet = json.loads(line.strip())
            countP += 1
        except:
            countF += 1            
            # add { if missing then decode
            if line[0] != '{':
                line = '{'+line
                tweet = json.loads(line.strip())
                e1 += 1
            # add } if missing then decode
            elif line[-1] != '}':
                line = line+'}' 
                tweet = json.loads(line.strip())
                e2 += 1
            # report for further investigation
            else:
                errors.append(line)
                e3 += 1

        # date formatting - access just numeric date
        d_form = tweet['created_at'].split(',')[1].strip()
        # convert date to datetime data type
        tweet['created_at'] = dt.datetime.strptime(d_form, '%d %b %Y %H:%M:%S')    
        # aggregate tweets
        # tweets are indexed by number to avoid the removal of duplicates
        tweets[count] = [tweet['created_at'], tweet['text']]; count+=1          
        # aggregate errors 
        error_report = {'No {':e1, 'No }':e2, 'Unknown':[e3, errors]}

    #print('Successful entries:', countP)
    #print('Corrupted entries:', countF)
    return tweets, error_report



def word_cleaning(raw):
    clean_tweet = {}
    exclude = set(punctuation+'“'+'”'+'’''—') # set of excludable characters
    
    for i in raw:
        # keep only letters that are not special characters
        list_letters_noPunct = [char for char in raw[i][1] if char not in exclude]
        # reform the words
        text_noPunct = ''.join(list_letters_noPunct)
        # create list of words
        list_words = text_noPunct.strip().split()
        # make all lowercase
        list_words = [word.lower() for word in list_words]
        # add list to new dictionary
        clean_tweet[i] = [raw[i][0], list_words]
    
    return clean_tweet



def keywords(twitter):
    O_tweets = {}
    R_tweets = {}
    neither = {}  
    
    for i in twitter: # for each tweet
        success = 0 # ticker to keep track of tweets dont reference OBAMA or ROMNEY
        # LOOK FOR OBAMA WITHIN THE TWEET
        for e1 in twitter[i][1]: # for each individual string of the tweet
            if e1.find('barack') != -1: # look for 'barack' within the string
                O_tweets[i] = twitter[i] # if true, add tweet to obama dict
                success = 1 # if true, change ticker to indicate that reference is found
                break # if true, stop looking for OBAMA in this tweet
            elif e1.find('obama') != -1: # if false, look for 'obama' within string 
                O_tweets[i] = twitter[i] # if true, add tweet to obama dict
                success = 1 # if true, change ticker to indicate that reference is found
                break # if true, stop looking for OBAMA in this tweet
        # LOOK FOR ROMNEY WITHIN THE TWEET
        for e2 in twitter[i][1]: # for each individual string of the tweet
            if e2.find('mitt') != -1: # look for 'mitt' within the string
                R_tweets[i] = twitter[i] # if true, add tweet to romney dict
                success = 1 # if true, change ticker to indicate that reference is found
                break # if true, stop looking for ROMNEY in this tweet
            elif e2.find('romney') != -1: # if false, look for 'romney' within string
                R_tweets[i] = twitter[i] # if true, add tweet to romney dict
                success = 1 # if true, change ticker to indicate that reference is found
                break # if true, stop looking for ROMNEY in this tweet
        # NEITHER OBAMA NOR ROMNEY REFERENCED
        if success == 0: # ticker unchanged because no reference made
            neither[i] = twitter[i] # add tweet to neither dict
    
    #print(len(neither), 'probems occurred')
    return O_tweets, R_tweets  



def plotterInput(O_tweets, R_tweets, outfile1):    
    # calculate tweets per hour and write into input file
    tph_O = {} # tweets per hour - obama
    for o in O_tweets:
        # new time variable, datetime stripped of minutes and seconds
        time_O = O_tweets[o][0].replace(minute=0, second=0)
        # number of tweets for each time variable is added to new dict
        if time_O not in tph_O:
            tph_O[time_O] = 1
        elif time_O in tph_O:
            tph_O[time_O] += 1
    
    tph_O_sorted = {} # tweets per hour, sorted chronologically using base time 0
    count = 0
    for i in sorted(tph_O.keys()):
        # count with base time 0 replaces time index
        tph_O_sorted[count] = tph_O[i]
        count += 1
        
    tph_R = {} # tweets per hour - romney
    for r in R_tweets:
        # new time variable, datetime stripped of minutes and seconds
        time_R = R_tweets[r][0].replace(minute=0, second=0)
        # number of tweets per each time variable is added to new dict
        if time_R not in tph_R:
            tph_R[time_R] = 1
        elif time_R in tph_R:
            tph_R[time_R] += 1
        
    tph_R_sorted = {} # tweets per hour, sorted chronologically using base time 0
    count = 0
    for i in sorted(tph_R.keys()):
        # count with base time 0 replaces time index
        tph_R_sorted[count] = tph_R[i]
        count += 1     
        
    f = open(outfile1, 'w')
    for count in range(len(tph_O)):
        # write time index, obama tweets per hour, and romney tweets per hour
        # to outfile to be used as input in plotter file
        print(count, tph_O_sorted[count], tph_R_sorted[count], sep=' ', file=f)
    f.close()



def wordlist(O_tweets, R_tweets):  
    # strip individual words from each tweet and add to relevant list
    # (with replication)
    words_O = []
    words_R = []
    
    for o in O_tweets:
        # each individual word from each obama tweet is saved to new list
        for e in O_tweets[o][1]:
            words_O.append(e) 
    
    for r in R_tweets:
        # each individual word from each romney tweet is saved to a new list
        for k in R_tweets[r][1]:
            words_R.append(k)

    return words_O, words_R



def yuleCoeff(O_tweets_str, R_tweets_str, outfile2):
    word_freq_O = {} # calculate the frequency of each word in the obama corpus
    for word_O in O_tweets_str:
        if word_O not in word_freq_O:
            word_freq_O[word_O] = 1
        elif word_O in word_freq_O:
            word_freq_O[word_O] += 1
            
    word_freq_R = {} #calculate the frequency of each word in the romney corpus
    for word_R in R_tweets_str:
        if word_R not in word_freq_R:
            word_freq_R[word_R] = 1
        elif word_R in word_freq_R:
            word_freq_R[word_R] += 1
     
    # create a set of unique words contained within both corpuses
    O_words = set(word_freq_O.keys())
    R_words = set(word_freq_R.keys())
    words = O_words & R_words # every word in both corpuses (without replication)
    
    yules = {}
    for w in words:
        fOw = word_freq_O[w] # frequency of given word in obama corpus
        fRw = word_freq_R[w] # frequency of given word in romney corpus
        cw = (fOw-fRw)/(fOw+fRw) # yule coefficient calculation
        yules[w] = cw # c=1 is obama specific, c=-1 is romney specific
        
    obama_yules = {}    
    romney_yules = {}
    # sort the yule coefficients from greatest to least
    yules = sorted(yules.items(), key=lambda x: x[1], reverse=True)
    for i in yules[:100]: # add the first 100 coefficients to the obama yule dict
        obama_yules[i[0]] = i[1]
    for i in yules[-100:]: # add the last 100 coefficients to the romney yule dict
        romney_yules[i[0]] = i[1]
    
    f = open(outfile2, 'w', encoding='utf-8')
    # iterate over keys and values in both the obama and the romney yule dicts
    for (k1, v1), (k2, v2) in zip(obama_yules.items(), 
                                  sorted(romney_yules.items(), 
                                         key=lambda x: x[1])):
        # add the obama yule coefficients to the outfile, formatted properly
        print(k1.rjust(15), format(v1, '1.5f').ljust(10), sep=' ', end=' ', file=f)
        # add the romney yule coefficients to the outfile, formatted properly
        print(k2.rjust(18), format(v2, '1.5f').ljust(8), sep=' ', end='\n', file=f)
    f.close()


########### Questions ###########
    
### P1 ###
''' Load tweets from json into dictionary. Tweets are returned as 'raw_twitter'.
Report of repairs is also returned as 'errors'. '''
infile = gzip.open('HW04_twitterData.json.txt.gz', 'rt', encoding='utf-8')
raw_twitter, errors = reader(infile)
infile.close()

''' Strip special characters from words, apply standard format, split tweet 
into list of words. '''
twitter = word_cleaning(raw_twitter)

''' Divide tweets into Obama corpus and Romney corpus based on the presence
of either's name in a tweet. '''
O_tweets, R_tweets = keywords(twitter)

### P2 ###
''' Format an input file for the plotter script. Returns tweets per hour
for Obama and Romney corpuses. 'input_p2.txt' will be read into plotter 
script to produce graph for write up. '''
#outfile1 = 'input_p2.txt'
#plotterInput(O_tweets, R_tweets, outfile1)

### P3 ###
''' Split each individual tweet for the two corpuses into individual strings.
One long list of all words from every tweet is returned for each corpus. '''
#O_tweets_str, R_tweets_str = wordlist(O_tweets, R_tweets)

''' Format an output file of the top 100 yule coefficients for each candidate. '''
#outfile2 = 'yule_coefficients.txt'
#yuleCoeff(O_tweets_str, R_tweets_str, outfile2)

# Homework 06
# Will Arliss

'''
The code consists of imports in lines 8-17, functions in lines 24-399, 
problem 0 in lines 415-426, problem 1 in lines 429-440, problem 2 in lines
444-499, problem 3 in lines 502-515, and problem 4 in lines 518-536
'''

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import gzip
import datetime as dt
import json
from string import punctuation
import csv
import matplotlib.pyplot as plt
import os

########################################################################



############################  FUNCTIONS ################################
def reader(infile):
    '''Read in JSON payloads, fixing any problem lines, and format datetime. 
    Return list of all tweets and list of problem lines. Prints error lines'''
    
    tweets = []
    errors = []
    
    # Iterate over every line of the twitter data file
    for line in infile:
        try:
            # Try decoding json line
            tweet = json.loads(line.strip())
        except:
            # Add { if missing then decode
            if line[0] != '{':
                line = '{'+line
                tweet = json.loads(line.strip())
            # Add } if missing then decode
            elif line[-1] != '}':
                line = line+'}' 
                tweet = json.loads(line.strip())
            # Report problem line for further investigation
            else:
                errors.append(line)

        # Date formatting - access just numeric date
        d_form = tweet['created_at'].split(',')[1].strip()
        tweet['created_at'] = dt.datetime.strptime(d_form, '%d %b %Y %H:%M:%S')    
        # Clean the tweet text
        text = word_cleaning(tweet['text'])
        tweet['text'] = text
        # Aggregate the tweet data       
        tweets.append({'datetime':tweet['created_at'], 
                       'text':tweet['text']})     
    
    # Print problem lines if any exist then return tweet data
    [print(i) for i in errors if len(errors) != 0]
    return tweets



def word_cleaning(raw):
    '''Remove special characters from tweet texts. Returns clean word string''' 

    # Globalize excludable and special characters
    global exclude
    global special
    
    # Split text into list of words
    text = raw.split()
    tweet = []
    
    # Iterate over every word in the text list
    for t in text:
        # Test if a special character from VADER lexicon is in the word
        if t in special:
            pass
        else:
            # Test if the word is entirely uppercase 
            if t.isupper():
                # Remove excludable characters from word
                clean_tweet = [char for char in t if char not in exclude] 
            else:
                # Remove excludable characters from word and make all chars lowercase
                clean_tweet = [char.lower() for char in t if char not in exclude]
            t = ''.join(clean_tweet)
        # Append the word to the new tweet
        tweet.append(t)
        
    tweet = ' '.join(tweet)
    return tweet



def contains_obama(text):
    '''Checks the string ` text ` for mention of Obama. Is
    case - insensitive'''
    
    text = text.lower() 
    # Checks for mention of Obama in tweet
    if 'obama' in text or 'barack' in text:
        return True
    
    return False



def contains_romney(text):
    '''Checks the string ` text ` for mention of Romney. Is
    case - insensitive'''

    text = text.lower()
    # Checks for mention of Romney in tweet
    if 'romney' in text or 'mitt' in text:
        return True

    return False



def keywords(twitter):
    '''Exact word cleaning function from HW04'''
    
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



def export(file, obama, romney):
    '''Export twitter data and polarity scores to .csv file'''
    
    # Initialize the sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()
    # Open file to write
    f = open(file, 'w')
    # Write the headers into the file
    print('ID', 'Datetime', 'Corpus', 'Negative', 'Neutral', 'Positive', 'Compound', sep=',', file=f)

    done = [] # Keep track of tweets that are already written to the file
    # Iterate over Obama corpus
    for o in obama:
        
        # Make sure the tweet has not already been written to the file
        if o['id'] not in done:
            done.append(o['id'])
            # Calculate the polarity score of the tweet
            p = analyzer.polarity_scores(o['text'])
            # Append necessary information to file
            try: # Corpus 1 has datetime formatted as item of list
                print(o['id'], o['datetime'][0], 'O', 
                      p['neg'], p['neu'], p['pos'], 
                      p['compound'], sep=',', file=f) 
            except TypeError: # Corpus 2 has datetime formatted as datetime object
                print(o['id'], o['datetime'], 'O', 
                      p['neg'], p['neu'], p['pos'], 
                      p['compound'], sep=',', file=f) 
            except KeyError:
                pass
      
    # Iterate over Romney corpus
    for r in romney:
        
        # Make sure the tweet has not already been written to the file
        if r['id'] not in done:
            done.append(r['id'])
            # Calculate the polarity score of the tweet
            p = analyzer.polarity_scores(r['text'])
            # Append necessary information to file
            try: # Corpus 1 has datetime formatted as item of list
                print(r['id'], r['datetime'][0], 'R', 
                      p['neg'], p['neu'], p['pos'], 
                      p['compound'], sep=',', file=f)   
            except TypeError: # Corpus 2 has datetime formatted as datetime object
                print(r['id'], r['datetime'], 'R', 
                      p['neg'], p['neu'], p['pos'], 
                      p['compound'], sep=',', file=f) 
            except KeyError:
                pass
    
    # Close the file    
    f.close()
    
    

def load_tidy(f_name, data):
    '''Load twitter data from tidy .csv file'''
    
    # Open file
    f = open(f_name, 'r')
    # Load content
    content = csv.reader(f, delimiter=',')
    
    tweet_dta = []
    # Iterate over every line of the file
    for line in content:
        
        # Skip over first header line
        try:
            int(line[0])
        except ValueError:
            continue

        # Save twitter data from .csv line to dictionary
        tweet = {'id' : int(line[0]), 
                 'datetime' : dt.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S'),
                 'corpus' : line[2], 
                 'neg' : float(line[3]), 
                 'neu' : float(line[4]), 
                 'pos' : float(line[5]),
                 'comp' : float(line[6])}
        
        # Append dict to list
        tweet_dta.append(tweet)
    
    # Close the file
    f.close()
    # Return the list of dictionaries
    return tweet_dta
  
  
    
def summary(data, candidate):
    '''Present summary information on given corpus'''
    
    # Save the compound score, positive compound scores, and negative compound scores
    comp = [i['comp'] for i in data if i['corpus'] == candidate]
    nPos = len([i for i in comp if i>0])
    nNeg = len([i for i in comp if i<0])
    
    # Save the negative proportion, neutral proportion, and positive proportion
    meanNeg = [i['pos'] for i in data if i['corpus'] == candidate]
    meanNeu = [i['neu'] for i in data if i['corpus'] == candidate]
    meanPos = [i['neg'] for i in data if i['corpus'] == candidate]
   
    print(candidate)
    # Present statistics
    print(f'Mean compound score of all {candidate} tweets:', 
          format(sum(comp)/len(comp), '1.3f'))
    print(f'Proportion of {candidate} tweets with positive compound score:', 
          format(nPos/len(comp), '1.3f'))
    print(f'Proportion of {candidate} tweets with negative compound score:', 
          format(nNeg/len(comp), '1.3f'))
    print(f'Mean proportion of negative words in {candidate} tweets:', 
          format(sum(meanNeg)/len(meanNeg), '1.3f'))
    print(f'Mean proportion of neutral words in {candidate} tweets:', 
          format(sum(meanNeu)/len(meanNeu), '1.3f'))
    print(f'Mean proportion of positive words in {candidate} tweets:', 
          format(sum(meanPos)/len(meanPos), '1.3f'))
    
    plt.figure()
    # Create historgram of compound scores
    plt.hist(comp, bins=10)
    plt.xlabel('Compound VADER Polarity Score')
    plt.title(f'{candidate}: Compound Scores')
    plt.tight_layout()    
    # Save plot to folder
    path = os.getcwd()+'\\figures'
    plt.savefig(os.path.join(path, f'hist_{candidate}.svg'))



def plotter_input(data):
    '''Format twitter data for plotter functions'''
    
    sph_O = {}
    sph_R = {}
    # Iterate over all twitter data
    for d in data:
        
        # Romney corpus
        if d['corpus'] == 'O':
            # Shave datetime down to the hour
            t = d['datetime'].replace(minute=0, second=0)
            
            # Append compound score to new Romney corpus 
            if t not in sph_O:
                sph_O[t] = [d['comp']]
            else:
                sph_O[t].append(d['comp'])
        
        # Obama Corpus        
        elif d['corpus'] == 'R':
            # Shave datetime down to the hour
            t = d['datetime'].replace(minute=0, second=0)
            
            # Append compound score to new Obama corpus
            if t not in sph_R:
                sph_R[t] = [d['comp']]
            else:
                sph_R[t].append(d['comp'])
           
    sph_O_sorted = {} 
    count = 0
    # Create new sorted dictionary 
    for i in sorted(sph_O.keys()):
        
        # Replace time with index value
        sph_O_sorted[count] = sum(sph_O[i])/len(sph_O[i])
        count += 1
        
    sph_R_sorted = {} 
    count = 0
    # Create new sorted dictionary 
    for i in sorted(sph_R.keys()):
        
        # Replace time with index value
        sph_R_sorted[count] = sum(sph_R[i])/len(sph_R[i])
        count += 1    
    
    # Return sorted dictionaries        
    return sph_O_sorted, sph_R_sorted


    
def plotter1(O, R):
    '''Time series plot of Obama and Romney twitter sentiment'''
    
    # Save time, obama scores, romney scores, and total scores
    time = [k for k,v in O.items()]
    obama = [v for k,v in O.items()]
    romney = [v for k,v in R.items()]
    total = [(o+r)/2 for o,r in zip(obama, romney)]
    # Set path to save .svg files
    path = os.getcwd()+'\\figures'
    
    plt.figure()
    # Plot time on x and Obama in blue on y and Romney in red on y
    plt.plot(time, obama, color='C0', label='Obama')
    plt.plot(time, romney, color='C3', label='Romney')
    # Index number of hours since first tweet
    plt.xlabel('Hours since 2012/10/23 1:00')
    plt.ylabel('Compound VADER Polarity Score')
    plt.title('Avg Twitter Sentiment of Obama & Romney / Time')
    plt.legend()
    plt.tight_layout()  
    # Save plot to folder
    plt.savefig(os.path.join(path, 'ts_OR.svg'))
    
    plt.figure()
    # Plot time on x and total elextion sentiment on y
    plt.plot(time, total)
    # Index number of hours since first tweet
    plt.xlabel('Hours since 2012/10/23 1:00')
    plt.ylabel('Compound VADER Polarity Score')
    plt.title('Avg Twitter Sentiment of Election / Time')
    plt.tight_layout()    
    # Save plot to folder
    plt.savefig(os.path.join(path, 'ts_all.svg'))
    
    
    
def plotter2(O1, O2, R1, R2):
    '''Time series plot to compare old and new obama/romney corpus'''
    
    # Save time and all the corpus variables
    time = [k for k,v in O1.items()]
    obama1 = [v for k,v in O1.items()]
    obama2 = [v for k,v in O2.items()]
    romney1 = [v for k,v in R1.items()]
    romney2 = [v for k,v in R2.items()]
    # Set path to save .svg file
    path = os.getcwd()+'\\figures'
    
    plt.figure()
    # Plot the two Obama corpus against time on x
    plt.plot(time, obama1, color='C0', alpha=.6, label='HW04')
    plt.plot(time, obama2, color='C3', alpha=.6, label='HW06')
    # Index number of hours since first tweet
    plt.xlabel('Hours since 2012/10/23 1:00')
    plt.ylabel('Compound VADER Polarity Score')
    plt.title('Sentiment Analysis of Obama Corpus: HW04 vs HW06')
    plt.legend()
    plt.tight_layout()  
    # Save plot to folder
    plt.savefig(os.path.join(path, 'ts_O1O2.svg'))
    
    plt.figure()
    # Plot the two Romney corpus against time on x
    plt.plot(time, romney1, color='C0', alpha=.6, label='HW04')
    plt.plot(time, romney2, color='C3', alpha=.6, label='HW06')
    # Index number of hours since first tweet
    plt.xlabel('Hours since 2012/10/23 1:00')
    plt.ylabel('Compound VADER Polarity Score')
    plt.title('Sentiment Analysis of Romney Corpus: HW04 vs HW06')
    plt.legend()
    plt.tight_layout()  
    # Save plot to folder
    plt.savefig(os.path.join(path, 'ts_R1R2.svg'))

    
    
########################################################################




######## P.0 ###########################################################
# Create set of excludable characters for word cleaning, keep '!'
exclude = set(punctuation.replace('!', '“”’—'))

# Create list of special characters from VADER lexicon
analyzer = SentimentIntensityAnalyzer()
lex = analyzer.make_lex_dict()
special = [l for l in lex if not l.isalnum()]

# Open twitter dataset
infile = gzip.open('HW04_twitterData.json.txt.gz', 'rt', encoding='utf-8')
all_tweets = reader(infile)
infile.close()

######## P.1 ###########################################################
sentence1 = "Alicia and Ben still have the best , most romantic story arc."
sentence2 = "Reed is a great scientist but a terrible husband (and father)!"

analyzer = SentimentIntensityAnalyzer()
result1 = analyzer.polarity_scores(sentence1)
result2 = analyzer.polarity_scores(sentence2)
LEN_LEXICON = len(analyzer.make_lex_dict())

### P.1.4 ###
print("R1 -", result1)
print("R2 -", result2)
print("There are", LEN_LEXICON , "tokens in the VADER lexicon.")

######## P.2 ###########################################################
### P.2.1 ###
# Add ID number for easier comparison
ID = 0
for tweet in all_tweets:
    tweet['id'] = str(ID)
    ID += 1

obamaC2 = []
romneyC2 = []

# Split into new Obama and Romney corpuses
for tweet in all_tweets:
    text = tweet['text']
    
    if contains_obama(text):
        obamaC2.append(tweet)
    if contains_romney(text):
        romneyC2.append(tweet)

# Format to look like HW04 data
all_tweets_split = {}
count = 1
for tweet in all_tweets:
    contents = [tweet['id'], (tweet['text'].split())]
    all_tweets_split[count] = contents
    count += 1
# Split into Obama and Romney corpuses using exact HW04 function    
oC1, rC1 = keywords(all_tweets_split)
obamaC1 = [{'id':oC1[tweet][0], 'text':' '.join(oC1[tweet][1])} for tweet in oC1]
romneyC1 = [{'id':rC1[tweet][0], 'text':' '.join(rC1[tweet][1])} for tweet in rC1]

### P.2.2 ###
# Convert to sets for comparison
obamaC2_set = set([tweet['id'] for tweet in obamaC2])
obamaC1_set = set([tweet['id'] for tweet in obamaC1])
romneyC2_set = set([tweet['id'] for tweet in romneyC2])
romneyC1_set = set([tweet['id'] for tweet in romneyC1])   
# Was in oC1, now in rC2 
o1r2 = len(obamaC1_set & romneyC2_set)
# Was in rC1, now in oC2
r1o2 = len(romneyC1_set & obamaC2_set)
# Was in oC1, now in oC2
o1o2 = len(obamaC1_set & obamaC2_set)
# Was in rC1, now in rC2
r1r2 = len(romneyC1_set & romneyC2_set)
# Display contingency table
print(f'''\t    Obama (C2)  Romney (C2)
 Obama (C1)   {o1o2}        {r1o2}
Romney (C1)   {r1o2}        {r1r2}''')

### P.2.3 ###
file = 'OR_tweet_scores_warliss.csv'
# Export twitter data to tidy .csv file
export(file, obamaC2, romneyC2)
# Read data from tidy .csv file back in
tidy_tweets = load_tidy(file, all_tweets)

######## P.3 ###########################################################
# Create lists of statistics from twitter data
tweet_data = {key:[] for key in tidy_tweets[0].keys()}
[{tweet_data[k].append(v) for k,v in tweet.items()} for tweet in tidy_tweets]

#[print(v, end=', ') for k,v in tidy_tweets[0].items()]; print()
#[print(tweet_data[data][0], end=', ') for data in tweet_data]
#print()
#[print(v, end=', ') for k,v in tidy_tweets[-1].items()]; print()
#[print(tweet_data[data][-1], end=', ') for data in tweet_data]

# Print summary output
summary(tidy_tweets, 'O')
print()  
summary(tidy_tweets, 'R')

######## P.4 ###########################################################
# Format twitter data for plotter
plotO2, plotR2 = plotter_input(tidy_tweets)
# Plot formatted twitter data in first plotter function
plotter1(plotO2, plotR2)
    
file = 'OR_tweet_scores_HW04.csv'
# Add datetime to old corpuses
#for o,r in zip(obamaC1, romneyC1):
#    o['datetime'] = [tweet['datetime'] for tweet in all_tweets if tweet['id'] == o['id']]
#    r['datetime'] = [tweet['datetime'] for tweet in all_tweets if tweet['id'] == r['id']]
# Export old corpus twitter data to .csv file
export(file, obamaC1, romneyC1)
# Read data from tidy .csv file back in
tidy_tweets_hw4 = load_tidy(file, all_tweets)  
  
# Format old twitter data for plotter
plotO1, plotR1 = plotter_input(tidy_tweets_hw4)
# Plot formatted twitter data in first plotter function
plotter2(plotO1, plotO2, plotR1, plotR2)



    
    
    
    

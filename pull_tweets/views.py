import re
import json
import tweepy

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse


def index(request):
    if request.method == 'POST':
        data = json.load(request)
        payload = data.get('payload')
        hashtag = payload['hashtag']
        user = payload['user']
        count = payload['count']

        if hashtag or user:
            if not hashtag:
                hashtag = ''
                hashtag_query = ''
            else:
                hashtag_query = ' #' + hashtag
            if not user:
                user = ''
                user_query = ''
            else:
                user_query = ' from:' + user
            print('Hashtag:', hashtag)
            print('Użytkownik:', user)
            print('Ilość:', count)

            client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)

            # query = '#war lang:en'
            query = 'lang:en' + hashtag_query + user_query
            print(query)

            tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                                 max_results=count)
            for tweet in tweets.data:
                print(clean_str(tweet.text))
                print("___________________________________________________________")
            # return render(request, 'pull_tweets/index.html', {'hashtag': hashtag})
            return JsonResponse({'hashtag': hashtag, 'user': user, 'count': count})

    return render(request, 'pull_tweets/index.html')

# def view_tweets(request):
#     hashtag = request.POST.get('hashtag')
#     lang = request.POST.get('lang')
#     count = request.POST.get('count')
#
#     return render(request, 'pull_tweets/pulled_tweets.html', {'hashtag': hashtag})


def clean_str(string):
    """
    Tokenization/string cleaning for the dataset.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    # substitute single chars and not important chars with space
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    # add space before apostrophes
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    # add space before and after punctuation
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    # remove excess whitespace
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

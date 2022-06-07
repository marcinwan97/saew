import re
import json
import tweepy
import tensorflow as tf
import numpy as np
import tensorflow_text
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

# outputs = {
#     0: "Anger",
#     1: "Disgust",
#     2: "Fear",
#     3: "Joy",
#     4: "Sadness",
#     5: "Surprise"
# }

outputs = {
    0: "Gniew",
    1: "Obrzydzenie",
    2: "Strach",
    3: "Radość",
    4: "Smutek",
    5: "Zaskoczenie"
}


def index(request):
    return render(request, 'pull_tweets/index.html')


def multi_analysis(request):
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

        query = 'lang:en' + hashtag_query + user_query
        print(query)

        tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                             max_results=count)

        dataset_name = 'combined'
        saved_model_path = './{}_bert'.format(dataset_name.replace('/', '_'))

        reloaded_model = tf.saved_model.load(saved_model_path)
        results = []
        for tweet in tweets.data:
            reloaded_results = tf.sigmoid(reloaded_model(tf.constant([clean_str(tweet.text)])))
            results.append(outputs[int(np.argmax(reloaded_results))])
            # print(clean_str(tweet.text))
            # print("___________________________________________________________")
        anger = results.count('Gniew')
        disgust = results.count('Obrzydzenie')
        fear = results.count('Strach')
        joy = results.count('Radość')
        sadness = results.count('Smutek')
        surprise = results.count('Zaskoczenie')
        # return render(request, 'pull_tweets/index.html', {'hashtag': hashtag})
        return JsonResponse({'hashtag': hashtag, 'user': user, 'count': count, 'anger': anger, 'disgust': disgust,
                             'fear': fear, 'joy': joy, 'sadness': sadness, 'surprise': surprise})


def single_analysis(request):
    data = json.load(request)
    payload = data.get('payload')
    # hashtag = payload['hashtag']
    # user = payload['user']
    # count = payload['count']
    text = payload['text']

    if text:
        dataset_name = 'combined'
        saved_model_path = './{}_bert'.format(dataset_name.replace('/', '_'))

        reloaded_model = tf.saved_model.load(saved_model_path)
        result = tf.sigmoid(reloaded_model(tf.constant([clean_str(text)])))
        result = outputs[int(np.argmax(result))]

        return JsonResponse({'result': result})


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

    # string = re.sub(r"rt", "", string)

    return string.strip().lower()

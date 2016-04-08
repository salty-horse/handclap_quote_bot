#!/usr/bin/env python3
# encoding: utf-8

import os
import random
import tweepy
import wikiquote
from wikiquote.utils import (
    NoSuchPageException,
    DisambiguationPageException,
)
from secret import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
bad_words = set(open(ROOT_PATH + 'badwords.txt').read().splitlines())

# Yeah...
bad_titles = [
    'hitler',
    'kampf',
    'greg giraldo',
]

def get_quote():
    titles = wikiquote.random_titles()
    for title in titles:
        lower_title = title.lower()
        print('trying title', title)
        quotes = None
        if title.startswith('List of'):
            continue
        if any(w in lower_title for w in bad_titles):
            continue
        try:
            quotes = wikiquote.quotes(title, max_quotes=1000)
        except (NoSuchPageException, DisambiguationPageException):
            pass

        if not quotes:
            continue

        quotes = [q for q in quotes if len(q) < 140]

        random.shuffle(quotes)
        for quote in quotes:
            # Don't use lines of dialogue
            if '\n' in quote:
                continue

            # Assume this is a quote from a character and not a person
            if ':' in quote[:20]:
                continue

            # Assume this is an external link and not a quote
            if lower_title in quote.lower():
                continue

            # Strip enclosing quotes
            if quote[0] == quote[-1] and quote[0] in ('"', "'"):
                quote = quote[1:-2]

            words = quote.split()
            if len(words) < 4:
                continue
            if any(w in quote.lower() for w in bad_words):
                continue
            new_quote = ' \U0001f44f '.join(words)
            if len(new_quote) <= 140:
                print('Chosen quote from', title)
                return new_quote

    # Couldn't find matching quotes
    return None

def post_tweet():
    attempts = 0
    while attempts < 20:
        quote = get_quote()
        if quote:
            break
        attempts += 1

    if quote is None:
        print('Too many attempts. Quitting')

    print('Tweeting:', quote)
    # Submit to Twitter
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.secure = True
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET)
    api = tweepy.API(auth)
    api.update_status(quote)

if __name__ == '__main__':
    post_tweet()

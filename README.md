twitter_signature
=================

Sample Python program that shows you how to correctly authorize and sign a request to the Twitter API

This sample code is based on the [Creating a Signature](https://dev.twitter.com/docs/auth/creating-signature) and [Authorizing Request](https://dev.twitter.com/docs/auth/authorizing-request) documents.

I assume you know how to generate the proper keys, tokens and secrets for your [app](https://dev.twitter.com/apps)


Setting up the environment:

    $ git clone git://github.com/kelsmj/twitter_signature.git
    $ mkvirtualenv twitter_signature
    $ pip install -r requirements.txt
    $ touch settings.cfg

Populate the settings.cfg with the following:

    [Keys]
    twitter_consumer_secret: YOUR_CONSUMER_SECRET
    twitter_consumer_key: YOUR_CONSUMER_KEY
    access_token: YOUR_ACCESS_TOKEN
    access_token_secret: YOUR_ACCESS_TOKEN_SECRET

Run the program:

    $ python twitter_signature.py



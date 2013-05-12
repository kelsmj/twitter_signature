import ConfigParser
import urllib
import random
import base64
import hmac
import binascii
import time
import collections
import hashlib
import requests
import json


def escape(s):
    """Percent Encode the passed in string"""
    return urllib.quote(s, safe='~')


def get_nonce():
    """Unique token generated for each request"""
    n = base64.b64encode(
        ''.join([str(random.randint(0, 9)) for i in range(24)]))
    return n


def generate_signature(method, url, url_parameters, oauth_parameters,
                       oauth_consumer_key, oauth_consumer_secret,
                       oauth_token_secret=None, status=None):
    """Create the signature base string"""

    #Combine parameters into one hash
    temp = collect_parameters(oauth_parameters, status, url_parameters)

    #Create string of combined url and oauth parameters
    parameter_string = stringify_parameters(temp)

    #Create your Signature Base String
    signature_base_string = (
        method.upper() + '&' +
        escape(str(url)) + '&' +
        escape(parameter_string)
    )

    #Get the signing key
    signing_key = create_signing_key(oauth_consumer_secret, oauth_token_secret)

    return calculate_signature(signing_key, signature_base_string)

def collect_parameters(oauth_parameters, status, url_parameters):
    """Combines oauth, url and status parameters"""
    #Add the oauth_parameters to temp hash
    temp = oauth_parameters.copy()

    #Add the status, if passed in.  Used for posting a new tweet
    if status is not None:
        temp['status'] = status

    #Add the url_parameters to the temp hash
    for k, v in url_parameters.iteritems():
        temp[k] = v

    return temp


def calculate_signature(signing_key, signature_base_string):
    """Calculate the signature using SHA1"""
    hashed = hmac.new(signing_key, signature_base_string, hashlib.sha1)

    sig = binascii.b2a_base64(hashed.digest())[:-1]

    return escape(sig)


def create_signing_key(oauth_consumer_secret, oauth_token_secret=None):
    """Create key to sign request with"""
    signing_key = escape(oauth_consumer_secret) + '&'

    if oauth_token_secret is not None:
        signing_key += escape(oauth_token_secret)

    return signing_key


def create_auth_header(parameters):
    """For all collected parameters, order them and create auth header"""
    ordered_parameters = {}
    ordered_parameters = collections.OrderedDict(sorted(parameters.items()))
    auth_header = (
        '%s="%s"' % (k, v) for k, v in ordered_parameters.iteritems())
    val = "OAuth " + ', '.join(auth_header)
    return val


def stringify_parameters(parameters):
    """Orders parameters, and generates string representation of parameters"""
    output = ''
    ordered_parameters = {}
    ordered_parameters = collections.OrderedDict(sorted(parameters.items()))

    counter = 1
    for k, v in ordered_parameters.iteritems():
        output += escape(str(k)) + '=' + escape(str(v))
        if counter < len(ordered_parameters):
            output += '&'
            counter += 1

    return output


def get_oauth_parameters(consumer_key, access_token):
    """Returns OAuth parameters needed for making request"""
    oauth_parameters = {
        'oauth_timestamp': str(int(time.time())),
        'oauth_signature_method': "HMAC-SHA1",
        'oauth_version': "1.0",
        'oauth_token': access_token,
        'oauth_nonce': get_nonce(),
        'oauth_consumer_key': consumer_key
    }

    return oauth_parameters

if __name__ == '__main__':
    #Read the Config File to get the twitter keys and tokens
    config = ConfigParser.RawConfigParser()
    config.read('settings.cfg')

    #method, url and parameters to call
    method = "get"
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    url_parameters = {
        'exclude_replies': 'true'
    }

    #configuration hash for the keys
    keys = {
        "twitter_consumer_secret": config.get(
            'Keys', 'twitter_consumer_secret'),
        "twitter_consumer_key": config.get('Keys', 'twitter_consumer_key'),
        "access_token": config.get('Keys', 'access_token'),
        "access_token_secret": config.get('Keys', 'access_token_secret')
    }

    oauth_parameters = get_oauth_parameters(
        keys['twitter_consumer_key'],
        keys['access_token']
    )

    oauth_parameters['oauth_signature'] = generate_signature(
        method,
        url,
        url_parameters, oauth_parameters,
        keys['twitter_consumer_key'],
        keys['twitter_consumer_secret'],
        keys['access_token_secret']
    )

    headers = {'Authorization': create_auth_header(oauth_parameters)}

    url += '?' + urllib.urlencode(url_parameters)

    r = requests.get(url, headers=headers)

    print json.dumps(json.loads(r.text), sort_keys=False, indent=4)

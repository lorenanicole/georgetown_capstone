# Reddit

### Getting Started

We'll be using  PRAW (Python Reddit API Wrapper) to get data from Reddit.
You'll need to `pip install praw` in the `virtualenv` for Python 3.6.

There are three types of authorization flows, we'll be authenticating to
use a [web application](http://praw.readthedocs.io/en/latest/getting_started/authentication.html#script-application).

1. [Register Reddit dev application](https://www.reddit.com/prefs/apps/)
2. Obtain the `client_id` and `client_secret` as shown [here](https://stackoverflow.com/questions/28955541/how-to-get-access-token-reddit-api)


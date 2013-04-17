===========
Plivo Python Helper
===========

[![Build Status](https://travis-ci.org/agiliq/plivo-python.png?branch=master)](https://travis-ci.org/agiliq/plivo-python)

Example code to make a call
---------------------------

    #!/usr/bin/env python

    import plivo

    auth_id = 'XXXXXXXXXXXXXXXXXXXX'
    auth_token = 'XXXXXXXXXXXXXXXXXXXXXXXXX'

    p = plivo.RestAPI(auth_id, auth_token)

    params = {'to': '121212121212',
    'from': '1212121212',
    'ring_url': 'http://example.com/ring_url'
    'answer_url': 'http://example.com/answer_url',
    'hangup_url': 'http://example.com/hangup_url'
    }

    response = p.make_call(params)

The response will always be a tuple of two elements. The first element is the HTTP status code and second is the dictionary from the API. More details available at: https://www.plivo.com/docs/


Running Tests
-----------------------

Create a file named auth_secrets.py and give it your `AUTH_ID` and `AUTH_TOKEN`.
Run `python tests.py`

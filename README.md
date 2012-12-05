BURP-HTML
=========

URL, HTTP Headers and WHOIS analyzer for the Better URL Reputation Platform

Tested on Python 2.6+ / 3.1+


Installation
------------

1. Install the BURP fork of python-whois (https://github.com/eecs-354-burp/python-whois) 

2. Execute the following command:

        python setup.py install


API
---

The `whois_headers(url, domain):` takes in a full URL (eg. `http://www.google.com/query=harry+potter`) and a domain(eg. `google.com`) for a website returns a dictionary with the following format:

    {
      "whois":   {
          "name"        : String,
          "registrat"   : String,
          "registrant"  : String,
          "creation_date" : String,
          "last_updated" : String,
          "expiration_date" : String
      },
      "httpHeaders":   {
        <all the key-value pairs in the reponse header to the HTTP request made on the given URL>
      },
      "ip":              String
    }

Command-Line Usage
-------------

BURP-HTML can be run from the command line like so:

    python burp_url/analyzer.py http://www.example.com

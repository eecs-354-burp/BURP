BURP-HTML
=========

URL, HTTP Headers and WHOIS analyzer for the Better URL Reputation Platform

Tested on Python 2.6+ / 3.1+


Installation Pre-requisites
-------------

The directory contains a folder called `python-whois`. Please navigate to that folder and install the python-whois module using:

        python setup.py install

before using burp_url.py


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

    python burp-url.py http://www.example.com

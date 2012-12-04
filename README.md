BURP-HTML
=========

[PyQuery](http://pypi.python.org/pypi/pyquery)-based HTML analyzer for the Better URL Reputation Platform

Tested on Python 2.6+ / 3.1+

Installation
------------

    python setup.py install

Usage
-----

BURP-HTML is optimized for analyzing URLs:

    from htmlanalyzer import *
    analyzer = HTMLAnalyzer(url)
    analysis = analyzer.analyze()

To analyze an HTML string directly, be sure to call the `setUrl()` method with the URL where the HTML originated from:

    from htmlanalyzer import *
    html = '<html>Hello World!</html>'
    analyzer = HTMLAnalyzer()
    analyzer.loadHtml(html)
    analyzer.setUrl('http://www.example.com')
    analysis = analyzer.analyze()

API
---

The `analyze()` method returns a dictionary with the following format:

    {
      "numCharacters":                Int,
      "percentWhitespace":            Float,
      "percentScriptContent":         Float,
      "numIframes":                   Int,
      "numScripts":                   Int,
      "numScriptsWithWrongExtension": Int,
      "numEmbeds":                    Int,
      "numObjects":                   Int,
      "numSuspiciousObjects":         Int,
      "numHyperlinks":                Int,
      "numMetaRefresh":               Int,
      "numHiddenElements":            Int,
      "numSmallElements":             Int,
      "hasDoubleDocuments":           Bool,
      "numUnsafeIncludedUrls":        Int,
      "numExternalUrls":              Int,
      "percentUnknownElements":       Float
    }

Running the Test Suite
-------------

    python tests.py

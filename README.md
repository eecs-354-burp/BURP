BURP-HTML
=========

[PyQuery](http://pypi.python.org/pypi/pyquery)-based HTML analyzer for the Better URL Reputation Platform

Tested on Python 2.6+ / 3.1+

Installation
------------

    python setup.py install

Usage
-----

The BURP HTML analyzer is optimized for retrieving and analyzing HTML from URLs:

    from burphtml.analyzer import HTMLAnalyzer
    analyzer = HTMLAnalyzer(url)
    analysis = analyzer.analyze()
    ...
    analyzer.loadUrl(url2)
    analysis2 = analyzer.analyze()
    ...

To analyze an HTML string directly, be sure to call the `setUrl()` method with the URL where the HTML originated from:

    from burphtml.analyzer import HTMLAnalyzer
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

    python setup.py test

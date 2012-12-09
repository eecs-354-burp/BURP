BURP
====

The Better URL Reputation Platform

By Khalid Aziz, Peter Li, Christopher Moran, and Ethan Romba

Installation
------------

1. Install [Weka](http://www.cs.waikato.ac.nz/ml/weka/) 3.7.7+

2. Follow [these instructions](http://weka.wikispaces.com/CLASSPATH) to add the weka.jar file to your CLASSPATH

3. Install the [BURP fork of python-whois](https://github.com/eecs-354-burp/python-whois):

        git clone https://github.com/eecs-354-burp/python-whois
        cd python-whois
        python setup.py install

4. Install BURP:

        git clone https://github.com/eecs-354-burp/BURP
        cd BURP
        python setup.py install

Usage
-----

### BURP

Run BURP from the command line, passing the URL you would like to classify:

    burp [URL]

### HTML Analyzer

The BURP HTML analyzer is optimized for retrieving and analyzing HTML from URLs:

    from burp.html import HTMLAnalyzer
    analyzer = HTMLAnalyzer(url)
    analysis = analyzer.analyze()
    ...
    analyzer.loadUrl(url2)
    analysis2 = analyzer.analyze()
    ...

To analyze an HTML string directly, be sure to call the `setUrl()` method with the URL where the HTML originated from:

    from burp.html import HTMLAnalyzer
    html = '<html>Hello World!</html>'
    analyzer = HTMLAnalyzer()
    analyzer.loadHtml(html)
    analyzer.setUrl('http://www.example.com')
    analysis = analyzer.analyze()

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

Running the HTML Test Suite
---------------------------

    python setup.py test
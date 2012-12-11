BURP - The Better URL Reputation Platform
====

Developed by Khalid Aziz, Peter Li, Christopher Moran, and Ethan Romba

BURP is a Python package that performs static analysis of HTML, URL tokens, HTTP headers, and WHOIS information, extracting features that can be used to evaluate the reputation of an arbitrary URL. The extracted features can be fed into a machine-learning system such as Weka to enable intelligent classification of URLs.

The package includes a script for analyzing URLs in bulk (e.g. for creating training sets), as well as a script that uses Weka to classify individual URLs as malicious or benign based on a decision-tree model developed from a training set of ~44,000 URLs.

BURP requires Python 2.6+ / 3.1+.

Installation
------------

1. Install [Weka](http://www.cs.waikato.ac.nz/ml/weka/) 3.7.7+

2. Follow [these instructions](http://weka.wikispaces.com/CLASSPATH) to add the weka.jar file to your CLASSPATH

3. Install [lxml](http://lxml.de/installation.html#installation)

4. Install the [BURP fork of python-whois](https://github.com/eecs-354-burp/python-whois):

        git clone https://github.com/eecs-354-burp/python-whois
        cd python-whois
        python setup.py install

5. Install BURP:

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

The `analyze()` method returns a dictionary with the following keys:

* **<code>numCharacters</code>**<br>
(Int) The number of characters in the HTML document

* **<code>percentWhitespace</code>**<br>
(Float) The percentage of whitespace characters in the HTML document

* **<code>percentScriptContent</code>**<br>
(Float) The precentage of inline script content in the HTML document

* **<code>numIframes</code>**<br>
(Int) The number of `<iframe>` elements

* **<code>numScripts</code>**<br>
(Int) The number of `<script>` elements

* **<code>numScriptsWithWrongExtension</code>**<br>
(Int) The number of `<script>` elements with the wrong extension (i.e. not .js)

* **<code>numEmbeds</code>**<br>
(Int) The number of `<embed>` elements

* **<code>numObjects</code>**<br>
(Int) The number of `<object>` elements

* **<code>numSuspiciousObjects</code>**<br>
(Int) The number of `<object>` elements whose classid is contained in a list of ActiveX controls known to be exploitable

* **<code>numHyperlinks</code>**<br>
(Int) The number of `<a>` elements

* **<code>numMetaRefresh</code>**<br>
(Int) The number of `<meta>` elements with an `http-equiv="refresh"` attribute

* **<code>numHiddenElements</code>**<br>
(Int) The number of elements with a style attribute that sets their CSS display property to "none" or their visibility property to "hidden"

* **<code>numSmallElements</code>**<br>
(Int) The number of elements with width, height, or style attributes that set their width or height to < 2 px or their total area to < 30 sq. px

* **<code>hasDoubleDocuments</code>**<br>
(Bool) True if the HTML document has more than one `<html>`, `<head>`, `<title>`, or `<body>`

* **<code>numUnsafeIncludedUrls</code>**<br>
(Int) The total number of URLs included by elements that can be used to include executable code (`<script>`, `<iframe>`, `<frame>`, `<embed>`, `<form>`, `<object>`)

* **<code>numExternalUrls</code>**<br>
(Int) The total number of included URLs that point to an external domain

* **<code>percentUnknownElements</code>**<br>
(Float) The percentage of elements that are not recognized by the HTML specification


### URL Analyzer

The BURP URL analyzer is optimized for URLs themselves, the IP addresses associated with the URLs, and the WHOIS information related to URLs:
        from burp.html import URLAnalyzer
        analyzer = URLAnalyzer()
        analysis1 = analyzer.analyze(url1)
        analysis2 = analyzer.analyze(url2)

The `analyze()` method returns a dictionary with the following keys:

* **<code>tokens</code>**<br>
(Dictionary) The tokens contained in the URL. This dictionary contains the following keys:
        'subdomain_length': (int)
        'domain': (string)
        'number_subdomains': (int)
        'domain_length': (int)
        'path': (string)
        'subdomain': (string)
        'port': (string)
* **<code>ip</code>**<br>
(String) IP address associated with the URL.
* **<code>tokens</code>**<br>
(Dictionary) The whois information in the URL. This dictionary contains the following keys:
        ‘last_updated’ : (Datetime Object)
        ‘name’ : (string)
        ‘expiration_date’ : (Datetime Object)
        ‘creation_date’ : (Datetime Object)
        ‘registrar’ : (string)
        ‘name_servers’ : (Set of Strings)

Running the HTML Test Suite
---------------------------

    python setup.py test

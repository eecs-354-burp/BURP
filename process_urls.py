import sqlite3
import sys
import urllib2
import threading
import Queue
import codecs
import requests
import burp.html
import burp.url 


logFile = codecs.open('error_log_fetcher.txt', 'a', 'utf-8')

class UrlInfo(dict):
    """UrlInfo is a dictionary with a restricted key set, defaults keys to None"""

    _valid_keys = set(['url', 'isBad', 'numCharacters','percentWhitespace', 'percentScriptContent', 
                       'numIframes', 'numScripts', 'numScriptsWithWrongExtension', 'numEmbeds', 
                       'numObjects', 'numHyperlinks','numMetaRefresh', 'numHiddenElements', 
                       'numSmallElements', 'hasDoubleDocuments', 'numUnsafeIncludedUrls', 
                       'numExternalUrls', 'percentUnknownElements', 'subdomain', 'domain', 
                       'port', 'path', 'creation_date', 'last_updated', 'registrar', 'expiration_date',
                       'numSuspiciousObjects', 'ip_address', 'content_type', 'expires', 'cache_control',
                       'server','transfer_encoding'])
    def __init__(self, url, isBad):
        for key in UrlInfo._valid_keys:
            self[key] = None
        self['url'] = url
        self['isBad'] = isBad

    def __setitem__(self, key, value):
        if key not in UrlInfo._valid_keys:
            raise KeyError('Invaid key')
        dict.__setitem__(self, key, value)

    def is_valid_key(self, key):
        return key in UrlInfo._valid_keys
        
    def valid_keys(self):
        return UrlInfo._valid_keys.copy()

class BurpUrl(object):
    """Holder for url and flag telling if malicious"""
    def __init__(self, url, isBad=False):
        self.url = url
        self.isBad = isBad

class InfoFetch(threading.Thread):
    """Fetches features for a url, reads from url_queue, outputs info to out_queue"""
    def __init__(self, url_queue, out_queue, my_num=0):
        threading.Thread.__init__(self)
        self.url_queue = url_queue
        self.out_queue = out_queue
        self.my_num = my_num # debugging 

    def run(self):
        while True:
            burp_url = self.url_queue.get()
            try: #paranoia
                url, isBad = (burp_url.url, burp_url.isBad)

                info = UrlInfo(url, isBad)
                # okay want to isolate errors as much as possible

                try:
                    r = requests.get(url)
                except Exception as e:
                    print('request, %s, %s\n' % (url, e))

                try: # html analysis
                    html = r.text
                    html_analyzer = HTMLAnalyzer()
                    html_analyzer.setUrl(url)
                    html_analyzer.loadHtml(html)
                    html_data = html_analyzer.analyze()
                    for key, value in html_data.iteritems():
                        info[key] = value
                except Exception as e:
                    logFile.write('html analysis, %s, %s\n' %(url, e))
                    
                domain = ""
                url_info = {};
                url_analyzer = URLAnalyzer()
                
                try: # url analyzer
                    url_info = url_analyzer.analyze(url)
                    info.update(url_info["tokens"])
                    domain = info['domain']
                    
                except Exception as e:
                    logFile.write('url analyzer, %s, %s\n' % (url, str(e)))

                
                if domain == "":
                    domain = url #hack
                try: # whois and headers
                    analysis['cache_control'] = r.headers['Cache-Control']
                    analysis['expires'] = r.headers['Expires']
                    analysis['content_type'] = r.headers['Content-Type']
                    analysis['server'] = r.headers['Server']
                    analysis['transfer_encoding'] = r.headers['Transfer-Encoding']
                 
                    info['ip_address'] = url_info["whois"]

                    domain = str(domain) # domain can't be unicode
                    whois = url_info["whois"]
                    if whois is not None:
                        for key, value in whois.iteritems():
                            if info.is_valid_key(key):
                                info[key] = str(value)
                    
                except Exception as e:
                    logFile.write('whois, %s, %s\n' % (url, str(e)))

                self.out_queue.put(info)
            except Exception as e:
                logFile.write("%s %s\n" % (url, str(e)))
            
            self.url_queue.task_done()


class UrlDatabaseLogger(threading.Thread):
    """Logs UrlInfo objects into the database"""

    # kinda gross
    insertStatement = """insert into url_info (
                           url,
                           isBad,
                           html_numCharacters,
                           html_percentWhitespace,
                           html_percentScriptContent,
                           html_numIframes,
                           html_numScripts,
                           html_numScriptsWithWrongExtension,
                           html_numEmbeds, 
                           html_numObjects,
                           html_numSuspiciousObjects,
                           html_numHyperlinks, 
                           html_numMetaRefresh,
                           html_numHiddenElements, 
                           html_numSmallElements,
                           html_hasDoubleDocuments,
                           html_numUnsafeIncludedUrls,
                           html_numExternalUrls,
                           html_percentUnknownElements,
                           ip_address,
                           headers_content_type,
                           headers_expires,
                           headers_cache_control,
                           headers_server,
                           headers_transfer_encoding,
                           token_subdomain,
                           token_domain,
                           token_port,
                           token_path,
                           whois_creation_date,
                           whois_last_updated,
                           whois_registrar,
                           whois_expiration_date ) values (
                           :url, 
                           :isBad, 
                           :numCharacters,
                           :percentWhitespace,
                           :percentScriptContent,
                           :numIframes,
                           :numScripts,
                           :numScriptsWithWrongExtension,
                           :numEmbeds, 
                           :numObjects,
                           :numSuspiciousObjects,
                           :numHyperlinks, 
                           :numMetaRefresh,
                           :numHiddenElements, 
                           :numSmallElements,
                           :hasDoubleDocuments,
                           :numUnsafeIncludedUrls,
                           :numExternalUrls,
                           :percentUnknownElements,
                           :ip_address,
                           :content_type,
                           :expires,
                           :cache_control,
                           :server,
                           :transfer_encoding,
                           :subdomain,
                           :domain,
                           :port,
                           :path,
                           :creation_date,
                           :last_updated,
                           :registrar,
                           :expiration_date )
    """
    def __init__(self, dbFileName, urls_queue):
        threading.Thread.__init__(self)
        self.db_file = dbFileName
        self.urls = urls_queue

    def init_db(self):
        createSql = '''create table if not exists url_info (
                           url text primary key,
                           isBad boolean,
                           html_numCharacters int,
                           html_percentWhitespace int,
                           html_percentScriptContent int,
                           html_numIframes int,
                           html_numScripts int,
                           html_numScriptsWithWrongExtension int,
                           html_numEmbeds int, 
                           html_numObjects int,
                           html_numSuspiciousObjects int,
                           html_numHyperlinks int, 
                           html_numMetaRefresh int,
                           html_numHiddenElements int, 
                           html_numSmallElements int,
                           html_hasDoubleDocuments boolean,
                           html_numUnsafeIncludedUrls int,
                           html_numExternalUrls int,
                           html_percentUnknownElements int,
                           ip_address text,
                           headers_content_type text,
                           headers_expires text,
                           headers_cache_control text,
                           headers_server text,
                           headers_transfer_encoding text,
                           token_subdomain text,
                           token_domain text,
                           token_port int,
                           token_path text,
                           whois_creation_date text,
                           whois_last_updated text,
                           whois_registrar text,
                           whois_expiration_date text 
                       )
        '''
        self.curs.execute(createSql)

    def open_db(self):
        self.db_conn = sqlite3.connect(self.db_file)
        self.curs = self.db_conn.cursor()
        self.init_db()

    def run(self):
        self.open_db()
        while True:
            url_info = self.urls.get()
            try:
                self.curs.execute(UrlDatabaseLogger.insertStatement, url_info)
                self.curs.execute('COMMIT') # force db to accept changes
            except Exception as e:
                logFile.write("error on insert %s\n" % str(e))
            self.urls.task_done()

    def close(self):
        self.db_conn.close()


def selectBenignUrls(curs, limit=None):
    if limit is None:
        sql = 'select url from urls where isBad=0 order by Random()'
    else:
        sql = 'select url from urls where isBad=0 order by Random() limit %d' % limit
    curs.execute(sql)
    return curs.fetchall()

def getUrlsFromFile(fileName, count=None):
    retList = []
    with codecs.open(fileName, 'r', 'utf-8') as f:
        for c, line in enumerate(f):
            if count is not None and c >= count:
                break
            retList.append(line.strip())
    return retList


def makeUrl(maybeDomain):
    if not (maybeDomain.startswith('http://') or maybeDomain.startswith('https://')):
        return "http://%s" % maybeDomain
    return maybeDomain

def getBenignUrls(dbFile, limit=None):
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()
    urls = selectBenignUrls(cursor, limit)
    conn.close()
    
    return [makeUrl(u[0]) for u in urls]

def getUrlsAlreadyProcessed(dbFile):
    conn = sqlite3.connect(dbFile)
    curs = conn.cursor()
    urls = curs.execute('select url from url_info').fetchall()
    conn.close()
    ret = set()
    for u in urls:
        ret.add(u[0])
    return ret

def getUrlsToProcess(the_good, the_bad, count=None):
    """returns a list BurpUrl objects from file names"""
    malus = getUrlsFromFile(the_bad, count)
    bene = getUrlsFromFile(the_good, count)

    retList = []
    for good, bad in zip(bene, malus):
        retList.append(BurpUrl(good, False))
        retList.append(BurpUrl(bad, True))
    return retList


def fetchUrls(urls, outputDatabaseFile, threadCount=5, numUrls=None):
    """Starts InfoFetch threads and builds a queue from urls for them to read.
    urls is a list of BurpUrl objects
    outputDatabaseFile is the file where the sqlite database will be filled in, initialize db with UrlDatabaseLogger.init_db call if necessary"""
    if numUrls is None:
        numUrls = len(urls)

    url_queue = Queue.Queue()
    output_queue = Queue.Queue()

    
    for i in range(threadCount):
        fetcher = InfoFetch(url_queue, output_queue, i)
        fetcher.setDaemon(True)
        fetcher.start()

    logger = UrlDatabaseLogger(outputDatabaseFile, output_queue)
    logger.setDaemon(True)
    logger.start()

    # add numUrls urls to the queue
    for count, url in enumerate(urls):
        if count < numUrls:
            url_queue.put(url)
        else:
            break

    url_queue.join()
    output_queue.join()

malicious_url_file = 'valid_urls'
benign_url_db = 'urls.db'
benign_url_file = 'benign_urls'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        _, dbFile, numThreads = sys.argv
        
        urls = getUrlsToProcess(benign_url_file, malicious_url_file)

        fetchUrls(urls, dbFile, int(numThreads))
    else:
        print "usage: python process_urls.py dbFile numThreads"

        




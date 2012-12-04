import sqlite3
import sys
import urllib2
import threading
import Queue
import codecs
import htmlanalyzer # ethan's file in BURP-HTML
import urlTokenizer # peter's file in BURP-URL
import burp_url 

logFile = codecs.open('error_log_fetcher.txt', 'a', 'utf-8')

class UrlInfo(dict):
    """
    UrlInfo is a dictionary with a restricted key set
    """
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


class InfoFetch(threading.Thread):
    def __init__(self, url_queue, out_queue, my_num=0):
        threading.Thread.__init__(self)
        super(threading.Thread, self).__init__()
        self.url_queue = url_queue
        self.out_queue = out_queue
        self.my_num = my_num # debugging 

    def run(self):
        while True:
            url_pair = self.url_queue.get()
            try: #paranoia
                url, isBad = url_pair
                url = url.strip(',') # saw in log file a lot
                info = UrlInfo(url, isBad)
                # okay want to isolate errors as much as possible

                try: # html analysis
                    html = htmlanalyzer.HTMLAnalyzer(url)
                    html_data = html.analyze()
                    for key, value in html_data.iteritems():
                        info[key] = value
                except Exception as e:
                    logFile.write('html analysis, %s, %s\n' %(url, e))
                    
                domain = ""
                try: # tokenizer
                    tokens = urlTokenizer.get_tokens(url)
                    info['subdomain'] = tokens[0]
                    info['domain'] = tokens[1]
                    domain = tokens[1]
                    info['port'] = tokens[2]
                    info['path'] = tokens[3]
                except Exception as e:
                    logFile.write('tokenizer, %s, %s\n' % (url, str(e)))

                
                if domain == "":
                    domain = url #hack
                try: # whois and headers
                    headers = burp_url.getheadersonly(url).dict
                    if "cache-control" in headers:
                        info['cache_control'] = headers['cache-control']
                    if "expires" in headers:
                        info['expires'] = headers['expires']
                    if "content-type" in headers:
                        info['content_type'] = headers['content-type']
                    if "server" in headers:
                        info['server'] = headers['server']
                    if "transfer-encoding" in headers:
                        info['transfer_encoding'] = headers['transfer-encoding']
                 
                    info['ip_address'] = burp_url.getIpAddr(domain)

                    domain = str(domain)
                    whois = burp_url.getWhoIs(domain)
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
    """
    returns a list of tuples (url, isBad) identifying which are malicious and benign
    """
    malus = getUrlsFromFile(the_bad, count)
    bene = getUrlsFromFile(the_good, count)

    retList = []
    for good, bad in zip(bene, malus):
        retList.append((good, False))
        retList.append((bad, True))
    return retList


def fetchUrls(urls, outputDatabaseFile, threadCount=5, numUrls=None):
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
        #usedUrls = getUrlsAlreadyProcessed('url_info.db')
        #proc_urls = []
        #for u in urls:
            #if u[0] not in proc_urls:
                #proc_urls.append(u)

        fetchUrls(urls, dbFile, int(numThreads))
    else:
        print "usage: python process_urls.py dbFile numThreads"

        




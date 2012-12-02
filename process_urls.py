import sqlite3
import sys
import urllib2
import threading
import Queue
import codecs
import htmlanalyzer # ethan's file in BURP-HTML


logFile = codecs.open('error_log_fetcher.txt', 'a', 'utf-8')

class UrlInfo(dict):
    """
    UrlInfo is a dictionary with a restricted key set
    """
    _valid_keys = set(['url', 'isBad', 'numchars','percentWhitespace', 'percentScriptChars', 'numIframes', 
                  'numScripts', 'numScriptsWithWrongExtension', 'numEmbeds', 'numObjects', 
                  'numHyperlinks','numMetaRefresh', 'numHiddenElements', 'numSmallElements',
                  'hasDoubleDocuments', 'numUnsafeIncludedUrls', 'numExternalUrls', 
                  'percentUnknownElements', 'subdomain', 'domain', 'port', 'path',
                  'creation_date', 'last_updated', 'registrar', 'expiration_date'])
    def __init__(self, url, isBad):
        for key in UrlInfo._valid_keys:
            self[key] = None
        self['url'] = url
        self['isBad'] = isBad

    def __setitem__(self, key, value):
        if key not in UrlInfo._valid_keys:
            raise KeyError('Invaid key')
        dict.__setitem__(self, key, value)
        
    def valid_keys(self):
        return UrlInfo._valid_keys.copy()


class InfoFetch(threading.Thread):
    def __init__(self, url_queue, out_queue, my_num=0):
        super(threading.Thread, self).__init__()
        self.url_queue = url_queue
        self.out_queue = out_queue
        self.my_num = my_num # debugging 

    def run(self):
        while True:
            url_pair = self.url_queue.get()
            try: #paranoia
                url, isBad = url_pair
                info = UrlInfo(url, isBad)

                # okay want to isolate errors as much as possible
                try: # html analysis
                    html = HTMLAnalyzer(url)
                    html_data = html.analyze()
                    for key, value in html_data:
                        info[key] = value
                except Exception as e:
                    logFile.write('html analysis, %s, %s\n' %(url, str(e)))
                    
                try: # tokenizer
                    pass
                except Exception as e:
                    logFile.write('tokenizer, %s, %s\n', %(url, str(e)))

                try: # whois
                    pass
                except Exception as e:
                    logFile.write('whois, %s, %s\n', % (url, str(e)))

                self.out_queue.put(info)
            except Exception as e:
                logFile.write("%s %s\n" % (url, str(e)))
            
            self.url_queue.task_done()


class UrlDatabaseLogger(threading.Thread):
    # kinda gross
    insertStatement = """insert into url_info (
                           url,
                           isBad,
                           html_numchars,
                           html_percentWhitespace,
                           html_percentScriptChars,
                           html_numIframes,
                           html_numScripts,
                           html_numScriptsWithWrongExtension,
                           html_numEmbeds, 
                           html_numObjects,
                           html_numHyperlinks, 
                           html_numMetaRefresh,
                           html_numHiddenElements, 
                           html_numSmallElements,
                           html_hasDoubleDocuments,
                           html_numUnsafeIncludedUrls,
                           html_numExternalUrls,
                           html_percentUnknownElements,
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
                           :numchars,
                           :percentWhitespace,
                           :percentScriptChars,
                           :numIframes,
                           :numScripts,
                           :numScriptsWithWrongExtension,
                           :numEmbeds, 
                           :numObjects,
                           :numHyperlinks, 
                           :numMetaRefresh,
                           :numHiddenElements, 
                           :numSmallElements,
                           :hasDoubleDocuments,
                           :numUnsafeIncludedUrls,
                           :numExternalUrls,
                           :percentUnknownElements,
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
        super(threading.Thread, self).__init__() # i can never remember how to do this....
        #threading.Thread.__init__(self)
        self.db_conn = sqlite3.connect(dbFileName)
        self.curs = self.db_conn.cursor()
        self.urls = urls_queue

    def initDatabase(self):
        createSql = '''create table url_info (
                           url text primary key,
                           isBad boolean,
                           html_numchars int,
                           html_percentWhitespace int,
                           html_percentScriptChars int,
                           html_numIframes int,
                           html_numScripts int,
                           html_numScriptsWithWrongExtension int,
                           html_numEmbeds int, 
                           html_numObjects int,
                           html_numHyperlinks int, 
                           html_numMetaRefresh int,
                           html_numHiddenElements int, 
                           html_numSmallElements int,
                           html_hasDoubleDocuments boolean,
                           html_numUnsafeIncludedUrls int,
                           html_numExternalUrls int,
                           html_percentUnknownElements int,
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


    def run(self):
        while True:
            url_info = self.urls.get()
            try:
                self.curs.execute(UrlDatabaseLogger.insertStatement, url_info)
            except Exception as e:
                logFile.write("error on insert %s\n" % str(e))
            self.urls.task_done()

    def close(self):
        self.file.close()


def selectBenignUrls(curs, limit=None):
    if limit is None:
        sql = 'select url from urls where isBad=0 orery by Random()'
    else:
        sql = 'select url from urls where isBad=0 orery by Random() limit %d' % limit
    curs.execute(sql)
    return curs.fetchall()

def getValidMaliciousUrls(fileName):
    retList = []
    with codecs.open(fileName, 'r', 'utf-8') as f:
        for line in f:
            retList.append(line.strip())
    return retList


def makeUrl(maybeDomain):
    if not (maybeDomain.startswith('http://') or maybeDomain.startswith('https://')):
        return "http://%s" % maybeDomain
    return maybeDomain

# remove any previously fetched
def getBenignUrls(dbFile, limit=None):
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()
    urls = selectBenignUrls(cursor, limit)
    conn.close()
    return [makeUrl(u[0]) for u in urls]



def getUrlsToProcess(the_good, the_bad, count=None):
    """
    returns a list of tuples (url, isBad) identifying which are malicious and benign
    """
    malus = getValidMaliciousUrls(the_bad)
    c = len(malus) if count is None else count
    bene = getBenignUrls(the_good, c)

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

    logger = UrlDatabaseLogger(outputDatabaseFile, output_queue)
    logger.initDatabase()
    logger.setDaemon(True)
    logger.start()

    for i in range(threadCount):
        fetcher = InfoFetcher(url_queue, output_queue, i)
        fetcher.setDaemon(True)
        fetcher.start()

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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        _, dbFile, numThreads = sys.argv
        
        urls = getUrlsToProcess(benign_url_db, malicious_url_file)
        fetchUrls(urls, dbFile, int(numThreads))
    else:
        print "usage: python validate_urls.py dbFile numThreads"

        




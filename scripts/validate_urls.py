import sqlite3
import sys
import urllib2
import threading
import Queue
import codecs

logFile = codecs.open('error_log_validator.txt', 'a', 'utf-8')

class UrlValidator(threading.Thread):
    """Checks to make sure website at url is still up"""
    def __init__(self, url_queue, out_queue, my_num=0):
        threading.Thread.__init__(self)
        self.url_queue = url_queue
        self.out_queue = out_queue
        self.my_num = my_num # debugging 

    def run(self):
        while True:
            url = self.url_queue.get()
            try:
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = "http://%s" % url
                    
                try:
                    res = urllib2.urlopen(url, None, 5) # set timeout to 5 seconds
                    if res and res.code < 400:
                        self.out_queue.put(url)
                except urllib2.HTTPError as e: # 4xx or 5xx
                    logFile.write("%s %d\n" % (url, e.code))
                except urllib2.URLError as e:
                    logFile.write("%s %s\n" % (url, str(e)))
            except Exception as e:
                logFile.write("%s %s\n" % (url, str(e)))
            
            self.url_queue.task_done()


class UrlLogger(threading.Thread):
    """Logs urls into a file, one per line"""
    def __init__(self, fileName, urls):
        threading.Thread.__init__(self)
        self.file = codecs.open(fileName, 'a', 'utf-8')
        self.urls = urls

    def run(self):
        while True:
            url = self.urls.get()
            try:
                self.file.write("%s\n" % url)
            except Exception as e:
                logFile.write("error on write %s\n" % e)
            self.urls.task_done()

    def close(self):
        self.file.close()


def selectMaliciousUrls(curs, limit=None):
    if limit is None:
        sql = ''' select url from urls where isBad=1 '''
    else:
        sql = ''' select url from urls where isBad=1 limit %d''' % limit
    curs.execute(sql)
    return curs.fetchall()

def getCurrentUrls(validUrlsFile, errorsUrlFile):
    retSet = set()

    with codecs.open(validUrlsFile, 'r', 'utf-8') as f:
        for line in f:
            retSet.add(line.strip())

    with codecs.open(errorsUrlFile, 'r', 'utf-8') as f:
        for line in f:
            parts = line.strip().split(' ')
            if parts[0].startswith('http://') or parts[0].startswith('https://'):
                retSet.add(parts[0])

    
    return retSet

def makeUrl(maybeDomain):
    if not (maybeDomain.startswith('http://') or maybeDomain.startswith('https://')):
        return "http://%s" % maybeDomain
    return maybeDomain

# remove any previously fetched
def getMaliciousUrls(dbFile, prevUrls,limit=None):
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()
    urls = selectMaliciousUrls(cursor, limit=limit)
    conn.close()
    return [u for u in urls if makeUrl(u[0]) not in prevUrls]

def fetchUrls(urlList, validatedFileName, threadCount=5):
    url_queue = Queue.Queue()
    output_queue = Queue.Queue()
    for i in range(threadCount):
        validator = UrlValidator(url_queue, output_queue, i)
        validator.setDaemon(True)
        validator.start()

    logger = UrlLogger(validatedFileName, output_queue)
    logger.setDaemon(True)
    logger.start()

    for url in urlList:
        url_queue.put(url[0])

    url_queue.join()
    output_queue.join()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        _, dbFile, outFile = sys.argv

        prevUrls = getCurrentUrls(outFile, 'error_log_validator.txt')
        urls = getMaliciousUrls(dbFile, prevUrls)
        fetchUrls(urls, outFile, 10)
    else:
        print "usage: python validate_urls.py dbFile outfile"

        




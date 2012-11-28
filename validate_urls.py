import sqlite3
import sys
import urllib2
import threading
import Queue
import codecs
from sets import Set

class UrlValidator(threading.Thread):
    def __init__(self, url_queue, out_queue):
        threading.Thread.__init__(self)
        self.url_queue = url_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            url = self.url_queue.get()
            try:
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = "http://%s" % url
                    
                try:
                    res = urllib2.urlopen(url)
                    if res and res.code < 400:
                        self.out_queue.put(url)
                except urllib2.HTTPError as e: # 4xx or 5xx
                    print "%s %d" % (url, e.code)
                except urllib2.URLError as e:
                    print url," ", e
            except Exception as e:
                print url, " ", e
            self.url_queue.task_done()


class UrlLogger(threading.Thread):
    def __init__(self, fileName, urls):
        threading.Thread.__init__(self)
        self.file = codecs.open(fileName, 'w', 'utf-8')
        self.urls = urls

    def run(self):
        while True:
            url = self.urls.get()
            try:
                self.file.write("%s\n" % url)
            except Exception as e:
                print "error on write ", e
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

def getCurrentUrls(fileName):
    with codecs.open(fileName, 'r', 'utf-8') as f:
        retSet = Set()
        for line in f:
            retSet.add(line.strip())
        return retSet

def makeUrl(maybeDomain):
    if not (maybeDomain.startswith('http://') or maybeDomain.startswith('https://')):
        return "http://%s" % maybeDomain
    return maybeDomain


def getMaliciousUrls(dbFile, validatedUrls, limit=None):
    #urlSet = getCurrentUrls(validatedUrls)
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()
    urls = selectMaliciousUrls(cursor, limit=limit)
    conn.close()
    return urls

def fetchUrls(urlList, validatedFileName, threadCount=5):
    url_queue = Queue.Queue()
    output_queue = Queue.Queue()
    for i in range(threadCount):
        validator = UrlValidator(url_queue, output_queue)
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
        sys.stdout = open('error_log_validator.txt', 'w')
        urls = getMaliciousUrls(dbFile)
        fetchUrls(urls, outFile, 8)

        




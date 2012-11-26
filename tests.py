##
# Tests for HTML Analysis Library
##

import htmlanalyzer
from htmlanalyzer import *
import unittest

# Stub the urllib.urlopen method to open local files
htmlanalyzer.urllib.urlopen = lambda filepath: open('test.html', 'r')

class TestHTMLAnalysis(unittest.TestCase):

  def setUp(self):
    self.result = HTMLAnalyzer('http://www.google.com').analyze()

  def test_countElements(self):
    self.assertEqual(self.result['numIframes'], 2)
    self.assertEqual(self.result['numScripts'], 6)
    self.assertEqual(self.result['numScriptsWithWrongExtension'], 4)
    self.assertEqual(self.result['numEmbeds'], 2)
    self.assertEqual(self.result['numObjects'], 2)
    self.assertEqual(self.result['numHyperlinks'], 1)
    self.assertEqual(self.result['numMetaRefresh'], 1)
    self.assertEqual(self.result['numHiddenElements'], 2)
    self.assertEqual(self.result['numSmallElements'], 2)
    self.assertEqual(self.result['hasDoubleDocuments'], True)
    self.assertEqual(self.result['numUnsafeIncludedUrls'], 10)
    self.assertEqual(self.result['numExternalUrls'], 5)

if __name__ == '__main__':
  unittest.main()

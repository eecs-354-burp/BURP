##
# Tests for HTML Analysis Library
##

import htmlanalyzer
from htmlanalyzer import *
import unittest

# Stub the urllib.openurl method to open local files
htmlanalyzer.urllib.openurl = lambda filepath: open(filepath, 'r')

class TestHTMLAnalysis(unittest.TestCase):

  def setUp(self):
    self.result = HTMLAnalyzer('test.html').analyze()

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

if __name__ == '__main__':
  unittest.main()

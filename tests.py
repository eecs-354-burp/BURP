##
# Tests for HTML Analysis Library
##

from htmlanalyzer import *
import unittest

class TestHTMLAnalysis(unittest.TestCase):

  def setUp(self):
    analyzer = HTMLAnalyzer()
    f = open('test.html', 'r')
    html = f.read()
    analyzer.load(html)
    analyzer.setUrl('http://www.google.com')
    self.result = analyzer.analyze()

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

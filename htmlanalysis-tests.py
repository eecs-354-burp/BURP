##
# Tests for HTML Analysis Library
##

from htmlanalysis import *
import unittest

class TestHTMLAnalysis(unittest.TestCase):

  def setUp(self):
    f = open('test.html', 'r')
    html = f.read()
    self.result = analyzeHtml(html)

  def test_countElements(self):
    self.assertEqual(self.result['numIframes'], 2)
    self.assertEqual(self.result['numScripts'], 6)
    self.assertEqual(self.result['numEmbeds'], 1)
    self.assertEqual(self.result['numObjects'], 1)
    self.assertEqual(self.result['numHyperlinks'], 1)
    self.assertEqual(self.result['numMetaRefresh'], 1)

if __name__ == '__main__':
  unittest.main()


##
# Tests for HTML Analysis Library
##

from htmlanalysis import *
import unittest

class TestHTMLAnalysis(unittest.TestCase):

  def setUp(self):
    self.doc = pq(filename="test.html")

  def test_countElements(self):
    self.assertEqual(countElements(self.doc, "div"), 1)
    self.assertEqual(countElements(self.doc, "iframe"), 2)

if __name__ == '__main__':
  unittest.main()


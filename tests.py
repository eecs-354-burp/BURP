##
# Tests for HTML Analysis Library
##

from htmlanalyzer import *
import unittest

class HTMLAnalyzerTestCase(unittest.TestCase):

  def setUp(self):
    self.analyzer = HTMLAnalyzer()
    self.analyzer.setUrl('http://www.example.com')

  def loadFile(self, filename):
    f = open(filename, 'r')
    self.html = f.read()
    self.analyzer.load(self.html)

class TestExternalAPI(HTMLAnalyzerTestCase):

  def runTest(self):
    self.analyzer.load('<html></html>')
    result = self.analyzer.analyze()
    self.assertIn('numCharacters', result)
    self.assertIn('percentWhitespace', result)
    self.assertIn('percentScriptContent', result)
    self.assertIn('numIframes', result)
    self.assertIn('numScripts', result)
    self.assertIn('numScriptsWithWrongExtension', result)
    self.assertIn('numEmbeds', result)
    self.assertIn('numObjects', result)
    self.assertIn('numHyperlinks', result)
    self.assertIn('numMetaRefresh', result)
    self.assertIn('numHiddenElements', result)
    self.assertIn('numSmallElements', result)
    self.assertIn('hasDoubleDocuments', result)
    self.assertIn('numUnsafeIncludedUrls', result)
    self.assertIn('numExternalUrls', result)
    self.assertIn('percentUnknownElements', result)

class TestElementCounting(HTMLAnalyzerTestCase):

  def setUp(self):
    HTMLAnalyzerTestCase.setUp(self)
    self.analyzer.load('<html><body><div></div><div></div></body></html>')

  def test_CountRootElement(self):
    result = self.analyzer.countElems('html')
    self.assertEqual(result, 1)

  def test_NestedElement(self):
    result = self.analyzer.countElems('body')
    self.assertEqual(result, 1)

  def test_MultipleElements(self):
    result = self.analyzer.countElems('div')
    self.assertEqual(result, 2)

  def test_FilteredElements(self):
    f = lambda this: this.tag == 'div'
    result = self.analyzer.countElems('*', f)
    self.assertEqual(result, 2)

class TestCountWhitespaceChars(HTMLAnalyzerTestCase):

  def test_NoWhitespace(self):
    self.analyzer.load('<html></html>')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 0)

  def test_LeadingSpaces(self):
    self.analyzer.load('   <html></html>')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 3)

  def test_TrailingSpaces(self):
    self.analyzer.load('<html></html>    ')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 4)

  def test_InnerSpaces(self):
    self.analyzer.load('<html>  <div> </div>  </html>')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 5)

class TestCountScriptChars(HTMLAnalyzerTestCase):

  def test_NoScripts(self):
    self.analyzer.load('<html></html>')
    result = self.analyzer.countScriptChars()
    self.assertEqual(result, 0)

  def test_EmptyScript(self):
    self.analyzer.load('<html><script></script></html>')
    result = self.analyzer.countScriptChars()
    self.assertEqual(result, 0)

  def test_InlineScript(self):
    self.analyzer.load('<html><script>alert("abc")</script></html>')
    result = self.analyzer.countScriptChars()
    self.assertEqual(result, 12)

class TestHasWrongExtension(HTMLAnalyzerTestCase):

  def test_InlineScript(self):
    elem = PyQuery('<script>alert("abc")</script>')
    result = self.analyzer.hasWrongExtension(elem)
    self.assertFalse(result)

  def test_CorrectExtension(self):
    elem = PyQuery('<script src="src.js"></script>')
    result = self.analyzer.hasWrongExtension(elem)
    self.assertFalse(result)

  def test_WrongExtension(self):
    elem = PyQuery('<script src="src.exe"></script>')
    result = self.analyzer.hasWrongExtension(elem)
    self.assertTrue(result)

class TestIsRefresh(HTMLAnalyzerTestCase):

  def test_MetaNoRefresh(self):
    elem = PyQuery('<meta></meta>')
    result = self.analyzer.isRefresh(elem)
    self.assertFalse(result)

  def test_MetaWithHttpEquivAttribute(self):
    elem = PyQuery('<meta http-equiv="content-type"></meta>')
    result = self.analyzer.isRefresh(elem)
    self.assertFalse(result)

  def test_MetaWithRefresh(self):
    elem = PyQuery('<meta http-equiv="refresh"></meta>')
    result = self.analyzer.isRefresh(elem)
    self.assertTrue(result)

class TestIsHidden(HTMLAnalyzerTestCase):

  def test_NoStyle(self):
    elem = PyQuery('<div></div>')
    result = self.analyzer.isHidden(elem)
    self.assertFalse(result)

  def test_NoHiddenStyles(self):
    elem = PyQuery('<div style="color: red;"></div>')
    result = self.analyzer.isHidden(elem)
    self.assertFalse(result)

  def test_DisplayNone(self):
    elem = PyQuery('<div style="display: none;"></div>')
    result = self.analyzer.isHidden(elem)
    self.assertTrue(result)

  def test_ExtraSpaces(self):
    elem = PyQuery('<div style="  display  :  none  "></div>')
    result = self.analyzer.isHidden(elem)
    self.assertTrue(result)

  def test_VisibilityHidden(self):
    elem = PyQuery('<div style="visibility: hidden;"></div>')
    result = self.analyzer.isHidden(elem)
    self.assertTrue(result)

class TestGetDimension(HTMLAnalyzerTestCase):

  def test_widthAttr(self):
    elem = PyQuery('<iframe width="10"></iframe>')
    result = self.analyzer.getDimension(elem, 'width')
    self.assertEqual(result, 10)

  def test_heightAttr(self):
    elem = PyQuery('<iframe height="20"></iframe>')
    result = self.analyzer.getDimension(elem, 'height')
    self.assertEqual(result, 20)

  def test_CssWidth(self):
    elem = PyQuery('<iframe style="width: 30px;"></iframe>')
    result = self.analyzer.getDimension(elem, 'width')
    self.assertEqual(result, 30)

  def test_CssHeight(self):
    elem = PyQuery('<iframe style="height: 40px;"></iframe>')
    result = self.analyzer.getDimension(elem, 'height')
    self.assertEqual(result, 40)

  def test_CssPrecedence(self):
    elem = PyQuery('<iframe width="10" height="20" style="width: 30px; height: 40px;"></iframe>')
    width = self.analyzer.getDimension(elem, 'width')
    height = self.analyzer.getDimension(elem, 'height')
    self.assertEqual(width, 30)
    self.assertEqual(height, 40)

  def test_CssExtraSpaces(self):
    elem = PyQuery('<iframe style="  width  :  50px  "></iframe>')
    result = self.analyzer.getDimension(elem, 'width')
    self.assertEqual(result, 50)

  def test_CssNoPx(self):
    elem = PyQuery('<iframe style="width: 60;"></iframe>')
    result = self.analyzer.getDimension(elem, 'width')
    self.assertEqual(result, 60)

  def test_CssFloat(self):
    elem = PyQuery('<iframe style="width: 70.5;"></iframe>')
    result = self.analyzer.getDimension(elem, 'width')
    self.assertEqual(result, 70.5)

class TestIsSmall(HTMLAnalyzerTestCase):

  def test_NoDimensions(self):
    elem = PyQuery('<iframe></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertFalse(result)

  def test_LargeArea(self):
    elem = PyQuery('<iframe style="width: 20px; height: 20px"></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertFalse(result)

  def test_LargeWidth(self):
    elem = PyQuery('<iframe style="width: 20px"></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertFalse(result)

  def test_LargeHeight(self):
    elem = PyQuery('<iframe style="height: 20px"></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertFalse(result)

  def test_SmallArea(self):
    elem = PyQuery('<iframe style="width: 3px; height: 3px"></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertTrue(result)

  def test_SmallWidth(self):
    elem = PyQuery('<iframe style="width: 1px"></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertTrue(result)

  def test_SmallHeight(self):
    elem = PyQuery('<iframe style="height: 1px"></iframe>')
    result = self.analyzer.isSmall(elem)
    self.assertTrue(result)

class TestHasDoubleDocuments(HTMLAnalyzerTestCase):

  def test_NoDoubleDocuments(self):
    self.analyzer.load('<html><head><title></title></head><body></body></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertFalse(result)

  def test_DoubleHtml(self):
    self.analyzer.load('<html></html><html></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

  def test_DoubleHead(self):
    self.analyzer.load('<html><head></head><head></head></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

  def test_DoubleTitle(self):
    self.analyzer.load('<html><head><title></title><title></title></head></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

  def test_DoubleBody(self):
    self.analyzer.load('<html><body></body><body></body></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

class TestGetAttrValues(HTMLAnalyzerTestCase):

  def test_NoAttributes(self):
    self.analyzer.load('<div></div><div></div>')
    result = self.analyzer.getAttrValues('div', 'id')
    self.assertEqual(len(result), 0)

  def test_MultipleAttributes(self):
    self.analyzer.load('<div id="a"></div><div id="b"></div>')
    result = self.analyzer.getAttrValues('div', 'id')
    self.assertIn('a', result)
    self.assertIn('b', result)

class TestGetUnsafeIncludedUrls(HTMLAnalyzerTestCase):

  def test_ScriptSrc(self):
    self.analyzer.load('<script src="script.js"></script>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertIn('script.js', result)

  def test_IframeSrc(self):
    self.analyzer.load('<iframe src="iframe.html"></iframe>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertIn('iframe.html', result)

  def test_FrameSrc(self):
    self.analyzer.load('<body><frame src="frame.html"></body>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertIn('frame.html', result)

  def test_EmbedSrc(self):
    self.analyzer.load('<embed src="embed.mov"></embed>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertIn('embed.mov', result)

  def test_FormAction(self):
    self.analyzer.load('<form action="submit.php"></form>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertIn('submit.php', result)

  def test_ObjectData(self):
    self.analyzer.load('<object data="object.swf"></object>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertIn('object.swf', result)

class TestGetSafeIncludedUrls(HTMLAnalyzerTestCase):

  def test_ImgSrc(self):
    self.analyzer.load('<img src="image.jpg" />')
    result = self.analyzer.getSafeIncludedUrls()
    self.assertIn('image.jpg', result)

  def test_LinkHref(self):
    self.analyzer.load('<link href="style.css" />')
    result = self.analyzer.getSafeIncludedUrls()
    self.assertIn('style.css', result)

class TestIsExternalUrl(HTMLAnalyzerTestCase):

  def test_NoDomain(self):
    result = self.analyzer.isExternalUrl('/directory/index.html')
    self.assertFalse(result)

  def test_InternalUrl(self):
    result = self.analyzer.isExternalUrl('http://www.example.com')
    self.assertFalse(result)

  def test_InternalUrlWithoutWWW(self):
    result = self.analyzer.isExternalUrl('http://example.com')
    self.assertFalse(result)

  def test_ExternalUrl(self):
    result = self.analyzer.isExternalUrl('http://www.google.com')
    self.assertTrue(result)

class TestIsUnknownElement(HTMLAnalyzerTestCase):

  def test_KnownElement(self):
    elem = PyQuery('<html></html>')
    result = self.analyzer.isUnknownElement(elem)
    self.assertFalse(result)

  def test_UnknownElement(self):
    elem = PyQuery('<invalidElement></invalidElement>')
    result = self.analyzer.isUnknownElement(elem)
    self.assertTrue(result)

class TestGetPercentage(HTMLAnalyzerTestCase):
  
  def test_0_Percent(self):
    result = self.analyzer.getPercentage(0, 8)
    self.assertEqual(result, 0)

  def test_62_5_Percent(self):
    result = self.analyzer.getPercentage(5, 8)
    self.assertEqual(result, 62.5)

  def test_100_Percent(self):
    result = self.analyzer.getPercentage(8, 8)
    self.assertEqual(result, 100)

class TestCountSuspiciousObjects(HTMLAnalyzerTestCase):

  def test_UnsuspiciousObject(self):
    self.analyzer.load('<object classid="AE7AB96B-FF5E-4dce-801E-14DF2C4CD681"></object>')
    result = self.analyzer.countSuspiciousObjects()
    self.assertEqual(result, 0)

  def test_SuspiciousObject(self):
    self.analyzer.load('<object classid="CA8A9780-280D-11CF-A24D-444553540000"></object>')
    result = self.analyzer.countSuspiciousObjects()
    self.assertEqual(result, 1)

if __name__ == '__main__':
  unittest.main()

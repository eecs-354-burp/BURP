##
# Test Suite for HTMLAnalyzer Class
##

import unittest

from burp.html.analyzer import HTMLAnalyzer, PyQuery

class HTMLAnalyzerTestCase(unittest.TestCase):

  def setUp(self):
    self.analyzer = HTMLAnalyzer()
    self.analyzer.setUrl('http://www.example.com')

  def loadFile(self, filename):
    f = open(filename, 'r')
    self.html = f.read()
    self.analyzer.loadHtml(self.html)

class TestExternalAPI(HTMLAnalyzerTestCase):

  def runTest(self):
    self.analyzer.loadHtml('<html></html>')
    result = self.analyzer.analyze()
    self.assertTrue('numCharacters' in result)
    self.assertTrue('percentWhitespace' in result)
    self.assertTrue('percentScriptContent' in result)
    self.assertTrue('numIframes' in result)
    self.assertTrue('numScripts' in result)
    self.assertTrue('numScriptsWithWrongExtension' in result)
    self.assertTrue('numEmbeds' in result)
    self.assertTrue('numObjects' in result)
    self.assertTrue('numHyperlinks' in result)
    self.assertTrue('numMetaRefresh' in result)
    self.assertTrue('numHiddenElements' in result)
    self.assertTrue('numSmallElements' in result)
    self.assertTrue('hasDoubleDocuments' in result)
    self.assertTrue('numUnsafeIncludedUrls' in result)
    self.assertTrue('numExternalUrls' in result)
    self.assertTrue('percentUnknownElements' in result)

class TestElementCounting(HTMLAnalyzerTestCase):

  def setUp(self):
    HTMLAnalyzerTestCase.setUp(self)
    self.analyzer.loadHtml('<html><body><div></div><div></div></body></html>')

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
    self.analyzer.loadHtml('<html></html>')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 0)

  def test_LeadingSpaces(self):
    self.analyzer.loadHtml('   <html></html>')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 3)

  def test_TrailingSpaces(self):
    self.analyzer.loadHtml('<html></html>    ')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 4)

  def test_InnerSpaces(self):
    self.analyzer.loadHtml('<html>  <div> </div>  </html>')
    result = self.analyzer.countWhitespaceChars()
    self.assertEqual(result, 5)

class TestCountScriptChars(HTMLAnalyzerTestCase):

  def test_NoScripts(self):
    self.analyzer.loadHtml('<html></html>')
    result = self.analyzer.countScriptChars()
    self.assertEqual(result, 0)

  def test_EmptyScript(self):
    self.analyzer.loadHtml('<html><script></script></html>')
    result = self.analyzer.countScriptChars()
    self.assertEqual(result, 0)

  def test_InlineScript(self):
    self.analyzer.loadHtml('<html><script>alert("abc")</script></html>')
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

class TestIsMetaRefresh(HTMLAnalyzerTestCase):

  def test_MetaNoRefresh(self):
    elem = PyQuery('<meta></meta>')
    result = self.analyzer.isMetaRefresh(elem)
    self.assertFalse(result)

  def test_MetaWithHttpEquivAttribute(self):
    elem = PyQuery('<meta http-equiv="content-type"></meta>')
    result = self.analyzer.isMetaRefresh(elem)
    self.assertFalse(result)

  def test_MetaWithRefresh(self):
    elem = PyQuery('<meta http-equiv="refresh"></meta>')
    result = self.analyzer.isMetaRefresh(elem)
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
    self.analyzer.loadHtml('<html><head><title></title></head><body></body></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertFalse(result)

  def test_DoubleHtml(self):
    self.analyzer.loadHtml('<html></html><html></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

  def test_DoubleHead(self):
    self.analyzer.loadHtml('<html><head></head><head></head></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

  def test_DoubleTitle(self):
    self.analyzer.loadHtml('<html><head><title></title><title></title></head></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

  def test_DoubleBody(self):
    self.analyzer.loadHtml('<html><body></body><body></body></html>')
    result = self.analyzer.hasDoubleDocuments()
    self.assertTrue(result)

class TestGetAttrValues(HTMLAnalyzerTestCase):

  def test_NoAttributes(self):
    self.analyzer.loadHtml('<div></div><div></div>')
    result = self.analyzer.getAttrValues('div', 'id')
    self.assertEqual(len(result), 0)

  def test_MultipleAttributes(self):
    self.analyzer.loadHtml('<div id="a"></div><div id="b"></div>')
    result = self.analyzer.getAttrValues('div', 'id')
    self.assertTrue('a' in result)
    self.assertTrue('b' in result)

class TestGetUnsafeIncludedUrls(HTMLAnalyzerTestCase):

  def test_ScriptSrc(self):
    self.analyzer.loadHtml('<script src="script.js"></script>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertTrue('script.js' in result)

  def test_IframeSrc(self):
    self.analyzer.loadHtml('<iframe src="iframe.html"></iframe>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertTrue('iframe.html' in result)

  def test_FrameSrc(self):
    self.analyzer.loadHtml('<body><frame src="frame.html"></body>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertTrue('frame.html' in result)

  def test_EmbedSrc(self):
    self.analyzer.loadHtml('<embed src="embed.mov"></embed>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertTrue('embed.mov' in result)

  def test_FormAction(self):
    self.analyzer.loadHtml('<form action="submit.php"></form>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertTrue('submit.php' in result)

  def test_ObjectData(self):
    self.analyzer.loadHtml('<object data="object.swf"></object>')
    result = self.analyzer.getUnsafeIncludedUrls()
    self.assertTrue('object.swf' in result)

class TestGetSafeIncludedUrls(HTMLAnalyzerTestCase):

  def test_ImgSrc(self):
    self.analyzer.loadHtml('<img src="image.jpg" />')
    result = self.analyzer.getSafeIncludedUrls()
    self.assertTrue('image.jpg' in result)

  def test_LinkHref(self):
    self.analyzer.loadHtml('<link href="style.css" />')
    result = self.analyzer.getSafeIncludedUrls()
    self.assertTrue('style.css' in result)

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
    elem = PyQuery('<object classid="clsid:AE7AB96B-FF5E-4dce-801E-14DF2C4CD681"></object>')
    result = self.analyzer.isSuspiciousObject(elem)
    self.assertEqual(result, False)

  def test_SuspiciousObject(self):
    elem = PyQuery('<object classid="clsid:CA8A9780-280D-11CF-A24D-444553540000"></object>')
    result = self.analyzer.isSuspiciousObject(elem)
    self.assertEqual(result, True)

if __name__ == '__main__':
  unittest.main()

# py-xmltools - XML Traversal Wrapper

XML wrapper to traverse and quickly build an XML tree in native python dot and index notation, with no external dependencies outside the standard python library.

## Motivation
I needed a quick and dirty utiltiy to build XML responses for simulators. The simulators were hosted on hardware that was locked down.  I was only able to use python 2.5 and the base packages that came with it. At the time that meant combining this with bottle.py.



## How to use
* Attributes and non-python compatable xml tag names can be accessed with string index notation. `root['cool-beans']` or `root['@color']`
* If there is more than one xml element with the same tag name the first element will be chosen when using dot notation.
* If you want to access other elements with the same tag name use index with an integer.`root.table.h1[2]`
* Element existence can be tested. `if root.tag: print 'hi'`
* Elements that do not exist will not be created until a value is assigned.


### Eg:
```python
root = XMLObject("""
	<root>
		<a1><mytext>some data</mytext></a1>
		<a2>value1</a2>
		<a2 attrib1='somevalue'>value2</a2>
		<bad-tag><myval>12</myval></bad-tag>
	</root>""")

print '/root/a1/mytext/text() value is "%s"' % root.a1.mytext
print '/root/a2[1]/@attrib1 value is "%s"' % root.a2[1]['@attrib1']
print '/root/a2[0]/doesnotexist value is "%s"' % root.a2[0].doesnotexist
print '/root/bad-tag/myval/text() value is "%s"' % root['bad-tag'].myval
print '/root/a2[0]/myval value is "%s"' % root.a2
```

### Output is:
```python
/root/a1/mytext/text() value is "some data"
/root/a2[1]/@attrib1 value is "somevalue"
/root/a2[0]/doesnotexist value is "None"
/root/bad-tag/myval/text() value is "12"
/root/a2[0]/myval value is "value1"
```


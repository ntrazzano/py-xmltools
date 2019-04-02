# Copyright 2012 Neil Razzano
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

class XMLObject(object):
    '''Xml traversal wrapper
    
    XML wrapper to traverse an xml tree in native python dot and index notation. 
    
    Attributes and non-python compatable xml tag names can be accessed with string index notation.
    To access attributes prepend the attribute's name with the @ symbol.
    
    If there is more than one xml element with the same tag name the first element will be chosen when using dot notation.
    If you want to access other elements with the same tag name use index with an integer.
    Element existence can be tested as well, use with any boolean functions such as if.
    Elements that do not exist will not be created until a value is assigned.
    eg,
    
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
    
    Output is:
    /root/a1/mytext/text() value is "some data"
    /root/a2[1]/@attrib1 value is "somevalue"
    /root/a2[0]/doesnotexist value is "None"
    /root/bad-tag/myval/text() value is "12"
    /root/a2[0]/myval value is "value1"
    '''
    from xml.etree import ElementTree as ET
    def __init__(self, e=None, parent=None, name=None):
        if XMLObject.ET.iselement(e):
            self._list = list([e])
        elif isinstance(e, list):
            self._list = e
        elif e is not None:
            self._list = list([XMLObject.ET.XML(e)])
        else:
            self._list = list()
        self._parent = parent
        self._name = name
         
    def __getattribute__(self, key):
        if key.startswith("_"):
            return object.__getattribute__(self, key)

        if len(self._list) == 0:
            return XMLObject(parent=self, name=key)
        
        retVal = [child for child in list(self._list[0]) if child.tag == key ]
        
        if len(retVal) > 0:
            return XMLObject(retVal, parent=self, name=key)
        else:
            return XMLObject(parent=self, name=key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, key):
        if isinstance(key, int):
            try:
                return XMLObject(self._list[key], parent=self._parent, name=self._name)
            except IndexError:
                return XMLObject(parent=self._parent, name=self._name)
        elif key.startswith('@'):
            if len(self._list) == 0:
                return None
            else:
                return self._list[0].attrib.__getitem__(key[1:])
        else:
            return object.__getattribute__(self,'__getattribute__')(key)

    def _materialize(self):
        pe =  self._parent._getElement()
            
        # Create self, append to parent Element.
        s = XMLObject.ET.Element(self._name)
        pe.append(s)

        # Append self to our list.
        self._list.append(s)

    def __setattr__(self, name, value):
        if str(name).startswith("_"): 
            return object.__setattr__(self, name, value)
        
        if value is None:
            del self[name]
            return

        if len(self._list) == 0: 
                self._materialize()

        if isinstance(name, int):
            try:
                self._list[name].text = str(value)
            except IndexError:
                self._materialize()
                self._list[-1].text = str(value)
        elif name.startswith("@"):
            self._list[0].attrib[name[1:]] = str(value)
        else:
            matchedChildren = [child for child in self._list[0] if child.tag == name]

            if len(matchedChildren) > 0:
                # Modify existing child if something matched.
                matchedChildren[0].text = str(value)
            else:
                # Create new child if nothing matched.
                e = XMLObject.ET.Element(name)
                e.text = str(value)
                self._list[0].append(e)
    
    def _getElement(self):
        if len(self._list) == 0:
            self._materialize()
        return self._list[0]
            
    def __len__(self):
        return len(self._list)
            
    def __nonzero__(self):
        return len(self._list) != 0
            
    def __str__(self):
        if len(self._list) == 0: return str(None)
        return self._list[0].text or ""
        
    def __repr__(self):
        if len(self._list) == 0: return  "XMLObject()"
        return  "XMLObject('''%s''')" % XMLObject.ET.tostring(self._list[0])
    
    def __delattr__(self, name):
        for n in self._list:
            map( lambda x:  n.remove(x), 
                [child for child in list(n) if child.tag == name] )

    def __delitem__(self, key):
        if len(self._list) == 0: return

        if key.startswith("@"):
            del self._list[0].attrib[key[1:]]
        else:
            self.__delattr__(key)

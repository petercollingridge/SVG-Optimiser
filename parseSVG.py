#!/usr/bin/env python

import xml.etree.ElementTree as ET
import re

# Regex
re_translate = re.compile('\((-?\d+\.?\d*)\s*,?\s*(-?\d+\.?\d*)\)')

value_attributes = ["x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "width", "height"]

position_attributes = {"rect":    (["x", "y"]),
                       "circle":  (["cx", "cy"]),
                       "ellipse": (["cx", "cy"]),
                       "line":    (["x1", "y1", "x2", "y2"])}

def fixtag(tag, namespaces):
    # given a decorated tag (of the form {uri}tag), return prefixed
    # tag and namespace declaration, if any
    if isinstance(tag, ET.QName):
        tag = tag.text
    namespace_uri, tag = tag[1:].split("}", 1)
    prefix = namespaces.get(namespace_uri)
    if prefix is None:
        prefix = ET._namespace_map.get(namespace_uri)
        if prefix is None:
            prefix = "ns%d" % len(namespaces)
        namespaces[namespace_uri] = prefix
        
        if prefix == "xml":
            xmlns = None
        else:
            xmlns = ("xmlns", namespace_uri)
    else:
        xmlns = None
        
    return tag, xmlns

def printNode(node):
    print ">", node.tag.split('}')[1]

class SVGTree(ET.ElementTree):

    def _write(self, file, node, encoding, namespaces):
        """ Overwrite the normal method to avoid writing namespaces everywhere. """
    
        # write XML to file
        tag = node.tag
        if tag is ET.Comment:
            file.write("<!-- %s -->" % _escape_cdata(node.text, encoding))
        elif tag is ET.ProcessingInstruction:
            file.write("<?%s?>" % _escape_cdata(node.text, encoding))
        else:
            items = node.items()
            xmlns_items = [] # new namespaces in this scope
            try:
                if isinstance(tag, ET.QName) or tag[:1] == "{":
                    tag, xmlns = fixtag(tag, namespaces)
                    if xmlns: xmlns_items.append(xmlns)
            except TypeError:
                _raise_serialization_error(tag)
            file.write("<" + ET._encode(tag, encoding))
            
            if items or xmlns_items:
                items.sort() # lexical order
                for k, v in items:
                    file.write(" %s=\"%s\"" % (ET._encode(k, encoding), ET._escape_attrib(v, encoding)))
                for k, v in xmlns_items:
                    file.write(" %s=\"%s\"" % (ET._encode(k, encoding), ET._escape_attrib(v, encoding)))
                    
            if node.text or len(node):
                file.write(">")
                if node.text:
                    file.write(ET._escape_cdata(node.text, encoding))
                for n in node:
                    self._write(file, n, encoding, namespaces)
                file.write("</" + ET._encode(tag, encoding) + ">")
                
            else:
                file.write(" />")
            for k, v in xmlns_items:
                del namespaces[v]
        if node.tail:
            file.write(ET._escape_cdata(node.tail, encoding))

class CleanSVG:
    def __init__(self, svgfile=None):
        self.tree = SVGTree()
        self.root = None
        
        self.num_format = "%s"
        self.setDemicalPlaces(1)
        
        if file:
            self.parseFile(svgfile)
            
    def parseFile(self, filename):
        self.tree.parse(filename)
        self.root = self.tree.getroot()
        
    def write(self, filename):
        self.tree.write(filename)
    
    def setDemicalPlaces(self, dps):
        if dps == 0:
            self.num_format = "%d"
        else:
            self.num_format = "%%.%df" % dps    
    
    def _traverse(self, node, func, *args):
        """ Call a passed function with a node and all its descendents. """
        
        func(node, args)
        
        for child in node.getchildren():
            self._traverse(child, func, *args)

    def findTransforms(self):
        self._traverse(self.root, self._handleTransforms)

    def cleanDecimals(self, decimal_places):
        self.setDemicalPlaces(decimal_places)
        self._traverse(self.root, self._cleanDecimals)

    def _cleanDecimals(self, node, *args):
        for attribute in value_attributes:
            if attribute in node.keys():
                node.set(attribute, self.num_format % float(node.get(attribute)))

    def _handleTransforms(self, node, *args):
        printNode(node)
        
        if 'transform' in node.keys():
            transform = node.get('transform')
            
            if "translate" in transform:
                translation = re_translate.search(transform)
                if translation:
                    print " - translate by: (%s, %s)" % translation.group(1,2)
                    self._translateElement(node, translation.group(1,2))
                
    def _translateElement(self, element, delta):
        element_type = element.tag.split('}')[1]
        coords = position_attributes.get(element_type)
            
        if coords:
            for i, coord_name in enumerate(coords):
                new_coord = float(element.get(coord_name, 0)) + float(delta[i % 2])
                element.set(coord_name, self.num_format % new_coord)
            
            del element.attrib['transform']

def main():
    import os
    filename = os.path.join('examples', 'translations.svg')
    
    s = CleanSVG(filename)
    s.setDemicalPlaces(1)
    s.cleanDecimals(1)
    s.findTransforms()
    s.write('%s_test.svg' % filename[:-4])
    
if __name__ == "__main__":
    main()
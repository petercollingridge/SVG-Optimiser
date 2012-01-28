#!/usr/bin/env python

import xml.etree.ElementTree as ET
import re

# Regex
re_translate = re.compile('\((-?\d+\.?\d*)\s*,?\s*(-?\d+\.?\d*)\)')
re_coord_split = re.compile('\s+|,')
re_trailing_zeros = re.compile('\.(\d*?)(0+)$')

# Attribute names
value_attributes = ["x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height"]

position_attributes = {"rect":    (["x", "y"]),
                       "circle":  (["cx", "cy"]),
                       "ellipse": (["cx", "cy"]),
                       "line":    (["x1", "y1", "x2", "y2"])}

def qname(tag):
    if '}' in tag:
        return tag.split('}')[1]
    else:
        return tag

def _serialize_xml(write, elem, encoding, namespaces):
    tag = elem.tag
    text = elem.text
    if tag is ET.Comment:
        write("<!--%s-->" % ET._encode(text, encoding))
    elif tag is ET.ProcessingInstruction:
        write("<?%s?>" % ET._encode(text, encoding))
    else:
        tag = qname(tag)
        if tag is None:
            if text:
                write(ET._escape_cdata(text, encoding))
            for e in elem:
                _serialize_xml(write, e, encoding, None)
        else:
            write("<" + tag)
            items = elem.items()
            if items or namespaces:
                if namespaces:
                    for v, k in sorted(namespaces.items(), key=lambda x: x[1]):  # sort on prefix
                        write(" xmlns=\"%s\"" % (ET._escape_attrib(v, encoding)))
                for k, v in sorted(items):  # lexical order
                    if isinstance(k, ET.QName):
                        k = k.text
                    if isinstance(v, ET.QName):
                        v = qnames[v.text]
                    else:
                        v = ET._escape_attrib(v, encoding)
                    write(" %s=\"%s\"" % (qname(k), v))
            if text or len(elem):
                write(">")
                if text:
                    write(ET._escape_cdata(text, encoding))
                for e in elem:
                    _serialize_xml(write, e, encoding, None)
                write("</" + tag + ">")
            else:
                write(" />")
    if elem.tail:
        write(ET._escape_cdata(elem.tail, encoding))

def printNode(node):
    print ">", node.tag.split('}')[1]

class SVGTree(ET.ElementTree):

    def write(self, file_or_filename, xml_declaration=None, default_namespace=None):
        """ Overwrite the normal method to avoid writing namespaces everywhere. """
        
        assert self._root is not None
        
        if hasattr(file_or_filename, "write"):
            file = file_or_filename
        else:
            file = open(file_or_filename, "wb")
            
        write = file.write
        # Might be able to ignore this - should go through tags and remove namespaces
        qnames, namespaces = ET._namespaces(self._root, "us-ascii", default_namespace)
        _serialize_xml(write, self._root, "us-ascii", namespaces)
        
        if file_or_filename is not file:
            file.close()

class CleanSVG:
    def __init__(self, svgfile=None):
        self.tree = SVGTree()
        self.root = None
        
        self.num_format = "%s"
        
        if file:
            self.parseFile(svgfile)
            
    def parseFile(self, filename):
        self.tree.parse(filename)
        self.root = self.tree.getroot()
        
    def write(self, filename):
        self.tree.write(filename)
    
    def setDemicalPlaces(self, decimal_places):
        if decimal_places == 0:
            self.num_format = "%d"
        else:
            self.num_format = "%%.%df" % decimal_places
        self._traverse(self.root, self._cleanDecimals) 
    
    def _traverse(self, node, func, *args):
        """ Call a passed function with a node and all its descendents. """
        
        func(node, args)
        
        for child in node.getchildren():
            self._traverse(child, func, *args)

    def stripAttribute(self, attribute):
        """ Remove all instances of a given attribute. """
        self._traverse(self.root, self._removeAttribute, attribute)

    def cleanDecimals(self, decimal_places):
        """ Ensure all numbers have equal or fewer than a given number of decimal places. """
        self.setDemicalPlaces(decimal_places)
        self._traverse(self.root, self._cleanDecimals)
        
    def findTransforms(self):
        self._traverse(self.root, self._handleTransforms)

    def _removeAttribute(self, element, attributes):
        for attribute in attributes:
            if attribute in element.keys():
                del element.attrib[attribute]

    def _cleanDecimals(self, element, *args):
        for attribute in element.keys():
            if attribute == "points":
                values = map(self._formatNumber, re_coord_split.split(element.get(attribute)))
                point_list = " ".join((values[i] + "," + values[i+1] for i in range(0, len(values), 2)))
                element.set("points", point_list)
                
            elif attribute in value_attributes:
                element.set(attribute, self._formatNumber(element.get(attribute)))

    def _formatNumber(self, number):
        """ Convert a number to a string representation 
            with the appropriate number of decimal places. """
        
        try:
            number = float(number)
        except ValueError:
            return number
        
        str_number = self.num_format % number
        trailing_zeros = re_trailing_zeros.search(str_number)
        
        if trailing_zeros:
            # length equals number of trailing zeros + decimal point if no other numbers
            length = (len(trailing_zeros.group(2)) + (len(trailing_zeros.group(1)) == 0))
            str_number = str_number[:-length]
        
        return str_number

    def _handleTransforms(self, node, *args):
        if 'transform' in node.keys():
            transform = node.get('transform')
            
            if "translate" in transform:
                translation = re_translate.search(transform)
                if translation:
                    self._translateElement(node, translation.group(1,2))
                
    def _translateElement(self, element, delta):
        print " - translate by: (%s, %s)" % delta
        element_type = element.tag.split('}')[1]
        coords = position_attributes.get(element_type)

        if coords:
            for i, coord_name in enumerate(coords):
                new_coord = float(element.get(coord_name, 0)) + float(delta[i % 2])
                element.set(coord_name, self._formatNumber(new_coord))
            del element.attrib['transform']
                
        elif "points" in element.keys():
            values = [float(v) + float(delta[i % 2]) for i, v in enumerate(re_coord_split.split(element.get("points")))]
            str_values = map(self._formatNumber, values)
            point_list = " ".join((str_values[i] + "," + str_values[i+1] for i in range(0, len(str_values), 2)))
            element.set("points", point_list)
            del element.attrib['transform']

def main(filename):
    s = CleanSVG(filename)
    s.setDemicalPlaces(1)
    s.findTransforms()
    s.stripAttribute('id')
    s.write('%s_test.svg' % filename[:-4])
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        import os
        main(os.path.join('examples', 'translations.svg'))
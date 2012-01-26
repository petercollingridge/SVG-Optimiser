#!/usr/bin/env python

from xml.etree.ElementTree import ElementTree
import re

# Regex
re_translate = re.compile('\((-?\d+\.?\d*)\s*,?\s*(-?\d+\.?\d*)\)')

position_attributes = {"rect":    (["x", "y"]),
                       "circle":  (["cx", "cy"]),
                       "ellipse": (["cx", "cy"]),
                       "line":    (["x1", "y1", "x2", "y2"])}

def printNode(node):
    print node.tag

class CleanSVG:
    def __init__(self, svgfile=None):
        self.tree = ElementTree()
        self.root = None
        
        self.num_format = "%s"
        
        if file:
            self.parseFile(svgfile)
            
    def parseFile(self, filename):
        self.tree.parse(filename)
        self.root = self.tree.getroot()
        
    def write(self, filename):
        self.tree.write(filename)
    
    def _traverse(self, node, func, *args):
        """ Call a passed function with a node and all its descendents. """
        
        func(node, args)
        
        for child in node.getchildren():
            self._traverse(child, func, *args)

    def findTransforms(self):
        self._traverse(self.root, self._handleTransforms)

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
    s.findTransforms()
    s.write('%s_test.svg' % filename[:-4])
    
if __name__ == "__main__":
    main()
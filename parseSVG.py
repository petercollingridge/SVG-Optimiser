#!/usr/bin/env python

from xml.etree.ElementTree import ElementTree

def printNode(node):
    print node.tag

def translateRect(rect, dx, dy):
    x = float(rect.get('x', 0)) + dx
    y = float(rect.get('y', 0)) + dy
    
    rect.set("x", "%.2f" % x)
    rect.set("y", "%.2f" % y)
    

class CleanSVG:
    def __init__(self, svgfile=None):
        self.tree = ElementTree()
        self.root = None
        
        if file:
            self.parseFile(svgfile)
            
    def parseFile(self, filename):
        self.tree.parse(filename)
        self.root = self.tree.getroot()
        
    def write(self, filename):
        print self.tree.write(filename)
    
    def _traverse(self, node, func=printNode):
        """ Call a passed function with a node and all its descendents. """
        
        func(node)
        
        for child in node.getchildren():
            self._traverse(child, func)

    def findTransforms(self):
        self._traverse(self.root, func=self.handleTransforms)

    def handleTransforms(self, node):
        #printNode(node)
        
        if 'transform' in node.keys():
            print " -transform"
            transform = node.get('transform')
            
            if "translate" in transform:
                print " -translate by:", map(float, transform[10:-1].split(','))
                if node.tag.split('}')[1] == 'rect':
                    translateRect(node,3,3)

def d():
    tree = ElementTree()
    tree.parse("test_shape.svg")

    root = tree.getroot()
    doc = root.getchildren()[-1]

    traverse(doc, func=findTransforms)

s = CleanSVG('test_translate.svg')
s.findTransforms()
s.write('test.svg')
#!/usr/bin/env python

from lxml import etree
import re

# Regex
re_translate = re.compile('\((-?\d+\.?\d*)\s*,?\s*(-?\d+\.?\d*)\)')
re_coord_split = re.compile('\s+|,')
re_trailing_zeros = re.compile('\.(\d*?)(0+)$')
re_length = re.compile('^(\d+\.?\d*)\s*(em|ex|px|in|cm|mm|pt|pc|%|\w*)')

# Attribute names
value_attributes = ["x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height"]
default_styles = set([
    ("opacity", "1"),
    ("fill-opacity", "1"),
    ("stroke-width", "1"),
    ("stroke-opacity", "1"),
    ("stroke-miterlimit", "4"),
    ("stroke-linecap", "butt"),
    ("stroke-dasharray", "none"),
    ("stroke-dashoffset", "0")
])

position_attributes = {"rect":    (["x", "y"]),
                       "circle":  (["cx", "cy"]),
                       "ellipse": (["cx", "cy"]),
                       "line":    (["x1", "y1", "x2", "y2"])}

class CleanSVG:
    def __init__(self, svgfile=None):
        self.tree = None
        self.root = None
        
        # Need to update this if style elements found
        self.styles = {}
        self.style_counter = 0
        
        self.num_format = "%s"
        
        if file:
            self.parseFile(svgfile)
            
    def parseFile(self, filename):
        self.tree = etree.parse(filename)
        self.root = self.tree.getroot()
        
    def write(self, filename):
        if self.styles:
            self._addStyleElement()
        self.tree.write(filename, pretty_print=True)
    
    def _addStyleElement(self):
        """ Insert a CSS style element containing information 
            from self.styles to the top of the file. """
        
        style_element = etree.SubElement(self.root, "style")
        self.root.insert(0, style_element)
        style_text = '\n'
        
        # Should order styles
        for styles, style_class in self.styles.iteritems():
            style_text += "\t.%s{\n" % style_class
            for (style_id, style_value) in styles:
                style_text += '\t\t%s:\t%s;\n' % (style_id, style_value)
            style_text += "\t}\n"
        
        style_element.text = style_text
    
    def setDemicalPlaces(self, decimal_places):
        if decimal_places == 0:
            self.num_format = "%d"
        elif decimal_places > 0:
            self.num_format = "%%.%df" % decimal_places
        else:
            self.num_format = "%s"
            
        for element in self.tree.iter():
            self._cleanDecimals(element)

    def removeAttribute(self, attribute):
        """ Remove all instances of a given attribute. """
        
        for element in self.tree.iter():
            self._removeAttribute(element, attribute)
        
    def removeNamespace(self, namespace):
        """ Remove all attributes of a given namespace. """
        
        nslink = self.root.nsmap.get(namespace)
        if nslink:
            nslink = "{%s}" % nslink
            length = len(nslink)
            
            for element in self.tree.iter():
                self._removeNamespace(element, nslink, length)
                
            del self.root.nsmap[namespace]

    def cleanDecimals(self, decimal_places):
        """ Round all numbers to a given number of decimal places. """
        
        self.setDemicalPlaces(decimal_places)
        for element in self.tree.iter():
            self._cleanDecimals(element)
    
    def extractStyles(self):
        """ Remove style attribute and but in <style> element as CSS. """
        
        for element in self.tree.iter():
            self._extractStyles(element)
    
    def applyTransforms(self):
        """ Apply transforms to element coordinates. """
        
        for element in self.tree.iter():
            self._applyTransforms(element)

    def _removeAttribute(self, element, *attributes):
        for attribute in attributes:
            if attribute in element.attrib.keys():
                del element.attrib[attribute]
                
    def _removeNamespace(self, element, namespace, length):
        for attribute in element.attrib.keys():
            if attribute[:length] == namespace:
                del element.attrib[attribute]

    def _cleanDecimals(self, element):
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

    def _extractStyles(self, element):
        if "style" in element.keys():
            styles = element.attrib["style"].split(';')
            style_list = [tuple(style.split(':')) for style in styles]
        
            # Remove pointless styles, e.g. opacity = 1
            for default_style in default_styles & set(style_list):
                style_list.remove(default_style)
                
            # Clean decimals:
            for i, (style_name, style_value) in enumerate(style_list):
                number = re_length.search(style_value)
                if number:
                    clean_number = self._formatNumber(number.group(1))
                    style_list[i] = (style_name, clean_number + number.group(2))
                
            style_tuple = tuple(style_list)
            if style_tuple not in self.styles:
                style_class = "style%d" % self.style_counter
                self.styles[style_tuple] = style_class
                self.style_counter += 1
            else:
                style_class = self.styles[style_tuple]
                
            # Should test to see whether there is already a class
            element.set("class", style_class)
            del element.attrib["style"]

    def _applyTransforms(self, element):
        if 'transform' in element.keys():
            transform = element.get('transform')
            
            if "translate" in transform:
                translation = re_translate.search(transform)
                if translation:
                    self._translateElement(element, translation.group(1,2))
                
    def _translateElement(self, element, delta):
        print " - translate by: (%s, %s)" % delta
        element_type = element.tag.split('}')[1]
        coords = position_attributes.get(element_type)

        if coords:
            for i, coord_name in enumerate(coords):
                new_coord = float(element.get(coord_name, 0)) + float(delta[i % 2])
                element.set(coord_name, self._formatNumber(new_coord))
            del element.attrib["transform"]
                
        elif "points" in element.keys():
            values = [float(v) + float(delta[i % 2]) for i, v in enumerate(re_coord_split.split(element.get("points")))]
            str_values = map(self._formatNumber, values)
            point_list = " ".join((str_values[i] + "," + str_values[i+1] for i in range(0, len(str_values), 2)))
            element.set("points", point_list)
            del element.attrib["transform"]

def main(filename):
    svg = CleanSVG(filename)
    svg.removeAttribute('id')
    svg.removeNamespace('sodipodi')
    svg.setDemicalPlaces(2)
    svg.extractStyles()
    svg.applyTransforms()
    svg.write('%s_test.svg' % filename[:-4])
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        import os
        #main(os.path.join('examples', 'translations.svg'))
        #main(os.path.join('examples', 'styles.svg'))
        main(os.path.join('examples', 'Chlamydomonas.svg'))
#!/usr/bin/env python

from lxml import etree
import re

# Regex
re_transform = re.compile('([a-zA-Z]+)\((-?\d+\.?\d*),?\s*(-?\d+\.?\d*)?\)')
re_translate = re.compile('\((-?\d+\.?\d*)\s*,?\s*(-?\d+\.?\d*)\)')
re_coord_split = re.compile('\s+|,')
re_path_coords = re.compile('[a-zA-Z]')
re_path_split = re.compile('([ACHLMQSTVZachlmqstvz])')
re_trailing_zeros = re.compile('\.(\d*?)(0+)$')
re_length = re.compile('^(\d+\.?\d*)\s*(em|ex|px|in|cm|mm|pt|pc|%|\w*)')

# Path commands
path_commands = {
    "M": (0, 1),
    "L": (0, 1),
    "T": (0, 1),
    "H": (0),
    "V": (1),
    "A": (-1, -1, -1, -1, -1, 0, 1),    
    "C": (0, 1, 0, 1, 0, 1)
}

# Attribute names
value_attributes = ["x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height"]
default_styles = set([
    ("opacity", "1"),
    ("fill-opacity", "1"),
    ("stroke", "none"),
    ("stroke-width", "1"),
    ("stroke-opacity", "1"),
    ("stroke-miterlimit", "4"),
    ("stroke-linecap", "butt"),
    ("stroke-linejoin", "miter"),
    ("stroke-dasharray", "none"),
    ("stroke-dashoffset", "0"),
    ("font-anchor", "start"),
    ("font-style", "normal"),
    ("font-weight", "normal"),
    ("font-stretch", "normal"),
    ("font-variant", "normal")
])

position_attributes = {"rect":    (["x", "y"]),
                       "tspan":   (["x", "y"]),
                       "circle":  (["cx", "cy"]),
                       "ellipse": (["cx", "cy"]),
                       "line":    (["x1", "y1", "x2", "y2"])}

scaling_attributes = {"rect":    (["x", "y", "width", "height"]),}

class CleanSVG:
    def __init__(self, svgfile=None):
        self.tree = None
        self.root = None
        
        # Need to update this if style elements found
        self.styles = {}
        self.style_counter = 0
        
        self.num_format = "%s"
        
        if svgfile:
            self.parseFile(svgfile)
            
    def parseFile(self, filename):
        self.tree = etree.parse(filename)
        self.root = self.tree.getroot()
    
    def analyse(self):
        """ Search for namespaces. Will do more later """
        
        print "Namespaces:"
        for ns, link in self.root.nsmap.iteritems():
            print "  %s: %s" % (ns, link)
            
    def removeGroups(self):
        """ Remove groups with no attributes """
        # Doesn't work for nested groups
        
        for element in self.tree.iter():
            if not isinstance(element.tag, basestring):
                continue
            
            element_type = element.tag.split('}')[1]
            if element_type == 'g' and not element.keys():
                parent = element.getparent()
                if parent is not None:
                    parent_postion = parent.index(element)
                    print
                    print parent
                    # Move children outside of group
                    for i, child in enumerate(element, parent_postion):
                        print i
                        print "move %s to %s" % (child, i)
                        parent.insert(i, child)
                        
                    #del parent[i]
    
    def write(self, filename):
        """ Write current SVG to a file. """
        
        if not filename.endswith('.svg'):
            filename += '.svg'
        
        if self.styles:
            self._addStyleElement()
        self.tree.write(filename, pretty_print=True)
        
    def toString(self):
        """ Return a string of the current SVG """
        
        if self.styles:
            self._addStyleElement()
        return etree.tostring(self.root)
    
    def _addStyleElement(self):
        """ Insert a CSS style element containing information 
            from self.styles to the top of the file. """
        
        style_element = etree.SubElement(self.root, "style")
        self.root.insert(0, style_element)
        style_text = '\n'
        
        for styles, style_class in sorted(self.styles.iteritems(), key=lambda (k,v): v):
            style_text += "\t.%s{\n" % style_class
            for (style_id, style_value) in styles:
                style_text += '\t\t%s:\t%s;\n' % (style_id, style_value)
            style_text += "\t}\n"
        
        style_element.text = style_text
    
    def setDecimalPlaces(self, decimal_places):
        """ Round attribute numbers to a given number of decimal places. """
        
        if decimal_places == 0:
            self.num_format = "%d"
        elif decimal_places > 0:
            self.num_format = "%%.%df" % decimal_places
        else:
            self.num_format = "%s"
        
        for element in self.tree.iter():
            if not isinstance(element.tag, basestring):
                continue
            
            tag = element.tag.split('}')[1]
            
            if tag == "polyline" or tag == "polygon":
                coords = map(self._formatNumber, re_coord_split.split(element.get("points")))
                point_list = " ".join((coords[i] + "," + coords[i+1] for i in range(0, len(coords), 2)))
                element.set("points", point_list)
                
            elif tag == "path":
                coords = map(self._formatNumber, re_coord_split.split(element.get("d")))
                coord_list = " ".join(coords)
                element.set("d", coord_list)
                #for coord in coords:
                #    if re_path_coords.match(coord):
                #        print coord
                
            else:
                for attribute in element.attrib.keys():
                    if attribute in value_attributes:
                        element.set(attribute, self._formatNumber(element.get(attribute)))

    def removeAttributes(self, *attributes):
        """ Remove all instances of a given list of attributes. """
        
        for element in self.tree.iter():
            for attribute in attributes:
                if attribute in element.attrib.keys():
                    del element.attrib[attribute]
    
    def removeNamespace(self, namespace):
        """ Remove all attributes of a given namespace. """
        
        nslink = self.root.nsmap.get(namespace)
        if nslink:
            nslink = "{%s}" % nslink
            length = len(nslink)
            
            for element in self.tree.iter():
                if element.tag[:length] == nslink:
                    self.root.remove(element)
                
                for attribute in element.attrib.keys():
                    if attribute[:length] == nslink:
                        del element.attrib[attribute]
                
            del self.root.nsmap[namespace]
    
    def extractStyles(self):
        """ Remove style attribute and but in <style> element as CSS. """
        
        for element in self.tree.iter():
            if "style" in element.keys():
                styles = element.attrib["style"].split(';')
                style_list = [tuple(style.split(':')) for style in styles]

                # Ensure styling is in the form: (key, value)
                style_list = [style for style in style_list if len(style)==2]
            
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
    
    def applyTransforms(self):
        """ Apply transforms to element coordinates. """
        
        for element in self.tree.iter():
            if 'transform' in element.keys():
                transform = element.get('transform')
                transformations = re_transform.findall(transform)
                transformations.reverse()
                
                element_type = element.tag.split('}')[1]
                if element_type == 'g':
                    self._applyGroupTransforms(element, transformations)
                
                sucessful_transformation = False
                for transformation in transformations:
                    delta = [float(n) for n in transformation[1:] if n]
                    if transformation[0] == 'translate':
                        sucessful_transformation = self._translateElement(element, delta)
                    elif transformation[0] == 'scale':
                        sucessful_transformation = self._scaleElement(element, delta)
                
                # Doesn't take into account if one transformation isn't sucessful
                if sucessful_transformation:
                    del element.attrib["transform"]
    
    def _applyGroupTransforms(self, group_element, transformations):
        
        # Ensure all child elements are paths
        children = [child for child in group_element if isinstance(child.tag, basestring)]
        if any((child.tag.split('}')[1] != 'path' for child in children)):
            return
            
        f_dict = {'translate': self._translatePath, 'scale': self._scalePath}
        
        sucessful_transformation = False
        for transformation in transformations:
            delta = [float(n) for n in transformation[1:] if n]
            
            trans_f = f_dict.get(transformation[0])
            if trans_f:
                for child in children:
                    sucessful_transformation = trans_f(child, delta)
        
        if sucessful_transformation:
            del group_element.attrib["transform"]
    
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

    def _translateElement(self, element, delta):
        #print " - translate by: (%s, %s)" % delta
        element_type = element.tag.split('}')[1]
        coords = position_attributes.get(element_type)

        if coords:
            for i, coord_name in enumerate(coords):
                new_coord = float(element.get(coord_name, 0)) + delta[i % 2]
                element.set(coord_name, self._formatNumber(new_coord))
            return True
            
        elif "points" in element.keys():
            values = [float(v) + delta[i % 2] for i, v in enumerate(re_coord_split.split(element.get("points")))]
            str_values = map(self._formatNumber, values)
            point_list = " ".join((str_values[i] + "," + str_values[i+1] for i in range(0, len(str_values), 2)))
            element.set("points", point_list)
            return True
            
        elif "d" in element.keys():
            self._translatePath(element, delta)
            return True

    def _scaleElement(self, element, delta):
        if len(delta) == 1:
            delta = [delta[0], delta[0]]        
        
        element_type = element.tag.split('}')[1]
        coords = scaling_attributes.get(element_type)
        
        if coords:
            for i, coord_name in enumerate(coords):
                new_coord = float(element.get(coord_name, 0)) * delta[i % 2]
                element.set(coord_name, self._formatNumber(new_coord))
            return True

    def _translatePath(self, path, delta):
        delta.append(0) # add as a null value for flags
        commands = self._parsePath(path.get("d"))

        new_d = ""
        for command, values in commands:
            new_d += command
            if command in path_commands:
                d = path_commands[command]
                for n, value in enumerate(values):
                    new_d += "%s " % self._formatNumber(value + delta[ d[n % len(d)]])
            else:
                new_d += " ".join(map(self._formatNumber, values))

        path.set("d", new_d)
        return True
        
    def _scalePath(self, path, delta):
        if len(delta) == 1:
            delta = [delta[0], delta[0], 0]
        elif len(delta) == 2:
            delta.append(0) # add as a null value for flags
            
        commands = self._parsePath(path.get("d"))

        new_d = ""
        for command, values in commands:
            new_d += command
            if command in path_commands:
                d = path_commands[command]
                for n, value in enumerate(values):
                    new_d += "%s " % self._formatNumber(value * delta[ d[n % len(d)]])
            else:
                new_d += " ".join(map(self._formatNumber, values))

        path.set("d", new_d)
        return True
    
    def _parsePath(self, d):
        commands = []
        split_commands = re_path_split.split(d)
        
        if len(split_commands) > 2:
            for command, values in [(split_commands[i], split_commands[i+1]) for i in range(1, len(split_commands), 2)]:
                values = [float(value) for value in re_coord_split.split(values) if value != '']
                commands.append((command, values))
        
        return commands

def main(filename):
    svg = CleanSVG(filename)
    svg.removeAttributes('id')
    svg.removeNamespace('sodipodi')
    svg.removeNamespace('inkscape')
    svg.removeGroups()
    svg.extractStyles()
    svg.setDecimalPlaces(2)
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
        main(os.path.join('examples', 'paths.svg'))
        #main(os.path.join('examples', 'Chlamydomonas.svg'))

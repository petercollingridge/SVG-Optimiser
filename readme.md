Python program to clean up SVG files, particularly those created by Inkscape or Illustrator



# --- Current Functionality ---

## Remove attributes
	Remove attributes with a given name, e.g. remove 'id' attributes, which often aren't used.

## Remove comments
    Removes all comments.

## Remove elements
    Remove elements by their tag name.

## Remove namespaces
	Remove all attributes associated with a given namespace, e.g. remove 'sodipodi' attributes created by Inkscape.
	
## Remove redundant groups
	Move child elements outdside of group with no attributes, then delete group.

## Set decimal places
    Rewrite attributes to a given number of decimal places.
    Strip out unnecessary trailing zeros.
    
* Attributes
	- x, y, x1, y2, x2, y2
	- cx, cy
	- r, rx, ry
	- width, height
	- points
	- d

## Apply transformations
	Applies transformations to elements so the attribute can be removed.

* Translation
    - In the form
        - comma: (12,34)
        - space(s): (12 34)
        - comma and space(s): (12, 34), (12 ,34), (12 , 34)
        - decimal: (1.2, 3.4)
        - negative: (-1.2, -3.4)
        
    - Shapes
        - line
        - rect
        - circle, ellipse
        - polyline, polygon
        - path (not fully tested)
        - g (not fully tested)
        
* Scale
    - Shapes
        - path
        - rect

## CSS stlying
    Convert individual style attributes to CSS styling.
    Remove default styles.
    
# --- To Do ---

## Remove namespaces
	Remove xml namespace if possible
	
## Groups
	Remove unnecessary groups
	Remove unnecessary text groups
	Add groups in make styling and transforms more efficient

## Transformations

* Translation
    - In the form
        - single: (12)

    - Shapes
        - text
        - tspan
        
* Rotation
    - Shapes
        - path
        - polyline/polygon
        - line
        - circle
        - rect -> polygon/path?
        
* Scale
    - Shapes
        - polyline/polygon
        - line
        - circle -> ellipse?
        
* SkewX and SkewY
	- Shapes
		- line
		- path
		- polyline/polygon
		- rect -> polygon/path?
		- circle -> path arc?
		
* Matrix
	- Shapes
		- line
		- path
		- polyline/polygon
		- rect -> polygon/path?
            
## CSS styling
	Need to check whether style element already exists and whether class names already exist.
    Ideally find most efficient way to class elements for styling.
    
## License

	

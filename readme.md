Python program to clean up SVG files, particularly those created by Inkscape or Illustrator

# --- Current Functionality ---

## Remove attributes
	Remove attributes with a given name, e.g. remove 'id' attributes, which often aren't used.

## Remove namespaces
	Remove all attributes associated with a given namespace, e.g. remove 'sodipodi' attributes created by Inkscape.

## Decimal places
    Rewrite attributes to a given number of decimal places.
    Strips out unnecessary trailing zeros.
    
* Attributes
	- x, y, x1, y2, x2, y2
	- cx, cy
	- r, rx, ry
	- width, height
	- points

## Transformations
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

## CSS stlying
    Convert individual style attributes to CSS styling.
    
# --- To Do ---

## Decimal places    
* Attributes
	- path: d

## Transformations

* Translation
    - In the form
        - single: (12)

    - Shapes
        - path
        - g
        - text
        - tspan
        
* Rotation
    - Shapes
        - path
        - polyline
        - line
        - circle
        - rect -> polygon?
        
* Scale
    - Shapes
        - path
        - polyline
        - line
        - rect
        - circle -> ellipse?
            
## CSS stlying
	Need to check whether style element already exists and whether class names already exist.
    Ideally find most efficient way to class elements for styling.
    
## Flatten groups
	Remove groups that aren't adding properties, such as animations or transforms

function SVGElement() {

    this.extractAttributes = function(data) {
        // Extract a list of attributes from the passed data
        var attr = {};
        data.each(function() {
            $.each(this.attributes, function(i, attrib) {
                attr[attrib.name] = attrib.value;
            });
        });

        this.attr = attr;

        for (var a in this.required_attributes) {
            var attribute = this.required_attributes[a];
            if (attribute === "points" || attribute === "d") {
                if (!this.attr[attribute]) { this.attr[attribute] = ""; }
                this.parseCoordinates(this.attr[attribute]);
            } else {
                if (!this.attr[attribute]) { this.attr[attribute] = 0; }
                this.attr[attribute] = parseFloat(this.attr[attribute]);
            }
        }
    };

    this.parseCoordinates = function(coords) {
        var coord_list = coords.split(/(?:\s*,\s*)|(?:\s+)/);
        this.coords = [];
        for (var i=0; i<coord_list.length; i+=2){
            this.coords.push([parseFloat(coord_list[i]), parseFloat(coord_list[i+1])])
        }
    }

    this.translate = function(dx, dy) {
        return false;
    }

    this.scale = function(sx, sy) {
        return false;
    }

    this.rotate = function(t, cx, cy) {
        return false;
    }

    this.skewX = function(t) {
        return false;
    }

    this.skewY = function(t) {
        return false;
    }

    this.matrix = function(a, b, c, d, e, f) {
        if (b === 0 && c === 0){
            this.scale(a, d);
            this.translate(e, f);
        } else {
            return false;
        }
    }

    this.compareAttributes = function(results) {
        for (var i in results) {
			if (this.attr[i] !=  results[i]) {
				console.log(" - " + i + " = " + this.attr[i] + " (not " + results[i] + ")");
				return false;
			}
		}
        return true;
    }
    
    this.write = function() {
        var str = '<' + this.name;
        for (var a in this.attr) {
            // Don't write attributes that are equal to 0 - need to check that these are just required attributes
            if (this.attr[a] != 0) {
                str += ' ' + a + '="' + this.attr[a] + '"';
            }
        }
        str += '/>'
        return str;
    };
}

function SVG_Circle() {
    this.name = "circle";
    this.required_attributes = ["cx", "cy", "r"];

    this.translate = function(dx, dy) {
        this.attr["cx"] += dx;
        this.attr["cy"] += dy;
    }

    this.scale = function(sx, sy) {
        if (sx === sy) {
            this.attr["cx"] *= sx;
            this.attr["cy"] *= sy;
            this.attr["r"] = sx >= 0 ? this.attr["r"] * sx : this.attr["r"] * -sx;
        } else {
            return false;
        }
    }
}

function SVG_Ellipse() {
    this.name = "ellipse";
    this.required_attributes = ["cx", "cy", "rx", "ry"];

    this.translate = function(dx, dy) {
        this.attr["cx"] += dx;
        this.attr["cy"] += dy;
    }

    this.scale = function(sx, sy) {
        this.attr["cx"] *= sx;
        this.attr["cy"] *= sy;

        if (sx >= 0) {
            this.attr["rx"] *= sx;
        } else {
            this.attr["rx"] *= -sx;
        }
        if (sy >= 0) {
            this.attr["ry"] *= sy;
        } else {
            this.attr["ry"] *= -sy;
        }
    }
}

function SVG_Rect() {
    this.name = "rect";
    this.required_attributes = ["x", "y", "width", "height"];

    this.translate = function(dx, dy) {
        this.attr["x"] += dx;
        this.attr["y"] += dy;
    }

    this.scale = function(sx, sy) {
        this.attr["x"] *= sx;
        this.attr["y"] *= sy;

        if (sx >= 0) {
            this.attr["width"] *= sx;
        } else {
            this.attr["width"] *= -sx;
            this.attr["x"] -= this.attr["width"]
        }
        if (sy >= 0) {
            this.attr["height"] *= sy;
        } else {
            this.attr["height"] *= -sy;
            this.attr["y"] -= this.attr["height"]
        }
    }
}

function SVG_Line() {
    this.name = "line";
    this.required_attributes = ["x1", "y1", "x2", "y2"];

    this.translate = function(dx, dy) {
        this.attr["x1"] += dx;
        this.attr["x2"] += dx;
        this.attr["y1"] += dy;
        this.attr["y2"] += dy;
    }

    this.scale = function(sx, sy) {
        this.attr["x1"] *= sx;
        this.attr["x2"] *= sx;
        this.attr["y1"] *= sy;
        this.attr["y2"] *= sy;
    }

    this.matrix = function(a, b, c, d, e, f) {
        var x = a * this.attr["x1"] + c * this.attr["y1"] + e;
        var y = b * this.attr["x1"] + d * this.attr["y1"] + f;
        this.attr["x1"] = x;
        this.attr["y1"] = y;

        var x = a * this.attr["x2"] + c * this.attr["y2"] + e;
        var y = b * this.attr["x2"] + d * this.attr["y2"] + f;
        this.attr["x2"] = x;
        this.attr["y2"] = y;
    }
}

function SVG_Polyline() {
    this.name = "polyline";
    this.required_attributes = ["points"];

    this.translate = function(dx, dy) {
        for (var i in this.coords){
            this.coords[i][0] += dx;
            this.coords[i][1] += dy;
        }
        this.attr["points"] = this.coords.join(" ");
    }

    this.scale = function(sx, sy) {
        for (var i in this.coords){
            this.coords[i][0] *= sx;
            this.coords[i][1] *= sy;
        }
        this.attr["points"] = this.coords.join(" ");
    }

    this.matrix = function(a, b, c, d, e, f) {
        for (var i in this.coords) {
            var x = a * this.coords[i][0] + c * this.coords[i][1] + e;
            var y = b * this.coords[i][0] + d * this.coords[i][1] + f;
            this.coords[i][0] = x;
            this.coords[i][1] = y;
        }
        this.attr["points"] = this.coords.join(" ");
    }
}

function SVG_Polygon() {
    this.name = "polygon";
}

function SVG_Path() {
    this.name = "path";
    this.required_attributes = ["d"];
    this.commands = [];
    this.implemented_scales = ['M', 'm', 'L', 'l', 'q', 'Q', 't', 'T', 'c', 'C', 's', 'S'];
    this.simple_translations = ['M', 'L', 'Q', 'T', 'C', 'S'];
    this.null_translations = ['m', 'l', 'h', 'v', 'q', 't', 'c', 's'];
    
    this.parseCoordinates = function(coord_string) {
        // Should simplify to remove multiple M, m, H, h, V or v coordinates
        // [Optional] Remove repeated commands e.g. "L x1 y1 L x2 y2" -> "L x1 y1 x2 y2"
    
        var re_commands = /([ACHLMQSTV])([-\+\d\.\s,e]*)(z)?/gi

        while(commands = re_commands.exec(coord_string)){
            var digits = extractDigits(commands[2]);
            var z = commands[3] ? "z" : "";
            digits.unshift(commands[1]);
            digits.push(z);
            this.commands.push(digits)
        }

        if (this.commands[0][0] === 'm') { this.commands[0][0] = 'M' };
        
        this.generatePathString();
    }

    this.translate = function(dx, dy) {
        for (var i in this.commands) {
            var command = this.commands[i];
            if ($.inArray(command[0], this.simple_translations) != -1) {
                for (var j=1; j<command.length-1; j+=2) {
                    command[j] += dx;
                    command[j+1] += dy;
                }
            } else if (command[0] === 'H') {
                for (var j=1; j<command.length-1; j++) {
                    command[j] += dx;
                }
            } else if (command[0] === 'V') {
                for (var j=1; j<command.length-1; j++) {
                    command[j] += dy;
                }
            } else if ($.inArray(command[0], this.null_translations) === -1) {
                return false;
            }
        }
        this.generatePathString();
    }

    this.scale = function(sx, sy) {        
        for (var i in this.commands) {
            var command = this.commands[i];
            if ($.inArray(command[0], this.implemented_scales) != -1) {
                for (var j=1; j<command.length-1; j+=2) {
                    command[j] *= sx;
                    command[j+1] *= sy;
                } 
            }
            else { return false; }
        }
        this.generatePathString();
    }

    this.generatePathString = function() {    
        var path_string = "";
        for (var i in this.commands) {
            path_string += this.commands[i][0]
            path_string += this.commands[i].slice(1).join(" ");
        }
        this.attr["d"] = path_string;
    }

}

SVG_shapes = {
    circle: SVG_Circle,
    ellipse: SVG_Ellipse,
    rect: SVG_Rect,
    line: SVG_Line,
    polyline: SVG_Polyline,
    polygon: SVG_Polygon,
    path: SVG_Path
};

for (var shape in SVG_shapes) {
    SVG_shapes[shape].prototype = new SVGElement();
}
SVG_Polygon.prototype = new SVG_Polyline;

var parseSVGString = function(svg_string) {
    // Given an SVG string, create DOM objects

    var svg = $(svg_string);

    for (var shape in SVG_shapes) {
        if (svg.filter(shape).length) {
            element = new SVG_shapes[shape]();
            element.extractAttributes(svg.filter(shape));
            return element;
        }
    }
}

var extractDigits = function(digit_string) {
    //Convert a string of digits to an array of floats
    
    if (!digit_string) {return;}
    
    var digit_strings = digit_string.split(/[\s,]+/);
    var digits = [];
    
    for (var i=0 in digit_strings) {
        if (digit_strings[i]) {
            digits.push(parseFloat(digit_strings[i]));
        }
    }
    
    return digits;
}

var parseTransformString = function(transform_string) {
    // Parse a string to extract any transformations and return
    // functions that call the relevant method of a passed object.

    var re_digits = /([-+]?\d*\.?\d+)/g;
    var re_translate = /translate\s*\(([-\+\d\.\s,e]+)\)/i;
    var re_scale = /scale\s*\(([-\+\d\.\s,e]+)\)/i;
    var re_matrix = /matrix\s*\(([-\+\d\.\s,e]+)\)/i;

    if (translate_digits = re_translate.exec(transform_string)) {
        var digits = extractDigits(translate_digits[1]);
        if (digits.length > 0) {
            return function(element) {
                return element.translate(digits[0], digits[1] ? digits[1] : 0);
            }
        }
    }

    if (scale_digits = re_scale.exec(transform_string)) {
        var digits = extractDigits(scale_digits[1]);
        if (digits.length > 0) {
            return function(element) {
                return element.scale(digits[0], digits[1] ? digits[1] : digits[0]);
            }
        }
    }

    if (matrix_digits = re_matrix.exec(transform_string)) {
        var digits = extractDigits(matrix_digits[1]);
        if (digits.length === 6) {
            return function(element) {
                return element.matrix(digits[0], digits[1], digits[2], digits[3], digits[4], digits[5]);
            }
        }
    }

};

var applyTransform = function() {
    $('#error-message').html("");
    
    var element = parseSVGString($("#input-svg").val());
    if (!element) {
        $('#error-message').html("Unable to find any valid SVG elements");
        return;
    }

    var transformation = parseTransformString($("#input-transformation").val());
    if (!transformation) {
        $('#error-message').html("Unable to parse transformation");
        return;
    }

    var transformed = transformation(element);
    if (transformed === false) {
        $('#error-message').html("That transformation is not implemented for this element");
        return;
    }

    $("#output-svg").text(element.write());
};

var addExampleElement = function(element_name){
    var element = SVG_elements[element_name];
    $("#input-svg").val(element);
}

var addExampleTransformation = function(element_name){
    var transformation = test_transformations[element_name];
    $("#input-transformation").val(transformation);
}

$(document).ready(function() {
    $("#apply-button").on("click", function(event){
        applyTransform();
    });
    $("#run-tests-button").on("click", function(event){
        runTests();
    });
});
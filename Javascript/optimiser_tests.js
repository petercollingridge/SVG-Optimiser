function TransformTester() {
    // Object to convert transformations into strings so they can be easily tested.
    this.transform_str = "undefined";

    this.translate = function(dx, dy) {
        this.transform_str = "translate(" + dx + " " + dy + ")";
    }

    this.scale = function(sx, sy) {
    	this.transform_str = "scale(" + sx + " " + sy + ")";
    }

    this.matrix = function(a, b, c, d, e, f) {
    	this.transform_str = "matrix(" + a + " " + b + " " + c +" " + d +" " + e +" " + f + ")";
    }
}

var transformation_parse_tests = [
	['none', ''],
	['translate(twelve)', ''],
	['translate(one 2)', ''],
	['translate(12)', 'translate(12 0)'],
	['translate(  12)', 'translate(12 0)'],
	['translate(12	)', 'translate(12 0)'],
	['translate( 12 )', 'translate(12 0)'],
	['translate ( 12 ) ', 'translate(12 0)'],
	['translate(12 34)', 'translate(12 34)'],
	['translate(12 	34 )', 'translate(12 34)'],
	['translate(12,34)', 'translate(12 34)'],
	['translate(12, 34)', 'translate(12 34)'],
	['translate(12 ,34)', 'translate(12 34)'],
	['translate( 12 , 34 )', 'translate(12 34)'],
	['translate( -12 )', 'translate(-12 0)'],
	['translate( +12.0 )', 'translate(12 0)'],
	['translate( 12.0 )', 'translate(12 0)'],
	['translate( 12. )', 'translate(12 0)'],
	['translate( 12.2 )', 'translate(12.2 0)'],
	['translate( 12.02 )', 'translate(12.02 0)'],
	['translate( -12.002 )', 'translate(-12.002 0)'],
	['translate( .002 )', 'translate(0.002 0)'],
	['translate( -.002 )', 'translate(-0.002 0)'],
	['translate( -.002 0.03 )', 'translate(-0.002 0.03)'],
	['translate( -9.9e-1 )', 'translate(-0.99 0)'],
	['scale( 0.2 )', 'scale(0.2 0.2)'],
	['scale( 0.2 -1.2 )', 'scale(0.2 -1.2)'],
	['scale( -10.2, 1.2 )', 'scale(-10.2 1.2)'],
	['matrix( 1.5 -2 3 0.4 -5.5 6 7.6)', ''],
	['matrix( 1.5 -2 3 0.4 -5.5 6 )', 'matrix(1.5 -2 3 0.4 -5.5 6)'],
	['matrix( 1.1  -2.2 -3.3 , 4.4, -5.5 6 )', 'matrix(1.1 -2.2 -3.3 4.4 -5.5 6)'],
];

var test_transformations = {
	'null transform' : 'nonsense string',
	'1D translate' : 'translate(-12.5)',
	'2D translate' : 'translate(12.5 -4)',
	'1D scale' : 'scale(-1.5)',
	'2D scale' : 'scale(1.5 -2)',
	'translate matrix': 'matrix(1 0 0 1 12.5 -4)',
	'scale matrix': 'matrix(1.5 0 0 -2 0 0)',
	'translate and scale matrix': 'matrix(1.5 0 0 -2 12.5 -4)',
	'matrix transformation': 'matrix(1.5 -2 3 0.4 -5.5 6)'
};

var SVG_elements = {
	rect: '<rect x="10" y="20" width="15" height="25"/>',
	rounded_rect: '<rect x="10" y="20" rx="2" ry="3" width="15" height="25"/>',
	circle: '<circle cx="10" cy="20" r="3"/>',
	ellipse: '<ellipse cx="10" cy="20" rx="4" ry="5"/>',
	line: '<line x1="10" y1="20" x2="15" y2="35"/>',
	polyline: '<polyline points="10,20 25,35 5,35"/>',
	polygon: '<polygon points="10,20 25,35 5,35"/>',
	messy_polyline: '<polyline points="120.0 11.1 145 55.51   95 55.5 -3.0, 2  3 , 3"/>',
	path_ML: '<path d="M10.0,-20.0 L-25.00 -30.05 -30.000,-25.000 L6 -3z"/>',
	path_MLl: '<path d="M-0.5 10.5 L19.5 10.5 L35.5 26.5 19.5 42.5 l-20 0 -16 -16z"/>',
	path_HhVv: '<path d="M-0.5 10.5 H19.5 V15.5 h20 v6.5"/>',
	path_QqTt: '<path d="M-10.5 50.5 q20 -25 20 25 t40 0 40.1 5 Q20.5 100 40 139.9 160 160 80 190" />',
	path_CcSs: '<path d="M-10.5 50.5 c20 -25 20 25 40 -25.5 s40 0 40.1 5 S20.5 100 40 139.9 160 160 80 190" />',
	xml_style: '<circle cx="10" cy="20" r="3"></circle>',
	with_style: '<circle cx="10" cy="20" r="3" style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.5;"/>',
	missing_attributes: '<circle cx="10" r="5"/>',
	no_attributes: '<circle/>',
	additional_attributes: '<circle class="circle" id="eye" cx="10" cy="20" r="3"/>',
	namespaced_attribute: '<circle inkscape:label="Circle 1" cx="10" cy="20" r="3"/>'
};

var test_cases = [
	['null transform', 'rect', 'null'],
	['null transform', 'circle', 'null'],
	['null transform', 'ellipse', 'null'],
	['null transform', 'line', 'null'],
	['null transform', 'polyline', 'null'],
	['null transform', 'polygon', 'null'],
	['null transform', 'path_ML', 'null'],
	['1D translate', 'rect', {x: -2.5, y: 20, width: 15, height: 25}],
	['1D translate', 'circle', {cx: -2.5, cy: 20, r: 3}],
	['1D translate', 'ellipse', {cx: -2.5, cy: 20, rx: 4, ry: 5}],
	['1D translate', 'line', {x1: -2.5, y1: 20, x2: 2.5, y2: 35}],
	['1D translate', 'polyline', {points: "-2.5,20 12.5,35 -7.5,35"}],
	['1D translate', 'polygon', {points: "-2.5,20 12.5,35 -7.5,35"}],
	['1D translate', 'path_ML', {d: "M-2.5 -20 L-37.5 -30.05 -42.5 -25 L-6.5 -3 z"}],
	['2D translate', 'rect', {x: 22.5, y: 16, width: 15, height: 25}],
	['2D translate', 'circle', {cx: 22.5, cy: 16, r: 3}],
	['2D translate', 'ellipse', {cx: 22.5, cy: 16, rx: 4, ry: 5}],
	['2D translate', 'line', {x1: 22.5, y1: 16, x2: 27.5, y2: 31}],
	['2D translate', 'polyline', {points: "22.5,16 37.5,31 17.5,31"}],
	['2D translate', 'polygon', {points: "22.5,16 37.5,31 17.5,31"}],
	['2D translate', 'path_ML', {d: "M22.5 -24 L-12.5 -34.05 -17.5 -29 L18.5 -7 z"}],
	['1D scale', 'rect', {x: -37.5, y: -67.5, width: 22.5, height: 37.5}],
	['1D scale', 'circle', {cx: -15, cy: -30, r: 4.5}],
	['1D scale', 'ellipse', {cx: -15, cy: -30, rx: 6, ry: 7.5}],
	['1D scale', 'line', {x1: -15, y1: -30, x2: -22.5, y2: -52.5}],
	['1D scale', 'polyline', {points: "-15,-30 -37.5,-52.5 -7.5,-52.5"}],
	['1D scale', 'polygon', {points: "-15,-30 -37.5,-52.5 -7.5,-52.5"}],
	['2D scale', 'rect', {x: 15, y: -90, width: 22.5, height: 50}],
	['2D scale', 'circle', 'null'],
	['2D scale', 'ellipse', {cx: 15, cy: -40, rx: 6, ry: 10}],
	['2D scale', 'line', {x1: 15, y1: -40, x2: 22.5, y2: -70}],
	['2D scale', 'polyline', {points: "15,-40 37.5,-70 7.5,-70"}],
	['2D scale', 'polygon', {points: "15,-40 37.5,-70 7.5,-70"}],
	['translate matrix', 'rect', {x: 22.5, y: 16, width: 15, height: 25}],
	['translate matrix', 'circle', {cx: 22.5, cy: 16, r: 3}],
	['translate matrix', 'ellipse', {cx: 22.5, cy: 16, rx: 4, ry: 5}],
	['translate matrix', 'line', {x1: 22.5, y1: 16, x2: 27.5, y2: 31}],
	['translate matrix', 'polyline', {points: "22.5,16 37.5,31 17.5,31"}],
	['translate matrix', 'polygon', {points: "22.5,16 37.5,31 17.5,31"}],
	['scale matrix', 'rect', {x: 15, y: -90, width: 22.5, height: 50}],
	['scale matrix', 'circle', 'null'],	
	['scale matrix', 'ellipse', {cx: 15, cy: -40, rx: 6, ry: 10}],
	['scale matrix', 'line', {x1: 15, y1: -40, x2: 22.5, y2: -70}],
	['scale matrix', 'polyline', {points: "15,-40 37.5,-70 7.5,-70"}],
	['scale matrix', 'polygon', {points: "15,-40 37.5,-70 7.5,-70"}],
	['translate and scale matrix', 'rect', {x: 27.5, y: -94, width: 22.5, height: 50}],
	['translate and scale matrix', 'circle', {cx: 22.5, cy: 16, r: 3}],					// Doesn't scale anything
	['translate and scale matrix', 'ellipse', {cx: 27.5, cy: -44, rx: 6, ry: 10}],
	['translate and scale matrix', 'line', {x1: 27.5, y1: -44, x2: 35, y2: -74}],
	['translate and scale matrix', 'polyline', {points: "27.5,-44 50,-74 20,-74"}],
	['translate and scale matrix', 'polygon', {points: "27.5,-44 50,-74 20,-74"}],
	['matrix transformation', 'rect', 'null'],
	['matrix transformation', 'circle', 'null'],
	['matrix transformation', 'ellipse', 'null'],
	['matrix transformation', 'line', {x1: 69.5, y1: -6, x2: 122, y2: -10}],
	['matrix transformation', 'polyline', {points: "69.5,-6 137,-30 107,10"}],
	['matrix transformation', 'polygon', {points: "69.5,-6 137,-30 107,10"}],
];

var testElementParsing = function() {
	// Test ability to parse SVG elements
	// Read then write SVG string and test whether the input and output are the same

	console.log("Test element parsing");
	for (var element in SVG_elements) {
		var SVG_string = SVG_elements[element]
		var element_object = parseSVGString(SVG_string);

		if (!element_object) {
			console.log (" - failed to parse " + element);
		} else {
			if (element_object[0].write() != SVG_string){
				console.log (" - " + SVG_string + " parsed as " + element_object[0].write());
			}
		}
	}
}

var testTransformationParsing = function() {
	// Test ability to parse transformations

    console.log("Test transformation parsing");
	var transform_tester = new TransformTester();
    var passed_count = transformation_parse_tests.length;

	for (var t in transformation_parse_tests) {
		var transform = transformation_parse_tests[t][0];
		var result = transformation_parse_tests[t][1];
		var transform_function = parseTransformString(transform);

		if (transform_function) {
			transform_function(transform_tester);
			if (transform_tester.transform_str != result) {
				console.log(" - " + transform + " parsed as " + transform_tester.transform_str);
                passed_count--;
			}
		} else {
            if (result) {
                console.log(" - failed to parse " + transform);
                passed_count--;
            }
		}
	}
    console.log(" * Passed " + passed_count + " of " + transformation_parse_tests.length);
}

var testTransformations = function() {
	// Test running transformations on elements

    console.log("Test transformations");
	var passed_count = 0;

	for (var t in test_cases) {
		var transformation_str = test_transformations[test_cases[t][0]];
		var element_string = SVG_elements[test_cases[t][1]]
        
		var transformation = parseTransformString(transformation_str);
		var element = parseSVGString(element_string)[0];
        
        var expected_result = test_cases[t][2];
        var transformation_results = false;
		
        if (transformation) { transformation_results = transformation(element); }
        
        if (expected_result === 'null' || transformation_results != false && element.compareAttributes(expected_result)) {
            passed_count++;
        } else {
            console.log(" - " + test_cases[t][0] + " " + test_cases[t][1] + " failed");
            console.log(element)
        }
    }
    console.log(" * Passed " + passed_count + " of " + test_cases.length);
}

var runTests = function() {
	testElementParsing();
	testTransformationParsing();
	testTransformations();
}
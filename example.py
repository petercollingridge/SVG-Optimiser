from cleanSVG import CleanSVG
import os

input_file = os.path.join("examples", "paths_test.svg")
output_file = "cleaned-test.svg"

svg = CleanSVG(input_file)
svg.removeAttribute('id')
svg.setDecimalPlaces(1)
svg.extractStyles()
svg.applyTransforms()
svg.write(output_file)
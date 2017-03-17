from cleanSVG import CleanSVG
import os

input_file = os.path.join("examples", "paths_test.svg")
output_file = "cleaned-test.svg"

svg = CleanSVG(input_file)
svg.removeAttribute('id')
svg.setDecimalPlaces(1)
svg.extractStyles()
svg.removeElement('title')
svg.removeElement('desc')
svg.removeElement('defs')
svg.removeComments()
svg.applyTransforms()
svg.write(output_file)
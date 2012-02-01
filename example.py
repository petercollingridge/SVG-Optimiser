from cleanSVG import CleanSVG

input_file = "test.svg"
output_file = "cleaned-test.svg"

svg = CleanSVG(input_file)
svg.removeAttributes('id')
svg.setDecimalPlaces(1)
svg.extractStyles()
svg.applyTransforms()
svg.write(output_file)

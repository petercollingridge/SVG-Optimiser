from cleanSVG import CleanSVG
import os

input_file = os.path.join("examples", "paths_test.svg")
output_file = "cleaned-test.svg"

svg = CleanSVG(input_file)
svg.remove_attribute('id')
svg.set_decimal_places(1)
svg.extract_styles()
svg.apply_transforms()
svg.write(output_file)

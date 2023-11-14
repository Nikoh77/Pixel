# Specific instruction for Nuitka compiler

from nuitka.OptionParsing import parseOptions
from nuitka import main

options = parseOptions

# Add any specific options needed here.

options.generateOnefile = False
options.createPlugin = True
options.standalone = False

options.output_dir = "dist"
options.entry_point = 'pixel.py'  # Replace with your main script

# Example of specifying external dependencies not in the standard library
# options.add_module('name_of_your_external_module')

# options.extra_modules = []
    # Add any other external modules or packages here

# Add any other necessary options for your project here

main(options)

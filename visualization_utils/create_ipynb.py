import nbformat as nbf

nb = nbf.v4.new_notebook()
text = """\
## Algorithm vizualization."""

code = """\
%pylab inline
# setting up
%load_ext autoreload
%autoreload 2

# imports
from visualization_utils.animate_list import animate_list
from visualization_utils.graph import Graph, Arc, Node
from models.fa import FiniteAutomaton
"""

nb['cells'] = [nbf.v4.new_markdown_cell(text),
               nbf.v4.new_code_cell(code)]
fname = 'test.ipynb'

with open(fname, 'w') as f:
    nbf.write(nb, f)

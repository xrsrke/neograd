from .autograd import tensor, new_graph, no_track
from .autograd import add, sub, mul, div, pow, exp, log, dot, sum, transpose
from .autograd.graph import Graph


global _NG_GRAPH
_NG_GRAPH = Graph()
'''
  _NG_GRAPH is the global graph object used to construct backprop graphs
'''
"""
"""
import py
from rpython.rlib.parsing.tree import RPythonVisitor
from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rio import rio_dir

grammar = py.path.local(rio_dir).join('grammar.txt').read("rt")
regexs, rules, ToAST = parse_ebnf(grammar)
_parse = make_parse_function(regexs, rules, eof=True)


class Node(object):
    """ A node on the Abstract Syntax Tree
    """
    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

class Block(Node):
    """ A list of statements
    """
    def __init__(self, exprs):
        self.exprs = exprs

class Expr(Node):
    """ A message chain.
    """
    def __init__(self, msgs):
        self.msgs = msgs

class Message(Node):
    """ Represent a message send.
    """
    def __init__(self, head, tail=None):
        self.head = head
        self.tail = tail

class ConstantInt(Node):
    """ Represent a constant - integer type
    """
    def __init__(self, intval):
        self.intval = intval

class Identifier(Node):
    """ A variable reference.
    """
    def __init__(self, varname):
        self.varname = varname

class Transformer(RPythonVisitor):
    """ Transforms AST from the obscure format given to us by the ebnfparser
    to something easier to work with
    """
    def visit_main(self, node):
        # a program is a single block of code
        return self.dispatch(node.children[0])

    def visit_block(self, node):
        # a block is built of multiple expressions
        return Block([self.dispatch(exprnode)
                      for exprnode in node.children])

    def visit_expr(self, node):
        # every expression is a message chain
        return Expr([self.dispatch(child)
                     for child in node.children])

    def visit_message(self, node):
        # a message (fragment) is a symbol and maybe some args
        child = node.children[0].children[0]
        return Message(ConstantInt(child.additional_info))

transformer = Transformer()
def parse(source):
    """ Parse the source code and produce an AST
    """
    return transformer.dispatch(_parse(source))

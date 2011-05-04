## {{{ http://code.activestate.com/recipes/577540/ (r2)
"""
Binary Search Tree: A sorted collection of values that supports
efficient insertion, deletion, and minimum/maximum value finding.
"""
# Copyright (C) 2008 by Edward Loper
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# IMPLEMENTATION NOTES:
#
# Internally, we represent tree nodes using Python lists.  These lists
# may either be empty (for empty nodes) or may have length four (for
# non-empty nodes).  The non-empty nodes contain:
#
#     [left_child, right_child, value, sort_key]
#
# Using lists rather than a node class more than doubles the overall
# performance in the benchmarks that I have run.
#
# The sort key is always accessed as node[-1].  This allows us to
# optimize the case where the sort key is identical to the value, by
# encoding such nodes as simply:
#
#     [left_child, right_child, value]
#
# The following constants are used to access the pieces of each search
# node.  If the constant-binding optimization recipe (which can be
# downloaded from <http://code.activestate.com/recipes/277940/>) is
# available, then it is used to replace these constants at
# import-time, increasing the binary search tree efficiency by 3-5%.
_LEFT = 'left'
_RIGHT = 'right'

class Node(object):
    '''The BST node structure. It uses slots t keep the memory usage same or
    better than a list. The sort_key is a lazy evaluated property.
    '''
    __slots__ = ('right', 'left', 'value', '_sort_key')
    def __init__(self, value, sort_key = None, right = None, left = None):
        self.value = value
        if sort_key is not None:
            self._sort_key = sort_key
        self.right = right
        self.left = left
    @property
    def sort_key(self):
        ''' Property method, returns sort_key if it exists, else
        returns the value.'''
        if hasattr(self, '_sort_key'):
            return self._sort_key
        return self.value
    
class BinarySearchTree(object):
    """
    A sorted collection of values that supports efficient insertion,
    deletion, and minimum/maximum value finding.  Values may sorted
    either based on their own value, or based on a key value whose
    value is computed by a key function (specified as an argument to
    the constructor).

    BinarySearchTree allows duplicates -- i.e., a BinarySearchTree may
    contain multiple values that are equal to one another (or multiple
    values with the same key).  The ordering of equal values, or
    values with equal keys, is undefined.
    """
    def __init__(self, values = None, sort_key=None):
        """
        Create a new empty BST.  If a sort key is specified, then it
        will be used to define the sort order for the BST.  If an
        explicit sort key is not specified, then each value is
        considered its own sort key.
        """
        self._root = None
        self._sort_key = sort_key
        self._len = 0
        if len(values):
            for elem in values:
                self.insert(elem)

    #/////////////////////////////////////////////////////////////////
    # Public Methods
    #/////////////////////////////////////////////////////////////////
        
    def insert(self, value):
        """
        Insert the specified value into the BST.
        """
        
        # Get the sort key for this value.
        if self._sort_key is None:
            new_node = Node(value)
        else:
            new_node = Node(value, self._sort_key(value))
        # Walk down the tree until we find an empty node.
        if self._root is None:
            self._root = new_node
        node = self._root
        while node is not new_node:
            if new_node.sort_key < node.sort_key:
                if node.left is None:
                    node.left = new_node
                node = node.left
            else:
                if node.right is None:
                    node.right = new_node
                node = node.right
        self._len += 1
        
    def minimum(self):
        """
        Return the value with the minimum sort key.  If multiple
        values have the same (minimum) sort key, then it is undefined
        which one will be returned.
        """
        return self._extreme_node(_LEFT).value
    
    def maximum(self):
        """
        Return the value with the maximum sort key.  If multiple values
        have the same (maximum) sort key, then it is undefined which one
        will be returned.
        """
        return self._extreme_node(_RIGHT).value

    def find(self, sort_key):
        """
        Find a value with the given sort key, and return it.  If no such
        value is found, then raise a KeyError.
        """
        return self._find(sort_key).value
    
    def pop_min(self):
        """
        Return the value with the minimum sort key, and remove that value
        from the BST.  If multiple values have the same (minimum) sort key,
        then it is undefined which one will be returned.
        """
        return self._pop_node(self._extreme_node(_LEFT))
    
    def pop_max(self):
        """
        Return the value with the maximum sort key, and remove that value
        from the BST.  If multiple values have the same (maximum) sort key,
        then it is undefined which one will be returned.
        """
        return self._pop_node(self._extreme_node(_RIGHT))

    def pop(self, sort_key):
        """
        Find a value with the given sort key, remove it from the BST, and
        return it.  If multiple values have the same sort key, then it is
        undefined which one will be returned.  If no value has the
        specified sort key, then raise a KeyError.
        """
        return self._pop_node(self._find(sort_key))

    def values(self, reverse=False):
        """Generate the values in this BST in sorted order."""
        if reverse:
            return self._iter(_RIGHT, _LEFT)
        else:
            return self._iter(_LEFT, _RIGHT)
    __iter__ = values

    def __len__(self):
        """Return the number of items in this BST"""
        return self._len

    def __nonzero__(self):
        """Return true if this BST is not empty"""
        return self._len > 0

    def __repr__(self):
        return '<BST: (%s)>' % ', '.join('%r' % v for v in self)

    def __str__(self):
        return self.pprint()

    def pprint(self, max_depth=10, frame=True, show_key=True):
        """
        Return a pretty-printed string representation of this binary
        search tree.
        """
        top, mid, bot = self._pprint(self._root, max_depth, show_key)
        lines = top + [mid] + bot
        if frame:
            width = max(40, max(len(line) for line in lines))
            sout = '+-'+'MIN'.rjust(width, '-')+'-+\n'
            sout += ''.join('| %s |\n' % line.ljust(width) for line in lines)
            sout += '+-'+'MAX'.rjust(width, '-')+'-+\n'
            return sout
        else:
            return '\n'.join(lines)

    #/////////////////////////////////////////////////////////////////
    # Private Helper Methods
    #/////////////////////////////////////////////////////////////////
        
    def _extreme_node(self, side):
        """
        Return the leaf node found by descending the given side of the
        BST (either _LEFT or _RIGHT).
        """
        if self._root is None:
            raise IndexError('Empty Binary Search Tree!')
        node = self._root
        # Walk down the specified side of the tree.
        while getattr(node, side) is not None:
            node = getattr(node, side)
        return node

    def _find(self, sort_key):
        """
        Return a node with the given sort key, or raise KeyError if not found.
        """
        node = self._root
        while node:
            node_key = node.sort_key
            if sort_key < node_key:
                node = node.left
            elif sort_key > node_key:
                node = node.right
            else:
                return node
        raise KeyError("Key %r not found in BST" % sort_key)

    def _pop_node(self, node):
        """
        Delete the given node, and return its value.
        """
        value = node.value
        if node.left:
            if node.right:
                # This node has a left child and a right child; find
                # the node's successor, and replace the node's value
                # with its successor's value.  Then replace the
                # sucessor with its right child (the sucessor is
                # guaranteed not to have a left child).  Note: node
                # and successor may not be the same length (3 vs 4)
                # because of the key-equal-to-value optimization; so
                # we have to be a little careful here.
                successor = node.right
                while successor.left:
                    successor = successor.left
                node.value = successor.value
                node.sort_key = successor.sort_key
                successor = successor.right
            else:
                # This node has a left child only; replace it with
                # that child.
                node = node.left
        else:
            if node.right:
                # This node has a right child only; replace it with
                # that child.
                node = node.right
            else:
                # This node has no children; make it empty.
                del node
        self._len -= 1
        return value

    def _iter(self, pre, post):
        '''Helper for sorted iterators.
            - If (pre,post) = (_LEFT,_RIGHT), then this will generate items
              in sorted order.
            - If (pre,post) = (_RIGHT,_LEFT), then this will generate items
              in reverse-sorted order.
          We use an iterative implemenation (rather than the recursive one)
          for efficiency.
        '''
        stack = []
        node = self._root
        while stack or node:
            if node: # descending the tree
                stack.append(node)
                node = getattr(node, pre)
            else: # ascending the tree
                node = stack.pop()
                yield node.value
                node = getattr(node, post)

    def _pprint(self, node, max_depth, show_key, spacer=2):
        """
        Returns a (top_lines, mid_line, bot_lines) tuple,
        """
        if max_depth == 0:
            return ([], '- ...', [])
        elif not node:
            return ([], '- EMPTY', [])
        else:
            top_lines = []
            bot_lines = []
            mid_line = '-%r' % node.value
            if len(node) > 3:
                mid_line += ' (key=%r)' % node.sort_key
            if node.left:
                top, mid, bot = self._pprint(node.left, max_depth-1,
                                     show_key, spacer)
                indent = ' '*(len(bot)+spacer)
                top_lines += [indent+' '+line for line in top]
                top_lines.append(indent+'/'+mid)
                top_lines += [' '*(len(bot)-i+spacer-1)+'/'+' '*(i+1)+line
                              for (i, line) in enumerate(bot)]
            if node.right:
                top, mid, bot = self._pprint(node.right, max_depth-1,
                                     show_key, spacer)
                indent = ' '*(len(top)+spacer)
                bot_lines += [' '*(i+spacer) + '\\' + ' ' * (len(top)-i) + line
                              for (i, line) in enumerate(top)]
                bot_lines.append(indent+'\\'+mid)
                bot_lines += [indent+' '+line for line in bot]
            return (top_lines, mid_line, bot_lines)

try:
    # Try to use the python recipe:
    # <http://code.activestate.com/recipes/277940/>
    # This will only work if that recipe has been saved a
    # "optimize_constants.py".
    from optimize_constants import bind_all
    bind_all(BinarySearchTree)
except ImportError:
    pass
## end of http://code.activestate.com/recipes/577540/ }}}


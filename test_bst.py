''' Test the binary search tree '''
from binarysearchtree import BinarySearchTree, Node
import unittest

class TestBST(unittest.TestCase):
    '''Runs the simple examples from the activate state recipe.'''
    names = 'bob joe Jane jack Mary sue Ed Zoey ann'.split()
    def setUp(self):
        self.bst = BinarySearchTree(self.names, str.upper)
    def test_insert(self):
        self.assertEquals(self.bst.minimum(), 'ann')
    def test_minimum(self):
        self.assertEquals(self.bst.maximum(), 'Zoey')
    def test_values(self):
        expected_list = ['ann', 'bob', 'Ed', 'jack', 'Jane', 'joe', 'Mary', 'sue', 'Zoey']
        for expected, result in zip(expected_list, self.bst.values()): 
            self.assertEquals(expected, result)
    def test_values_reversed(self):
        expected_list = ['Zoey', 'sue', 'Mary', 'joe', 'Jane', 'jack', 'Ed', 'bob', 'ann']
        for expected, result in zip(expected_list, self.bst.values(True)): 
            self.assertEquals(expected, result)

if __name__ == '__main__':
    unittest.main()

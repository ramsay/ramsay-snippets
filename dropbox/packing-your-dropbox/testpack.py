import unittest
from packurbox import DropBox, DropNode, pack, packtree, prettytree, fit

class DropBoxOfficial(unittest.TestCase):
    values = [(8,8), (4,3), (3, 4)]
    output = 88

    def setUp(self):
        self.boxes = []
        for b in self.values:
            db = DropBox()
            db.w, db.h = b
            self.boxes.append(db)

    #def testPack(self):
    #    """Test the official dropbox input/output"""
    #    self.assertEqual(self.output, pack(self.boxes))

    def testPacktree(self):
        tree = packtree(None, self.boxes)
        prettytree(tree)
        self.assertEqual(self.output, tree.width()*tree.height())

class SanityTest(DropBoxOfficial):
    values = [(100,100)]
    output = 10000

class TestSecondColumn(DropBoxOfficial):
    values = [(8,8), (4, 3), (3, 4), (1, 1), (1, 1), (1, 1)]
    output = 96

class TestFlipForOptimal(DropBoxOfficial):
    '''This test requires flipping the tail box.'''
    values = [(3,1), (2,2), (1,2)]
    output = 9

class TestFlipRoot(DropBoxOfficial):
    '''This test requires flipping the root box.'''
    values = [(2,3), (2,1)]
    output = 8

if __name__ == '__main__':
    unittest.main()

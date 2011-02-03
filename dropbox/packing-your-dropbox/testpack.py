import unittest
from packurbox import DropBox, pack, fit

class DropBoxOfficial(unittest.TestCase):
    values = [(8,8), (4,3), (3, 4)]
    output = 88
    def testPack(self):
        """Test the official dropbox input/output"""
        boxes = []
        for b in self.values:
            db = DropBox()
            db.w, db.h = b
            boxes.append(db)

        self.assertEqual(self.output, pack(boxes))

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

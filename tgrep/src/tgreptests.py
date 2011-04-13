'''
Created on Feb 12, 2011

@author: Robert Ramsay
'''
import unittest
from tgrep import LogHandler, make_datetime, approximate_year

class TestApproximateTime(unittest.TestCase):
    def test2011(self):
        y = approximate_year('homo.log')
        self.assertEqual(y,2011)
    
class TestMakedatetime(unittest.TestCase):
    def testFull(self):
        dti = make_datetime("Feb  9 06:52:00")
        self.assertEqual(2, dti.month)
        self.assertEqual(9, dti.day)
        self.assertEqual(6, dti.hour)
        self.assertEqual(52, dti.minute)
        self.assertEqual(0, dti.second)
    def testLeft(self):
        dti = make_datetime("Feb  9 06:", True)
        self.assertEqual(2, dti.month)
        self.assertEqual(9, dti.day)
        self.assertEqual(0, dti.hour)
        self.assertEqual(0, dti.minute)
        self.assertEqual(0, dti.second)
    def testRight(self):
        dti = make_datetime("Feb  9 06:", False)
        self.assertEqual(2, dti.month)
        self.assertEqual(9, dti.day)
        self.assertEqual(24, dti.hour)
        self.assertEqual(60, dti.minute)
        self.assertEqual(60, dti.second)

class TestLogHandler(unittest.TestCase):
    lh = None
    
    def setUp(self):
        self.lh = LogHandler('test.log')
    
    def testLogHandlerInit(self):
        self.assertTrue(self.lh.bytes>0)
        self.assertTrue(self.lh.first is not None)
        self.assertTrue(self.lh.last is not None)
        
        first = "Feb  9 06:52:00"
        last = "Feb 10 06:23:46"
        self.assertEqual(make_datetime(first), self.lh.first)
        self.assertEqual(make_datetime(last), self.lh.last)
    
    def testSingleFirst(self):
        param = 'Feb 9 06:52:00'
        date = make_datetime(param)
        self.assertEqual(0, self.lh.get_offset(date))
    
    def testSingleLastRightside(self):
        param = 'Feb 10 06:23:46'
        date = make_datetime(param)
        self.assertEqual(1350, self.lh.get_offset(date,False))    
    
    def testSingleMiddle(self):
        param = 'Feb 9 16:36:41'
        date = make_datetime(param)
        self.assertEqual(560, self.lh.get_offset(date))
            
    def testSingleMiddle2(self):
        param = 'Feb  9 18:35:15 '
        date = make_datetime(param)
        self.assertEqual(674, self.lh.get_offset(date))

class TestHomogeneus(unittest.TestCase):
    '''Tests in the cases where we have a homogeneous block.'''
    lh = None
    
    def setUp(self):
        '''Initializes the LogHandler'''
        self.lh = LogHandler('homo.log')
    
    def testRightSide(self):
        '''Test finding the right edge of a homgeneous block.'''
        param = 'Feb  9 07:50:27'
        date = make_datetime(param)
        self.assertEqual(210, self.lh.get_offset(date, False))
    
    def testLeftSide(self):
        '''Test finding the left edge of a homogeneous block.'''
        param = 'Feb  9 07:50:27'
        date = make_datetime(param)
        self.assertEqual(68, self.lh.get_offset(date))

if __name__ == "__main__":
    unittest.main()
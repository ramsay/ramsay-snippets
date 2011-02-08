import unittest
from dropbox_diet import diet
from dropbox_diet import max_activities, min_activities, sum_activities

class DropBox(unittest.TestCase):
    def testNoSolution(self):
        activities = {'red-bull': 140, 'coke': 110}
        output = ['no solution']
        
        self.assertEqual(output, diet(activities))
    
    def testGiven(self):
        activities = {'free-lunch': 802, 'mixed-nuts': 421, 'orange-juice': 143,
                      'heavy-ddr-session': -302, 'cheese-snacks': 137, 'cookies': 316,
                      'mexican-coke': 150, 'dropballers-basketball': -611, 'coding-six-hours': -466,
                      'riding-scooter': -42, 'rock-bank': -195, 'playing-drums': -295}
        output = ['coding-six-hours','cookies','mexican-coke']
        
        self.assertEqual(output, diet(activities))
    
    def testOneToOne(self):
        activities = {'apple':100, 'walk-a-lap':-100}
        output = ['apple', 'walk-a-lap']
        
        self.assertEqual(output, diet(activities))

class DietUtilitiesTest(unittest.TestCase):
    '''Tests for the utility functions for my upgrade to functional syntax.'''
    activities = []
    minimum = 0
    maximum = 0
    summation = 0
    
    def testMax(self):
        self.assertEqual(self.maximum,max_activities(self.activities)[1])
    def testMin(self):
        self.assertEqual(self.minimum,min_activities(self.activities)[1])
    def testSum(self):
        self.assertEqual(self.summation,sum_activities(self.activities))
    
class DietUtilitiesOne(DietUtilitiesTest):
    '''Test utilities with a list of one.'''
    activities = [('none', 100)]
    minimum = 100
    maximum = 100
    summation = 100
    
class DietUtilitiesThree(DietUtilitiesTest):
    '''Test utilities with a list of one.'''
    activities = [('abe', 10),('abe', 20),('abe', 30)]
    minimum = 10
    maximum = 30
    summation = 60
        
class DietUtilitiesNegative(DietUtilitiesTest):
    '''Test utilities with a list of negative numbers.'''
    activities = [('a', -1),('a', -2),('a', -3)]
    minimum = -3
    maximum = -1
    summation = -6
        
class DietUtilitiesZeroSum(DietUtilitiesTest):
    '''Test utilities with a list that sums to zero.'''
    activities = [('a',-50),('b',-50),('c',100)]
    minimum = -50
    maximum = 100
    summation = 0
        
if __name__ == '__main__':
    unittest.main()
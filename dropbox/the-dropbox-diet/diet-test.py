import unittest
from dropbox_diet import diet

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

if __name__ == '__main__':
    unittest.main()
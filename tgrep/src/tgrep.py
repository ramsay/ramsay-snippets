'''
Created on Feb 12, 2011

@author: Robert Ramsay
'''
import sys
import os.path
import datetime
from math import log

YEAR = 2011
MONTHS = {'Jan': 1, 'Feb': 2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 
          'Aug':8, 'Sep': 9, 'Oct':10, 'Nov':11, 'Dec':12}

class SearchError(Exception):
    '''Custom error for when a loop takes too long.'''
    def __init__(self, *terms):
        Exception.__init__(self)
        self.terms = terms
    def __str__(self):
        return ("Search went to deep or endless loop. Search terms: " + 
                str(self.terms))

class ParametersError(Exception):
    '''Custom error for when the user enters parameters in the wrong''' 
    '''format.'''
    def __init__(self, *params):
        Exception.__init__(self)
        self.params = params
    def __str__(self):
        return ("Search parameters should be a time in the format hour:minute" +
                ":[second][-hour:minute:[second]], your parameters are: " +
                str(self.params))

def approximate_year(path):
    try:
        ctime = os.path.getctime(path)
        creation = datetime.date.fromtimestamp(ctime)
        YEAR = creation.year
    except os.error:
        YEAR = 2011
    return YEAR

def make_datetime(line, left=True):
    '''Utility method for converting the log date-time format to a native
    python `datetime` object. Defaults to `left` that uses 0 for missing
    arguments.
    May throw InvalidInput.'''
    segments = line.split(' ')
    while '' in segments:
        segments.remove('')
    if len(segments) > 2:
        month = segments.pop(0)
        numbers = [segments[0]]
        numbers.extend(segments[1].split(':'))
        dhms = []
        for num in numbers:
            print >> sys.stderr, num
            dhms.append(int(num))
        if left:
            dhms.extend([0]*(len(dhms)-4))
        else:
            max_time = (24,60,60)
            dhms.extend(max_time[len(dhms):])
        return datetime.datetime(YEAR, MONTHS[month], 
                                 dhms[0], dhms[1], 
                                 dhms[2], dhms[3])

class LogHandler:
    '''This is wrapper around the log file that enacts the search and
    extraction methods.'''
    name = '/logs/haproxy.log'
    bytes = 0
    index = []
    def __init__(self, name = None):
        if name is not None:
            self.name = name
        try:
            self.bytes = os.path.getsize(self.name)
        except os.error:
            print("File error.")
            raise
        else:
            approximate_year(self.name)
            self.handle = open(self.name, 'r')
            # get first index
            sample = self.handle.readline()
            self.first = make_datetime(sample)
            # get last index
            self.handle.seek(self.bytes-3*len(sample))
            sample = self.handle.readline()
            sample = self.handle.readline()
            while sample:
                self.last = make_datetime(sample)
                sample = self.handle.readline()
    
    def get_offset(self, dti, from_left=True):
        '''Finds the proper index for a date-time in the log file. Defaults to
        look for the "right" edge of a block of identical date-time's.'''
        print >> sys.stderr, dti
        if from_left:
            if self.first == dti:
                return 0
            if self.first > dti:
                dti += datetime.timedelta(1)
        else:
            if self.last == dti:
                return self.bytes
            if self.last < dti:
                dti -= datetime.timedelta(1)
        left = 0
        right = self.bytes
        pivot = self._snap(right/2)
        i = make_datetime(self.handle.readline())
        max_iteration = log(self.bytes/5)
        catcher = 0
        while i > dti or i < dti:
            catcher += 1
            if catcher > max_iteration:
                raise SearchError(dti, pivot)
            if dti > i:
                print >> sys.stderr, "Going to the right of ", i
                left = pivot
            else:
                print >> sys.stderr, "Going to the left of ", i
                right = pivot
            pivot = (right+left)/2
            print >> sys.stderr, (left, pivot, right)
            pivot = self._snap(pivot)
            line = self.handle.readline()
            i = make_datetime(line)
        return self.find_edge(left, right, dti, from_left)
    
    def find_edge(self, left, right, dti, from_left = True):
        '''Find the left or right edge of a block of similar `datetime`s'''
        print >> sys.stderr, "Found match, searching for edge."
        nextpivot = None
        pivot = self._snap((right+left)/2)
        i = make_datetime(self.handle.readline())
        while i == dti:
            if nextpivot is not None:
                pivot = nextpivot
            if from_left:
                print >> sys.stderr, "Going to the left of ", i
                right = pivot
            else:
                print >> sys.stderr, "Going to the right of ", i
                left = pivot
            nextpivot = (right+left)/2
            nextpivot = self._snap(nextpivot, from_left)
            i = make_datetime(self.handle.readline())
        return pivot

    def _snap(self, pivot, from_left = True):
        '''Utility method that returns the index of the closest line break to
        the given pivot point.'''
        if from_left:
            print >> sys.stderr, "Snapping to the left of ", pivot
        else:
            print >> sys.stderr, "Snapping to the right of ", pivot
        self.handle.seek(pivot, os.SEEK_SET)
        peek = self.handle.read(1)
        while peek != '\n' and peek != '\r':
            if from_left:
                self.handle.seek(-2, os.SEEK_CUR)
                if self.handle.tell() < 1:
                    return 0
            else:
                if self.handle.tell() > self.bytes - 2:
                    return self.bytes
            peek = self.handle.read(1)
        return self.handle.tell()
    
    def extract(self, *params):
        '''Converts the command line search parameters to the proper arguments
        for `self._get_offset` and then prints all line between the offsets to
        `stdout`.'''
        if len(params) == 1:
            search1 = make_datetime(params[0])
            search2 = search1
        elif len(params) == 2:
            search1 = params[0]
            search2 = params[1]
        else:
            raise ParametersError(params)
        index2 = self.get_offset(search2,from_left=False)
        index1 = self.get_offset(search1)
        self._snap(index1)
        while self.handle.tell() < index2:
            print(self.handle.readline())
    
if __name__ == '__main__':
    PARAMS = []
    LOGNAME = None
    for arg in sys.argv[1:3]:
        if (arg.contains(':') or arg.contains('0123456789') and 
            not arg.contains('a..zA..Z')):
            PARAMS = arg.split('-')
        else:
            # file name
            LOGNAME = arg
    LH = LogHandler(LOGNAME)
    LH.extract(PARAMS)
    sys.exit()

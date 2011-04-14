import breathalyzer

def TestDistance():
    assert(breathalyzer.distance("a", "a") == 0)
    assert(breathalyzer.distance("aa", "a") == 1)
    assert(breathalyzer.distance("ab", "a") == 1)
    assert(breathalyzer.distance("cat", "cot") == 1)
    assert(breathalyzer.distance("aaaa", "bbbb") == 4)

if __name__ == '__main__':
    TestDistance()

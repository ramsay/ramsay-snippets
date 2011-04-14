import breathalyzer

def TestDistance():
    assert(breathalyzer.distance("a", "a") == 0)
    assert(breathalyzer.distance("aa", "a") == 1)
    assert(breathalyzer.distance("ab", "a") == 1)
    assert(breathalyzer.distance("cat", "cot") == 1)
    assert(breathalyzer.distance("aaaa", "bbbb") == 4)
    assert(breathalyzer.distance("GOOD", "GOUD") == 1)
    assert(breathalyzer.distance("GOUD", "GOOD") == 1)


def TestBreathalyzer():
    wordlist = open("twl06.txt")
    post = open("breathalyzer.txt").read()
    assert(breathalyzer.breathalyzer(post, wordlist)==8)

if __name__ == '__main__':
    TestDistance()
    TestBreathalyzer()

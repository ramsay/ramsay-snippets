import breathalyzer
import cPickle
dictionary = cPickle.load(open("dict.txt", 'rb'))

def TestDistance():
    assert(breathalyzer.distance("a", "a") == 0)
    assert(breathalyzer.distance("aa", "a") == 1)
    assert(breathalyzer.distance("ab", "a") == 1)
    assert(breathalyzer.distance("cat", "cot") == 1)
    assert(breathalyzer.distance("aaaa", "bbbb") == 4)
    assert(breathalyzer.distance("GOOD", "GOUD") == 1)
    assert(breathalyzer.distance("GOUD", "GOOD") == 1)


def TestBreathalyzer():
    post = open("breathalyzer.txt").read()
    assert(breathalyzer.breathalyzer(post, dictionary)==8)

def Test4():
    post = open("4.in").read()
    assert(breathalyzer.breathalyzer(post, dictionary)==4)

def Test187():
    post = open("187.in").read()
    assert(breathalyzer.breathalyzer(post, dictionary)==187)

if __name__ == '__main__':
    TestDistance()
    Test4()

#!/usr/bin/python
''' Robert Ramsay  
https://github.com/ramsay/ramsay-snippets/tree/master/dropbox/the-dropbox-diet
The Dropbox Diet challenge
Of the boatload of perks Dropbox offers, the ones most threatening to our 
engineers' waistlines are the daily lunches, the fully-stocked drink fridge, 
and a full-length bar covered with every snack you could want. All of those 
calories add up. Luckily, the office is also well-equipped with ping-pong, a 
DDR machine, and a subsidized gym right across the street that can burn those 
calories right back off. Although we often don't, Dropboxers should choose 
the food they eat to counterbalance the activities they perform so that they 
don't end up with caloric deficit or excess.

Help us keep our caloric intake in check. You'll be given a list of 
activities and their caloric impact. Write a program that outputs the names 
of activities a Dropboxer should choose to partake in so that the sum of 
their caloric impact is zero. Once the activity is selected, it cannot be 
chosen again.

Input
Your program reads an integer N (1 <= N <= 50) from stdinrepresenting the 
number of list items in the test file. The list is comprised of activities or 
food items and its respective calorie impact separated by a space, one pair 
per line. Activity names will use only lowercase ASCII letters and the dash 
(-) character.

Output
Output should be sent to stdout, one activity name per line, alphabetized. If 
there is no possible solution, the output should be no solution. If there are 
multiple solutions, your program can output any one of them.

Sample Input

2
red-bull 140
coke 110

Sample Output

no solution


12
free-lunch 802
mixed-nuts 421
orange-juice 143
heavy-ddr-session -302
cheese-snacks 137
cookies 316
mexican-coke 150
dropballers-basketball -611
coding-six-hours -466
riding-scooter -42
rock-band -195
playing-drums -295
coding-six-hours
cookies
mexican-coke
'''

def su(x, y):
    return x + y[1]

def sum_activities(tuple_list):
    return reduce(su,tuple_list,0)

def mi(x,y):
    if x[1] > y[1]:
        return y
    else:
        return x

def min_activities(tuple_list):
    if tuple_list:
        return reduce(mi,tuple_list)
    return (None,0)

def ma(x,y):
    if x[1] > y[1]:
        return x
    else:
        return y

def max_activities(tuple_list):
    if tuple_list:
        return reduce(ma, tuple_list)
    return (None, 0)

def diet(activities):
    ''' Takes a `dict` of activities {'name':calorie-value} and returns a list
    of strings that sum up to zero or "no solution"'''
    diet_list = []
    positive = []
    negative = []
    #Separate positive and negative activities.
    for k in activities:
        v = activities[k]
        if v > 0:
            positive.append((k,v))
        elif v < 0:
            negative.append((k,v))
        else:
            # Value is zero?! Good for any diet.
            diet_list.append(k)
    
    # At this point all items left will be non extremes and non-trivial
    ''' From en.wikipedia.org/wiki/Suset_sum_problem on Feb. 7, 2011
    The problem can be solved as follows using dynamic programming. Suppose the
    sequence is
        x1, ..., xn
    and we wish to determine if there is a nonempty subset which sums to 0. Let
    N be the sum of the negative values and P the sum of the positive values. 
    Define the boolean-valued function Q(i,s) to be the value (true or false) 
    of
        "there is a nonempty subset of x1, ..., xi which sums to s".
    Thus, the solution to the problem is the value of Q(n,0).
    Clearly, Q(i,s) = false if s < N or s > P so these values do not need to be
    stored or computed. Create an array to hold the values Q(i,s) for 1 <= i <= n
    and N <= s <= P.
    The array can now be filled in using a simple recursion. 
    Initially, for N <= s <= P, set
        Q(1,s) := (x1 = s).
    Then, for i = 2, ..., n, set
        Q(i,s) := Q(i - 1,s) or (xi = s) or Q(i - 1,s - xi) for N <= s <= P.
    For each assignment, the values of Q on the right side are already known,
    either because they were stored in the table for the previous value of i or
    because Q(i - 1,s - xi) = false if s - xi < N or s - xi > P. Therefore, the
    total number of arithmetic operations is O(n(P - N)). For example, if all 
    the values are O(nk) for some k, then the time required is O(nk+2).
    This algorithm is easily modified to return the subset with sum 0 if there 
    is one.
    This solution does not count as polynomial time in complexity theory 
    because P - N is not polynomial in the size of the problem, which is the 
    number of bits used to represent it. This algorithm is polynomial in the 
    values of N and P, which are exponential in their numbers of bits.
    '''
    if negative and positive:
        N = sum_activities(negative)
        P = sum_activities(positive)
        both = negative + positive
        q = [{str(both[0][1]): [both[0][0]]}]
        for i in range(1,len(both)):
            d = {}
            for s in range(N,P):
                if both[i][1] == s:
                    d[str(s)] = [both[i][0]]
                elif str(s) in q[i-1]:
                    d[str(s)] = q[i-1][str(s)]
                elif str(s-both[i][1]) in q[i-1]:
                    d[str(s)] = [both[i][0]] + q[i-1][str(s-both[i][1])]
            q.append(d)
        
        #Find a zero-sum in our solution space.
        for i in range(len(both)-1,0,-1):
            if '0' in q[i]:
                diet_list.extend(q[i]['0'])
                break # Just one will do.
    
    if diet_list:
        #We have at least one entry.
        diet_list.sort()
        return diet_list
    return ["no solution"]

if __name__ == '__main__':
    import sys
    try:
        count = int(input())
    except Exception as e:
        print sys.stderr >> e
        print("First input must be an integer")
        sys.exit()
    if count > 50:
        print >> sys.stderr, "Maximum count is 50 by project description."
        count = 50
    if count < 1:
        print >> sys.stderr, "Minimum count is 1 by project description."
        count = 1
    activites = {}
    for i in range(count):
        key_value_pair = raw_input()
        try:
            key = key_value_pair.split(' ')[0]
            value = int(key_value_pair.split(' ')[1])
        except Exception as e:
            print >> sys.stderr, e
            print("Activity Input must take form: activity-name 100")
            sys.exit()
        activites[key] = value
    print('\n'.join(diet(activites)))
    sys.exit()
        









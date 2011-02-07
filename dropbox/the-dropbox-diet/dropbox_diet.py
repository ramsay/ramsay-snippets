#!/usr/bin/python
''' The Dropbox Diet challenge
Of the boatload of perks Dropbox offers, the ones most threatening to our engineers' waistlines are the daily lunches, the fully-stocked drink fridge, and a full-length bar covered with every snack you could want. All of those calories add up. Luckily, the office is also well-equipped with ping-pong, a DDR machine, and a subsidized gym right across the street that can burn those calories right back off. Although we often don't, Dropboxers should choose the food they eat to counterbalance the activities they perform so that they don't end up with caloric deficit or excess.

Help us keep our caloric intake in check. You'll be given a list of activities and their caloric impact. Write a program that outputs the names of activities a Dropboxer should choose to partake in so that the sum of their caloric impact is zero. Once the activity is selected, it cannot be chosen again.

Input
Your program reads an integer N (1 <= N <= 50) from stdinrepresenting the number of list items in the test file. The list is comprised of activities or food items and its respective calorie impact separated by a space, one pair per line. Activity names will use only lowercase ASCII letters and the dash (-) character.

Output
Output should be sent to stdout, one activity name per line, alphabetized. If there is no possible solution, the output should be no solution. If there are multiple solutions, your program can output any one of them.

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

def sum_activities(tuple_list):
    s = 0
    for t in tuple_list:
        s += t[1]

def diet(activities):
    ''' Takes a `dict` of activities {'name':calorie-value} and returns a list
    of strings that sum up to zero or "no solution"'''
    diet_list = []
    positive = []
    negative = []
    #Separate positive and negative activites.
    for k in activities:
        v = activities[k]
        if v > 0:
            positive.append((k,v))
        elif v < 0:
            negative.append((k,abs(v)))
        else:
            # Value is zero?! Good for any diet.
            diet_list.append(k)
    
    #Remove 1 to |-1| duplicates.
    for i in range(len(positive)):
        k, v = positive[i]
        j = 0
        for j in range(len(negative)):
            k2, v2 = negative[j]
            if v == v2:
                diet_list.append(k)
                diet_list.append(k2)
                positive[i] = None
                break
        if positive[i] is None:
            negative.pop(j)
    
    #Clean up.
    while positive.count(None):
        positive.remove(None)
    
    while len(positive) and len(negative):
        break
    
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
        key_value_pair = input()
        try:
            key = key_value_pair.split(' ')[0]
            value = int(key_value_pair.split(' ')[0])
        except Exception as e:
            print sys.stderr >> e
            print("Activity Input must take form: activity-name 100")
            sys.exit()
        activites['key'] = value
    print('\n'.join(diet(activites)))
    sys.exit()
        









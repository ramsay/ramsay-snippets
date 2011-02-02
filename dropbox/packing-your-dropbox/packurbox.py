#!/usr/bin/python
"""
Robert Ramsay <robert.alan.ramsay@gmail.com>
Packing your Dropbox
When you're working with petabytes of data, you have to store files wherever they can fit. All of us here at Dropbox are always searching for more ways to efficiently pack data into smaller and more manageable chunks. The fun begins when you bend the rules a little bit and visualize it in two dimensions.

You'll be given a list of rectangular "files" that you'll need to pack into as small a "Dropbox" as possible. The dimensions of each file will be specified by a tuple (width, height), both of which will be integers. The output of your function should be the area of the smallest rectangular Dropbox that can enclose all of them without any overlap. Files can be rotated 90(deg) if it helps. Bonus points if you can draw pictures of the winning configurations along the way. While drawing pictures, any files sharing dimensions should be considered identical/interchangeable.

Input
Your program must read a small integer N (1 <= N <= 100) from stdin representing the maximum number of files to consider, followed by the width and height of each file, one per line.

Output
Output should be simply be the area of the smallest containing Dropbox. If you want to print pretty pictures, send that to stderr. Only the output on stdout will be judged.

Sample Input

3
8 8
4 3
3 4

Sample Output

88
"""
#from __future__ import print_function
import sys

class DropBox:
    w = 1
    h = 1
    x = 0
    y = 0
    def rotate(self):
        t = self.w
        self.w = self.h
        self.h = t

    def align(self):
        if self.w > self.h:
            self.rotate()
        return self.h

#free space = (lowest left x, lowest left y, width, height)
def fit(size, free, box):
    x, y, w, h = free
    box.x = x
    box.y = y

    if h < box.h and w < box.w:
        size = (size[0]+box.w-w, size[1]+box.h-h)
        x += box.w
        w = 0
        h = box.h
    elif w < box.w:
        size = (size[0] + box.w - w, size[1])
        w = box.w
        y += box.h
        h -= box.h
    else:
        x += box.w
        w -= box.w

    free = (x, y, w, h)
    return size, free

def pretty(boxes,w,h):
    '''Pretty print the list of boxes'''
    print >> sys.stderr, str(w) + 'x' + str(h) + ':'
    graph = [[' ' for l in range(h+1)] for m in range(w+1)]
    for box in boxes:
        try:
            # Vertices
            graph[box.x][box.y] = '+'
            graph[box.x+box.w][box.y] = '+'
            graph[box.x][box.y+box.h] = '+'
            graph[box.x+box.w][box.y+box.h] = '+'

            # Edges
            for x in range(box.x+1, box.x+box.w):
                graph[x][box.y] = '|'
                graph[x][box.y+box.h] = '|'

            for y in range(box.y+1, box.y+box.h):
                graph[box.x][y] = '-'
                graph[box.x+box.w][y] = '-'
        except:
            pass #Let's not worry about errors in an optional feature
    print >> sys.stderr, '\n'.join([''.join(row) for row in graph])


def pack(boxes):
    #Align all the boxes and sort them by height lagest to smallest
    boxes.sort(key=lambda box: box.align(), reverse=True)
    size = (0, 0)
    #free = (left, lower, width, height)
    free = (0, 0, 0, 0)
    for box in boxes:
        size, free = fit(size, free, box)
    pretty(boxes, size[0], size[1])
    return size[0]*size[1]

if __name__ == '__main__':
    import sys
    inp = input() #Number of boxes
    try:
        boxcount = int(inp)
    except:
        sys.exit()
    boxes = []
    for i in range(boxcount):
        inp = raw_input('') #Box: width height
        box = DropBox()
        try:
            w, h = inp.split(" ")
            box.w = int(w)
            box.h = int(h)
        except:
            sys.exit()
        boxes.append(box)
    print(pack(boxes))
    sys.exit()

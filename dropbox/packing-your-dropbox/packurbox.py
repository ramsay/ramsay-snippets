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
        # Our box will not fit inside the current freespace.
        size = (size[0]+box.w-w, size[1]+box.h-h)
        x += box.w
        w = 0
        h = box.h
    elif w < box.w:
        size = (size[0] + box.w - w, size[1])
        w = box.w
        y += box.h
        h -= box.h
    elif h < box.h:
        x += box.w
        w -= box.w
    else:
        box.rotate()
        if w < box.w:
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
        except Exception as e:
            print >> sys.stderr, "Box (", box.x, box.y, box.w, box.h, ") is outside bounds (", w, h,")"
            raise e
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

class DropNode:
    left = None # Left Edge is the parent.
    vertex = None # We can store atmost one Box
    right = None # Right Edge is the child.
    direction = [1,0] # direction is the identiy ray
    def __init__(self,vertex=None, left=None, right=None):
        self.vertex = vertex
        self.left = left
        if self.left:
            self.left.right = self
        self.right = right
        if self.right:
            if self.vertex.w > self.vertex.h:
                # An increase in width costs less than an increase in height
                # if width is already greater.
                self.direction = [1,0]
            else:
                self.direction = [0,1]
            self.right.left = self

    def rotate(self):
        direction.reverse()
        if self.vertex:
            self.vertex.rotate()
        if self.right:
            self.right.rotate()

    def width(self):
        w = 0
        if self.vertex:
            w = self.vertex.w
        if self.right:
            w += self.direction[0]*self.right.width()
        return w

    def height(self):
        h = 0
        if self.vertex:
            h = self.vertex.h
        if self.right:
            h += self.direction[1]*self.right.height()
        return h

def packtree(node, boxes):
    '''This is a recursive pack algorithm, similar to a binary search
    tree.'''
    if not boxes: # Stack empty.
        return node

    if node is None: #RootNode
        print >> sys.stderr, "root node", boxes[-1]
        return packtree(DropNode(boxes.pop(0)), boxes)

    if node.vertex is None: # Not sure if I agree with this.
        print >> sys.stderr, "curious"
        node.vertex = boxes.pop()
        return packtree(node, boxes)
    # Make comparisons simpler
    left = (max(boxes[0].w, boxes[0].h), min(boxes[0].w, boxes[0].h))
    w = node.width()
    h = node.height()
    right = (max(w, h), min(w, h))
    print >> sys.stderr, "left", left,
    print >> sys.stderr, "right", right,
    if left[0] > right[0]:
        if node.left:
            return packtree(node.left, boxes)
        else:
            print >> sys.stderr, "insert left"
            return packtree(DropNode(boxes.pop(0),None,node), boxes)
    if left[0] <= right[1]:
        if node.right:
            return packtree(node.right, boxes)
        else:
            print >> sys.stderr, "insert right"
            return packtree(DropNode(boxes.pop(0),node),boxes)
    print >> sys.stderr, "insert middle"
    return packtree(DropNode(boxes.pop(0), node.left, node), boxes)

def prettytree(tree):
    '''Pretty print the list of boxes'''
    w = tree.width()
    h = tree.height()
    print >> sys.stderr, str(w) + 'x' + str(h) + ':'
    graph = [[' ' for l in range(h+1)] for m in range(w+1)]
    #Find root:
    node = tree
    while node.left:
        node = node.left
    vx = 0
    vy = 0
    i = 0
    while node.right:
        i += 1
        print >> sys.stderr, '.',
        if node.vertex is None:
            print >> sys.stderr, "Empty Vertex"
            node = node.right
            continue
        try:
            vw = tree.vertex.w
            vh = tree.vertex.h
            # Vertices
            graph[vx][vy] = '+'
            graph[vx+vw][vy] = '+'
            graph[vx][vy+vh] = '+'
            graph[vx+vw][vy+vh] = '+'
    
            # Edges
            for x in range(vx+1, vx+vw):
                graph[x][vy] = '|'
                graph[x][vy+vh] = '|'
    
            for y in range(vy+1, vy+vh):
                graph[vx][y] = '-'
                graph[vx+vw][y] = '-'
            vx += tree.direction[0]*vw
            vy += tree.direction[1]*vh
        except Exception as e:
            raise e
        node = node.right
    print >> sys.stderr, '\n'.join([''.join(row) for row in graph])

if __name__ == '__main__':
    import sys
    inp = input() #Number of boxes
    try:
        boxcount = int(inp)
        if boxcount < 1 or boxcount > 100:
            raise
    except:
        sys.exit("Box count must be between 1 and 100 (inclusive)")

    boxes = []
    for i in range(boxcount):
        inp = raw_input('') #Box: width height
        box = DropBox()
        try:
            w, h = inp.split(" ")
            box.w = int(w)
            box.h = int(h)
        except:
            sys.exit("Box definition should be integers seperated "\
            "by whitespace")
        boxes.append(box)
    print(pack(boxes))
    sys.exit()

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
import sys

class DropBox:
    w = 1
    h = 1
    
    def rotate(self):
        t = self.w
        self.w = self.h
        self.h = t
    
    def align(self):    
        if self.w < self.h:
            self.rotate()
        return self.w

def fit(size, free, box):
    """Fits a DropBox `box` inside freespace `free`
    left.
    size - 2 tuple representing the (width, height) to fit our box inside
    free - 4 tuple representing the (x, y, width, height) of remaining space in
    the box.
    @returns new `size` and remaining `free`
    """
    if box.w > free[2] and box.h > free[3]:
        # Just grow the container and continue.
        
    if box.w > free[2]:
        #Our box does not fit, we must grow
        if box.w > free[2]:
            size[0] = size[0]+free[2]-box.w
            free[2] = box.w
        if box.h > free[3]:
            size[1] = size[1]+free[3]-box.h
            free[3] = box.h
            
    # Update `free`
    if box.w > box.h:
        free[0] = free[0]+box.w
        free[2] = free[2]-box.w
    else:
        free[3] = free[3]-box.h
    return size, free

def pack(boxes):
    #sort the boxes to deal with largest first
    boxes.sort(key=lambda box: return box.align(), reverse=True)
    size = (boxes[0].w, boxes[0].h)
    for box in boxes:
        size, free = fit(size, free, box)
    #return the area of our best fit size
    return size[0]*size[1]
    

if __name__ == '__main__':
    inp = input("Number of Boxes> ")
    try:
        boxcount = int(inp)
    except:
        sys.exit("First input must be an integer")
    boxes = []
    for i in range(boxcount):
        box = DropBox()
        inp = raw_input(str(i)+": width height> ")
        w, h = inp.split(" ")
        try:
            box.w = int(w)
            box.h = int(h)
        except:
            sys.exit("Width/Height must be integer")
        boxes.append(box)
    size = pack(boxes)
    sys.exit(str(size))

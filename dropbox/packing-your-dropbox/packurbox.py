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
class DropBox:
    w = 1
    h = 1
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

def pack(boxes):
    #Align all the boxes and sort them by height lagest to smallest
    boxes.sort(key=lambda box: box.align(), reverse=True)
    size = (0, 0)
    #free = (left, lower, width, height)
    free = (0, 0, 0, 0)
    for box in boxes:
        print( "Packing box: ", box.w, box.h)
        size, free = fit(size, free, box)
        print size, free
    return size[0]*size[1]

if __name__ == '__main__':
    import sys
    inp = input("Number of boxes")
    try:
        boxcount = int(inp)
    except:
        sys.exit()
    boxes = []
    for i in range(boxcount):
        inp = raw_input(str(i) + ": width height> ")
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

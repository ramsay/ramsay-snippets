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

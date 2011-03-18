"""
Liquid.py - Python+Pygame port V1 Robert Rasmay
MIT License ( http://www.opensource.org/licenses/mit-license.php )

/**
 * self version:
 * Copyright Stephen Sinclair (radarsat1) (http://www.music.mcgill.ca/~sinclair)
 * MIT License ( http://www.opensource.org/licenses/mit-license.php )
 * Downloaded from: http://www.music.mcgill.ca/~sinclair/blog
 */

/**
 * Flash version:
 * Copyright iunpin ( http://wonderfl.net/user/iunpin )
 * MIT License ( http://www.opensource.org/licenses/mit-license.php )
 * Downloaded from: http://wonderfl.net/c/6eu4
 */

/**
 * Original Java version:
 * http://grantkot.com/MPM/Liquid.html
 */
"""
import pygame
import pygame.locals
import math
import random
import time

WIDTH = 100
HEIGHT = 100
PARTICLESX = 50
PARTICLESY = 80

class LiquidTest:
    def __init__ (self, gsizeX, gsizeY, particlesX, particlesY):
        self.gsizeX = gsizeX
        self.gsizeY = gsizeY
        self.active = [] #Nodes
        self.water = Material(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        self.pressed = False
        self.pressedprev = False
        self.mx = 0.0
        self.my = 0.0
        self.mxprev = 0.0
        self.myprev = 0.0


        self.grid = [[Node() for j in range(self.gsizeY)] 
            for i in range(self.gsizeX)]
        
        '''
        for i in range(self.gsizeX):
            self.grid.append([])
            for j in range(self.gsizeY):
                self.grid[i].append(Node())
        '''
        self.particles = [Particle(self.water, i + 4, j + 4, 0.0, 0.0)
            for j in range(particlesY) for i in range(particlesX)]
        
        '''
        for i in range(particlesX):
            for j in range(particlesY):
                self.particles.append(Particle(self.water, i + 4, j + 4, 0.0, 0.0))
        '''

    def paint(self):
        for p in self.particles:
            pygame.draw.line(CANVAS, p.color, (4*p.x, 4*p.y,),
                (4*(p.x - p.u), 4.0*(p.y - p.v)))

    def simulate(self):
        drag = False
        mdx = mdy = 0.0

        if (self.pressed and self.pressedprev):
            drag = True
            mdx = 0.25 * (self.mx - self.mxprev)
            mdy = 0.25 * (self.my - self.myprev)

        self.pressedprev = self.pressed
        self.mxprev = self.mx
        self.myprev = self.my

        while(len(self.active)):
            self.active.pop().clear()


        fx = fy = 0.0
        for p in self.particles:
            p.cx = p.x - 0.5
            p.cy = p.y - 0.5

            x = p.cx - p.x
            p.px[0] = (0.5 * x * x + 1.5 * x + 1.125)
            p.gx[0] = (x + 1.5)
            x += 1.0
            p.px[1] = (-x * x + 0.75)
            p.gx[1] = (-2.0 * x)
            x += 1.0
            p.px[2] = (0.5 * x * x - 1.5 * x + 1.125)
            p.gx[2] = (x - 1.5)

            y = p.cy - p.y
            p.py[0] = (0.5 * y * y + 1.5 * y + 1.125)
            p.gy[0] = (y + 1.5)
            y += 1.0
            p.py[1] = (-y * y + 0.75)
            p.gy[1] = (-2.0 * y)
            y += 1.0
            p.py[2] = (0.5 * y * y - 1.5 * y + 1.125)
            p.gy[2] = (y - 1.5)

            for i in range(3):
                for j in range(3):
                    n = self.grid[int(p.cx + i)][int(p.cy + j)]
                    if not n.active:
                        self.active.append(n)
                        n.active = True
                    phi = p.px[i] * p.py[j]
                    n.m += phi * p.mat.m
                    n.d += phi
                    n.gx += p.gx[i] * p.py[j]
                    n.gy += p.px[i] * p.gy[j]


        for p in self.particles:

            cx = p.x
            cy = p.y
            cxi = cx + 1
            cyi = cy + 1

            n01 = self.grid[int(cx)][int(cy)]
            n02 = self.grid[int(cx)][int(cyi)]
            n11 = self.grid[int(cxi)][int(cy)]
            n12 = self.grid[int(cxi)][int(cyi)]

            pdx = n11.d - n01.d
            pdy = n02.d - n01.d
            C20 = 3.0 * pdx - n11.gx - 2.0 * n01.gx
            C02 = 3.0 * pdy - n02.gy - 2.0 * n01.gy
            C30 = -2.0 * pdx + n11.gx + n01.gx
            C03 = -2.0 * pdy + n02.gy + n01.gy
            csum1 = n01.d + n01.gy + C02 + C03
            csum2 = n01.d + n01.gx + C20 + C30
            C21 = 3.0 * n12.d - 2.0 * n02.gx - n12.gx - 3.0 * csum1 - C20
            C31 = -2.0 * n12.d + n02.gx + n12.gx + 2.0 * csum1 - C30
            C12 = 3.0 * n12.d - 2.0 * n11.gy - n12.gy - 3.0 * csum2 - C02
            C13 = -2.0 * n12.d + n11.gy + n12.gy + 2.0 * csum2 - C03
            C11 = n02.gx - C13 - C12 - n01.gx

            u = p.x - cx
            u2 = u * u
            u3 = u * u2
            v = p.y - cy
            v2 = v * v
            v3 = v * v2
            density = n01.d + n01.gx * u + n01.gy * v + C20 * u2 + C02 * v2 + C30 * u3 + C03 * v3 + C21 * u2 * v + C31 * u3 * v + C12 * u * v2 + C13 * u * v3 + C11 * u * v

            pressure = density - 1.0
            if pressure > 2.0:
                pressure = 2.0

            fx = 0.0
            fy = 0.0

            if (p.x < 4.0):
                fx += p.mat.m * (4.0 - p.x)
            elif (p.x > self.gsizeX - 5):
                fx += p.mat.m * (self.gsizeX - 5 - p.x)

            if (p.y < 4.0):
                fy += p.mat.m * (4.0 - p.y)
            elif (p.y > self.gsizeY - 5):
                fy += p.mat.m * (self.gsizeY - 5 - p.y)

            if drag:
                vx = math.fabs(p.x - 0.25 * self.mx)
                vy = math.fabs(p.y - 0.25 * self.my)
                if ((vx < 10.0) and (vy < 10.0)):
                    weight = p.mat.m * (1.0 - vx * 0.10) * (1.0 - vy * 0.10)
                    fx += weight * (mdx - p.u)
                    fy += weight * (mdy - p.v)

            for i in range(3):
                for j in range(3):
                    n = self.grid[int(p.cx + i)][int(p.cy + j)]
                    phi = p.px[i] * p.py[j]
                    n.ax += -((p.gx[i] * p.py[j]) * pressure) + fx * phi
                    n.ay += -((p.px[i] * p.gy[j]) * pressure) + fy * phi

        for n in self.active:
            if n.m > 0.0:
                n.ax /= n.m
                n.ay /= n.m
                n.ay += 0.03

        for p in self.particles:
            for i in range(3):
                for j in range(3):
                    n = self.grid[int(p.cx + i)][int(p.cy + j)]
                    phi = p.px[i] * p.py[j]
                    p.u += phi * n.ax
                    p.v += phi * n.ay
            mu = p.mat.m * p.u
            mv = p.mat.m * p.v
            for i in range(3):
                for j in range(3):
                    n = self.grid[int(p.cx + i)][int(p.cy + j)]
                    phi = p.px[i] * p.py[j]
                    n.u += phi * mu
                    n.v += phi * mv

        for n in self.active:
            if n.m > 0.0:
                n.u /= n.m
                n.v /= n.m

        for p in self.particles:
            gu = 0.0
            gv = 0.0
            for i  in range(3):
                for j  in range(3):
                    n = self.grid[int(p.cx + i)][int(p.cy + j)]
                    phi = p.px[i] * p.py[j]
                    gu += phi * n.u
                    gv += phi * n.v
            p.x += gu
            p.y += gv
            p.u += 1.0 * (gu - p.u)
            p.v += 1.0 * (gv - p.v)
            if (p.x < 1.0):
                p.x = (1.0 + random.random() * 0.01)
                p.u = 0.0
            elif (p.x > self.gsizeX - 2):
                p.x = (self.gsizeX - 2 - random.random() * 0.01)
                p.u = 0.0
            if (p.y < 1.0):
                p.y = (1.0 + random.random() * 0.01)
                p.v = 0.0
            elif (p.y > self.gsizeY - 2):
                p.y = (self.gsizeY - 2 - random.random() * 0.01)
                p.v = 0.0

class Node:
    def __init__(self):
        self.m = 0
        self.d = 0
        self.gx = 0
        self.gy = 0
        self.u = 0
        self.v = 0
        self.ax = 0
        self.ay = 0
        self.active = False
    
    def clear(self):
        self.m = self.d = self.gx = self.gy = self.u = self.v = self.ax = self.ay = 0.0
        self.active = False

class Particle:
    def __init__(self, mat, x, y, u, v):
        self.dudx = 0
        self.dudy = 0
        self.dvdx = 0
        self.dvdy = 0
        self.cx = 0
        self.cy = 0
        self.px = [0,0,0]
        self.py = [0,0,0]
        self.gx = [0,0,0]
        self.gy = [0,0,0]
        
        self.mat = mat
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.color = pygame.Color(0,0,255,255)

class Material:
    def __init__(self, m, rd, k, v, d, g):
        self.m = m
        self.rd = rd
        self.k = k
        self.v = v
        self.d = d
        self.g = g

def mouseMoved(event):
    LIQUID_TEST.mx = event.pos[0]
    LIQUID_TEST.my = event.pos[1]

def mousePressed(event):
    LIQUID_TEST.pressed = True

def mouseReleased(event):
    LIQUID_TEST.pressed = False

def main():
    pygame.init()
    global CANVAS
    CANVAS = pygame.display.set_mode((WIDTH*4, HEIGHT*4), pygame.DOUBLEBUF)
    
    global LIQUID_TEST
    LIQUID_TEST = LiquidTest(WIDTH, HEIGHT, PARTICLESX, PARTICLESY)
    while True:
        # clear
        CANVAS.fill(0, (3, 3, WIDTH*4-4, HEIGHT*4-4))
        # draw simulation state
        LIQUID_TEST.paint()
        pygame.display.flip()
        #get events
        for e in pygame.event.get():
            if e.type == pygame.locals.QUIT:
                return
            elif e.type == pygame.locals.MOUSEBUTTONDOWN:
                mousePressed(e)
            elif e.type == pygame.locals.MOUSEBUTTONUP:
                mouseReleased(e)
            elif e.type == pygame.locals.MOUSEMOTION:
                mouseMoved(e)
        # advance simulation
        LIQUID_TEST.simulate()
    
if __name__ == "__main__":
    main()

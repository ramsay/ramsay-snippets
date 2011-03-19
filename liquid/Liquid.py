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
from line_profiler import LineProfiler
from array import array

CANVAS = None
LIQUID_TEST = None
WIDTH = 100
HEIGHT = 100
PARTICLESX = 50
PARTICLESY = 80

RANGE = range(3)

class LiquidTest:
    def __init__ (self, width, height, particlesX, particlesY):
        self.width = width
        self.height = height
        self.active = set()
        self.water = Material(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        self.pressed = False
        self.pressedprev = False
        self.mx = 0.0
        self.my = 0.0
        self.mxprev = 0.0
        self.myprev = 0.0


        self.grid = [[Node() for j in range(self.height)] 
            for i in range(self.width)]
        
        self.particles = [Particle(self.water, i + 4, j + 4, 0.0, 0.0)
            for j in range(particlesY) for i in range(particlesX)]
        

    def paint(self):
        for p in self.particles:
            pygame.draw.line(CANVAS, p.color, (4*p.x, 4*p.y,),
                (4*(p.x - p.u), 4.0*(p.y - p.v)))

    def _step1(self):
        for particle in self.particles:
            particle.cx = int(particle.x - 0.5)
            particle.cy = int(particle.y - 0.5)
            
            x = float(particle.cx - particle.x)
            particle.px[0] = 0.5 * x * x + 1.5 * x + 1.125
            particle.gx[0] = x + 1.5
            x += 1.0
            particle.px[1] = -x * x + 0.75
            particle.gx[1] = -2.0 * x
            x += 1.0
            particle.px[2] = 0.5 * x * x - 1.5 * x + 1.125
            particle.gx[2] = x - 1.5

            y = float(particle.cy - particle.y)
            particle.py[0] = 0.5 * y * y + 1.5 * y + 1.125
            particle.gy[0] = y + 1.5
            y += 1.0
            particle.py[1] = -y * y + 0.75
            particle.gy[1] = -2.0 * y
            y += 1.0
            particle.py[2] = 0.5 * y * y - 1.5 * y + 1.125
            particle.gy[2] = y - 1.5


            for i in RANGE:
                for j in RANGE:
                    n = self.grid[particle.cx + i][particle.cy + j]
                    if not n.active:
                        n.active = True
                        self.active.add(n)
                    phi = particle.px[i] * particle.py[j]
                    n.m += phi * particle.material.m
                    n.d += phi
                    n.gx += particle.gx[i] * particle.py[j]
                    n.gy += particle.px[i] * particle.gy[j]

    def _step2(self, drag, mdx, mdy):       
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
            density = (n01.d + n01.gx * u + n01.gy * v + C20 * u2 + C02 * v2 + 
                C30 * u3 + C03 * v3 + C21 * u2 * v + C31 * u3 * v + C12 * u * 
                v2 + C13 * u * v3 + C11 * u * v)

            pressure = density - 1.0
            if pressure > 2.0:
                pressure = 2.0

            fx = 0.0
            fy = 0.0

            if p.x < 4.0:
                fx += p.material.m * (4.0 - p.x)
            elif p.x > self.width:
                fx += p.material.m * (self.width - p.x)

            if p.y < 4.0:
                fy += p.material.m * (4.0 - p.y)
            elif p.y > self.height:
                fy += p.material.m * (self.height - p.y)

            if drag:
                vx = math.fabs(p.x - 0.25 * self.mx)
                vy = math.fabs(p.y - 0.25 * self.my)
                if  vx < 10.0 > vy:
                    weight = p.material.m * (1.0 - vx * 0.10) * (1.0 - vy * 0.10)
                    fx += weight * (mdx - p.u)
                    fy += weight * (mdy - p.v)

            for i in RANGE:
                for j in RANGE:
                    n = self.grid[p.cx + i][p.cy + j]
                    phi = p.px[i] * p.py[j]
                    n.ax += -(p.gx[i] * p.py[j] * pressure) + fx * phi
                    n.ay += -(p.px[i] * p.gy[j] * pressure) + fy * phi
    
    def _compress_nodes(self):
        for n in self.active:
            if n.m > 0.0:
                n.ax /= n.m
                n.ay /= n.m
                n.ay += 0.03

    def _step3(self):
        for p in self.particles:
            for i in RANGE:
                for j in RANGE:
                    n = self.grid[p.cx + i][p.cy + j]
                    phi = p.px[i] * p.py[j]
                    p.u += phi * n.ax
                    p.v += phi * n.ay
            mu = p.material.m * p.u
            mv = p.material.m * p.v
            for i in RANGE:
                for j in RANGE:
                    n = self.grid[p.cx + i][p.cy + j]
                    phi = p.px[i] * p.py[j]
                    n.u += phi * mu
                    n.v += phi * mv

    def _compress_nodes2(self):
        for n in self.active:
            if n.m > 0.0:
                n.u /= n.m
                n.v /= n.m

    def _step4(self):
        for p in self.particles:
            gu = 0.0
            gv = 0.0
            for i  in RANGE:
                for j  in RANGE:
                    n = self.grid[p.cx + i][p.cy + j]
                    phi = p.px[i] * p.py[j]
                    gu += phi * n.u
                    gv += phi * n.v
            p.x += gu
            p.y += gv
            p.u += 1.0 * (gu - p.u)
            p.v += 1.0 * (gv - p.v)
            if p.x < 1.0:
                p.x = 1.0 + random.random() * 0.01
                p.u = 0.0
            elif p.x > self.width - 2:
                p.x = self.width - 2 - random.random() * 0.01
                p.u = 0.0
            if p.y < 1.0:
                p.y = 1.0 + random.random() * 0.01
                p.v = 0.0
            elif p.y > self.height - 2:
                p.y = self.height - 2 - random.random() * 0.01
                p.v = 0.0

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

        for node in self.active:
            node.__init__()
        self.active.clear()

        self._step1()
        
        self._step2(drag, mdx, mdy)
        
        self._compress_nodes()
        
        self._step3()
        
        self._compress_nodes2()

        self._step4()
        
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

class Particle:
    '''Particles are value holders that manage the mathematical and physical
    attributes of an object'''
    def __init__(self, material, x, y, u, v):
        self.dudx = 0
        self.dudy = 0
        self.dvdx = 0
        self.dvdy = 0
        self.cx = 0
        self.cy = 0
        self.px = array('f', [0, 0, 0])
        self.py = array('f', [0, 0, 0])
        self.gx = array('f', [0, 0, 0])
        self.gy = array('f', [0, 0, 0])
        
        self.material = material
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.color = pygame.Color(0, 0, 255, 255)

class Material:
    '''Some of these parameters are hard to explain in one or two sentences 
    (and a couple I made up) so I'll also link you to their corresponding 
    Wikipedia pages. One object I like to compare fluids with is springs. 
    Everybody is familiar with springs. If you pull on them they'll try to go 
    back to their original shape. Some springs are stronger and some are weaker 
    (stiffness and elasticity). Some springs will continue to bounce back and 
    forth for a long time, while others will quickly slow down and stop (bulk 
    viscosity and viscosity). If you pull hard enough the spring will break.

    Density - Target density for the particles. Higher density makes particles 
    want to be closer together.

    Stiffness - How compressible the fluid is.

    Bulk viscosity - Kind of like damping. Another effect it will have is that 
    it'll smooth out shockwaves.

    Elasticity - How fast the fluid will try to return to its original shape.

    Viscosity - Kind of like bulk viscosity only this operates on the shear 
    components.

    Yield rate - How fast the fluid forgets its shape or melts away. Only 
    affects things when elasticity is non-zero.

    Gravity - How much the particles will accelerate downwards.

    Smoothing - Smooths the velocity field. Will make things more stable. It is 
    also useful to have a high smoothing value when simulating elastic 
    materials.
    '''
    def __init__(self, m, rd, k, v, d, g):
        self.m = m
        self.rd = rd
        self.k = k
        self.v = v
        self.d = d
        self.g = g

def main(n = 200):
    pygame.init()
    global CANVAS
    CANVAS = pygame.display.set_mode((WIDTH*4, HEIGHT*4), pygame.DOUBLEBUF)
    
    global LIQUID_TEST
    LIQUID_TEST = LiquidTest(WIDTH, HEIGHT, PARTICLESX, PARTICLESY)
    for i in range(n):
        # clear
        CANVAS.fill(0, (3, 3, WIDTH*4-4, HEIGHT*4-4))
        # draw simulation state
        LIQUID_TEST.paint()
        pygame.display.flip()
        #get events
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                LIQUID_TEST.pressed = True
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                LIQUID_TEST.pressed = False
            elif event.type == pygame.locals.MOUSEMOTION:
                LIQUID_TEST.mx = event.pos[0]
                LIQUID_TEST.my = event.pos[1]
        # advance simulation
        LIQUID_TEST.simulate()

profiler = LineProfiler()
profiler.add_function(LiquidTest._step1)
profiler.add_function(LiquidTest._step2)
profiler.add_function(LiquidTest._step3)
profiler.add_function(LiquidTest._step4)
if __name__ == "__main__":
    profiler.runctx("main(100)", globals(), locals())
    stats = open("liquid.txt", 'w')
    profiler.print_stats(stats)

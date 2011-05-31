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
import math
import random
from array import array

RANGE = range(3)
RANGE2 = [(i, j) for i in RANGE for j in RANGE]

class LiquidTest:
    def __init__ (self, width, height, particlesX, particlesY):
        self.width = width
        self.height = height
        self.active = set()
        self.water = Material(3, 1.0, 1.0, 1.0, 1.0, 1.0)
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

    @staticmethod
    def _equation1(value):
        '''Returns two lists of lenth 3.'''
        x = float(value)
        pressure = [0.0, 0.0, 0.0]
        gravity = [0.0, 0.0, 0.0]
        pressure[0] = 0.5 * x * x + 1.5 * x + 1.125
        gravity[0] = x + 1.5
        x += 1.0
        pressure[1] = -x * x + 0.75
        gravity[1] = -2.0 * x
        x += 1.0
        pressure[2] = 0.5 * x * x - 1.5 * x + 1.125
        gravity[2] = x - 1.5
        return pressure, gravity
        
    def _step1(self):
        for particle in self.particles:
            particle.cx = int(particle.x - 0.5)
            particle.cy = int(particle.y - 0.5)
            
            particle.px, particle.gx = self._equation1(particle.cx - particle.x)

            particle.py, particle.gy = self._equation1(particle.cy - particle.y)
            
            for i, j in RANGE2:
                n = self.grid[particle.cx + i][particle.cy + j]
                if not n.active:
                    n.active = True
                    self.active.add(n)
                phi = particle.px[i] * particle.py[j]
                n.m += phi * particle.material.m
                n.d += phi
                n.gx += particle.gx[i] * particle.py[j]
                n.gy += particle.px[i] * particle.gy[j]

    def _density_summary(self, drag, mdx, mdy):       
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
                vx = math.fabs(p.x - self.mx)
                vy = math.fabs(p.y - self.my)
                if  vx < 10.0 > vy:
                    weight = p.material.m * (1.0 - vx * 0.10) * (1.0 - vy * 0.10)
                    fx += weight * (mdx - p.u)
                    fy += weight * (mdy - p.v)

            for i, j in RANGE2:
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
            for i, j in RANGE2:
                    n = self.grid[p.cx + i][p.cy + j]
                    phi = p.px[i] * p.py[j]
                    p.u += phi * n.ax
                    p.v += phi * n.ay
            mu = p.material.m * p.u
            mv = p.material.m * p.v
            for i, j in RANGE2:
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
            for i,j  in RANGE2:
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
                p.x = self.width - 3 - random.random() * 0.01
                p.u = 0.0
            if p.y < 1.0:
                p.y = 1.0 + random.random() * 0.01
                p.v = 0.0
            elif p.y > self.height - 2:
                p.y = self.height - 3 - random.random() * 0.01
                p.v = 0.0

    def simulate(self):
        drag = False
        mdx = mdy = 0.0
        
        if self.pressed and self.pressedprev:
            drag = True
            mdx = self.mx - self.mxprev
            mdy = self.my - self.myprev

        self.pressedprev = self.pressed
        self.mxprev = self.mx
        self.myprev = self.my

        for node in self.active:
            node.__init__()
        self.active.clear()

        self._step1()
        
        self._density_summary(drag, mdx, mdy)
        
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
        self.cx = 0
        self.cy = 0
        self.px = array('f', [0.0, 0.0, 0.0])
        self.py = array('f', [0.0, 0.0, 0.0])
        self.gx = array('f', [0.0, 0.0, 0.0])
        self.gy = array('f', [0.0, 0.0, 0.0])
        
        self.material = material
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        try:
            self.color = pygame.Color(0, 0, 255, 255)
        except NameError:
            self.color = (0, 0, 255, 255)
        

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

def pygame_main(liquid):
    import pygame
    import pygame.locals
    pygame.init()
    canvas = pygame.display.set_mode((liquid.width*4, liquid.height*4), pygame.DOUBLEBUF)
    while True:
        # clear
        canvas.fill(0, (3, 3, liquid.width*4-4, liquid.height*4-4))
        # draw simulation state
        for p in liquid.particles:
            pygame.draw.line(
                canvas, p.color, (4*p.x, 4*p.y,), (4*(p.x - p.u), 4*(p.y - p.v))
                )
        pygame.display.flip()
        #get events
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                liquid.pressed = True
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                liquid.pressed = False
            elif event.type == pygame.locals.MOUSEMOTION:
                liquid.mx = event.pos[0]/4
                liquid.my = event.pos[1]/4
        # advance simulation
        liquid.simulate()

def analytical_main(n = 200):
    global LIQUID_TEST
    LIQUID_TEST = LiquidTest(WIDTH, HEIGHT, PARTICLESX, PARTICLESY)
    times = []
    for i in range(n):
        t1 = time.time()
        LIQUID_TEST.simulate()
        times.append((t1,time.time()))
    total = 0.0
    for frame in times:
        total += frame[1] - frame[0]
    print "Total time: {0}".format((total))
    print "Average time: {0}".format((total/len(times)))

def pyglet_main(liquid):
    from pyglet.window import mouse, Screen, key
    from pyglet import gl, clock, app, graphics
    import pyglet.window
    import threading
    window = pyglet.window.Window(
        width = liquid.width * 4, height = liquid.height * 4
    )
    @window.event
    def on_draw():
        window.clear()
        vertices = []
        colors = []
        for p in liquid.particles:
            vertices.extend([p.x, p.y, p.x - p.u, p.y - p.v])
            colors.extend(p.color[:-1])
            colors.extend([0, 0, 0])
        graphics.draw(
            len(liquid.particles)*2,
            gl.GL_LINES,
            ('v2f', vertices),
            ('c3B', colors)
        )
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, liquid.width, liquid.height, 0, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button == mouse.LEFT:
            liquid.mx = x/4
            liquid.my = liquid.height - y/4
            liquid.pressed = True
    
    @window.event
    def on_mouse_release(x, y, button, modifiers):
        liquid.pressed = False
    
    @window.event
    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        if button == mouse.LEFT:
            liquid.mx = x/4
            liquid.my = liquid.height - y/4
            
    stop = threading.Event()
    def loop(lt, stop):
        while True:
            lt.simulate()
            if stop.is_set():
                break
    
    def induce_paint(dt):
        pass
    
    worker = threading.Thread(target=loop, args=(liquid, stop))
    clock.schedule_interval(induce_paint, 1.0/30.0)
    worker.start()
    app.run()
    stop.set()
    worker.join()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog='Liquid.py',
        description='Material Point Method liquid simulation',
    )
    parser.add_argument('--width', help='The width of the simulation area', default=100)
    parser.add_argument('--height', help='The height of the simulation area', default=100)
    parser.add_argument('--columns', help='The number of particle columns', default=50)
    parser.add_argument('--rows', help='The number of particle rows', default=80)
    parser.add_argument('--n', help='The number of iterations to run the simulation.', 
        default=200)
    parser.add_argument('-i', '--interactive', 
        help='Run the simulation through an interactive pygame or pyglet interface',
        choices=['pygame', 'pyglet'])
    args = parser.parse_args()
    LIQUID_TEST = LiquidTest(args.width, args.height, args.columns, args.rows)
    if args.interactive == 'pygame':
        pygame_main(LIQUID_TEST)
    elif args.interactive == 'pyglet':
        pyglet_main(LIQUID_TEST)
    else:
        import timeit
        timer = timeit.Timer('LIQUID_TEST.simulate()', setup='from __main__ import LIQUID_TEST')
        total = timer.timeit(args.n)
        print "Total simulation time: {0}".format(total)
        print "Average simulation frame time: {0}".format(total/args.n)

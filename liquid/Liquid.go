/**
 * Liquid.go - Go+SDL port V1 Robert Rasmay
 * MIT License ( http://www.opensource.org/licenses/mit-license.php )
 * 
 * JS version:
 *  Copyright Stephen Sinclair (radarsat1) (http://www.music.mcgill.ca/~sinclair)
 *  MIT License ( http://www.opensource.org/licenses/mit-license.php )
 *  Downloaded from: http://www.music.mcgill.ca/~sinclair/blog
 * 
 * Flash version:
 * Copyright iunpin ( http://wonderfl.net/user/iunpin )
 * MIT License ( http://www.opensource.org/licenses/mit-license.php )
 * Downloaded from: http://wonderfl.net/c/6eu4
 * 
 * 
 * Original Java version:
 * http://grantkot.com/MPM/Liquid.html
 */
package main

import (
	"github.com/neagix/Go-SDL/sdl"
	"math"
	"math/rand"
	"reflect"
	"unsafe"
	"time"
	"fmt"
)

/* Material
 * Some of these parameters are hard to explain in one or two sentences 
 * (and a couple I made up) so I'll also link you to their corresponding 
 * Wikipedia pages. One object I like to compare fluids with is springs. 
 * Everybody is familiar with springs. If you pull on them they'll try to go 
 * back to their original shape. Some springs are stronger and some are weaker 
 * (stiffness and elasticity). Some springs will continue to bounce back and 
 * forth for a long time, while others will quickly slow down and stop (bulk 
 * viscosity and viscosity). If you pull hard enough the spring will break.
 * 
 * Density - Target density for the particles. Higher density makes particles 
 * want to be closer together.
 * 
 * Stiffness - How compressible the fluid is.
 * 
 * Bulk viscosity - Kind of like damping. Another effect it will have is that 
 * it'll smooth out shockwaves.
 * 
 * Elasticity - How fast the fluid will try to return to its original shape.
 * 
 * Viscosity - Kind of like bulk viscosity only this operates on the shear 
 * components.
 * 
 * Yield rate - How fast the fluid forgets its shape or melts away. Only 
 * affects things when elasticity is non-zero.
 * 
 * Gravity - How much the particles will accelerate downwards.
 * 
 * Smoothing - Smooths the velocity field. Will make things more stable. It is 
 * also useful to have a high smoothing value when simulating elastic 
 * materials.
 */

type Material struct {
	m  float64
	rd float64
	k  float64
	v  float64
	d  float64
	g  float64
}

type Node struct {
	m      float64
	d      float64
	gx     float64
	gy     float64
	u      float64
	v      float64
	ax     float64
	ay     float64
	active bool
}

// Particles are value holders that manage the mathematical and physical
// attributes of an object
type Particle struct {
	material *Material
	x        float64
	y        float64
	u        float64
	v        float64
	cx       float64
	cy       float64
	px       [3]float64
	py       [3]float64
	gx       [3]float64
	gy       [3]float64
	color    sdl.Color
}

func MakeParticle(material *Material, x, y, u, v float64) *Particle {
	return &Particle{
		material, x, y, u, v, 0.0, 0.0, [3]float64{}, [3]float64{}, [3]float64{},
		[3]float64{}, sdl.Color{0, 0, 255, 255}}
}

type MouseState struct {
    pressed bool
    x       float64
    y       float64
}

type Liquid struct {
	width       float64
	height      float64
	pressed     bool
	pressedprev bool
	mouse       MouseState
	grid        [][]*Node
	particles   []*Particle
}

func MakeLiquid(width, height, rows, columns int) *Liquid {
	grid := make([][]*Node, width)
	for i := 0; i < height; i++ {
		grid[i] = make([]*Node, height)
		for j := 0; j < width; j++ {
			grid[i][j] = new(Node)
		}
	}
	water := &Material{1.0, 1.0, 1.0, 1.0, 1.0, 1.0}
	particles := make([]*Particle, rows*columns)
	for r := 0; r < rows; r++ {
		for c := 0; c < columns; c++ {
			particles[r*columns+c] = MakeParticle(water, float64(r), float64(c), 0.0, 0.0)
		}
	}
	return &Liquid{
		float64(width),
		float64(height),
		false,
		false,
		MouseState{false, 0.0, 0.0},
		grid,
		particles,
	}

}

func _equation1(pressure, gravity *[3]float64, x float64) {
	pressure[0] = 0.5*x*x + 1.5*x + 1.125
	gravity[0] = x + 1.5
	x += 1.0
	pressure[1] = -x*x + 0.75
	gravity[1] = -2.0 * x
	x += 1.0
	pressure[2] = 0.5*x*x - 1.5*x + 1.125
	gravity[2] = x - 1.5
}

func (l *Liquid) _step1() {
	for _, particle := range l.particles {
		particle.cx = float64(int(particle.x - 0.5))
		particle.cy = float64(int(particle.y - 0.5))

		_equation1(&particle.px, &particle.gx, particle.cx-particle.x)

		_equation1(&particle.py, &particle.gy, particle.cy-particle.y)

		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid[int(particle.cx)+i][int(particle.cy)+j]
				if n.active != true {
					n.active = true
				}
				phi := particle.px[i] * particle.py[j]
				n.m += phi * particle.material.m
				n.d += phi
				n.gx += particle.gx[i] * particle.py[j]
				n.gy += particle.px[i] * particle.gy[j]
			}
		}
	}
}

func (l *Liquid) _density_summary(drag bool, mdx, mdy float64) {
	var n01, n02, n11, n12 *Node
	var cx, cy, cxi, cyi int
	var pdx, pdy, C20, C02, C30, C03, csum1, csum2, C21, C31,
		C12, C13, C11, density, pressure, fx, fy, u, u2, u3, v, v2, v3 float64
	for _, p := range l.particles {
		cx = int(p.x)
		cy = int(p.y)
		cxi = cx + 1
		cyi = cy + 1

		n01 = l.grid[cx][cy]
		n02 = l.grid[cx][cyi]
		n11 = l.grid[cxi][cy]
		n12 = l.grid[cxi][cyi]

		pdx = n11.d - n01.d
		pdy = n02.d - n01.d
		C20 = 3.0*pdx - n11.gx - 2.0*n01.gx
		C02 = 3.0*pdy - n02.gy - 2.0*n01.gy
		C30 = -2.0*pdx + n11.gx + n01.gx
		C03 = -2.0*pdy + n02.gy + n01.gy
		csum1 = n01.d + n01.gy + C02 + C03
		csum2 = n01.d + n01.gx + C20 + C30
		C21 = 3.0*n12.d - 2.0*n02.gx - n12.gx - 3.0*csum1 - C20
		C31 = -2.0*n12.d + n02.gx + n12.gx + 2.0*csum1 - C30
		C12 = 3.0*n12.d - 2.0*n11.gy - n12.gy - 3.0*csum2 - C02
		C13 = -2.0*n12.d + n11.gy + n12.gy + 2.0*csum2 - C03
		C11 = n02.gx - C13 - C12 - n01.gx

		u = p.x - float64(cx)
		u2 = u * u
		u3 = u * u2
		v = p.y - float64(cy)
		v2 = v * v
		v3 = v * v2
		density = (n01.d + n01.gx*u + n01.gy*v + C20*u2 + C02*v2 +
			C30*u3 + C03*v3 + C21*u2*v + C31*u3*v + C12*u*
			v2 + C13*u*v3 + C11*u*v)

		pressure = density - 1.0
		if pressure > 2.0 {
			pressure = 2.0
		}

		fx = 0.0
		fy = 0.0

		if p.x < 4.0 {
			fx += p.material.m * (4.0 - p.x)
		} else if p.x > l.width-5 {
			fx += p.material.m * (l.width-5 - p.x)
		}
		if p.y < 4.0 {
			fy += p.material.m * (4.0 - p.y)
		} else if p.y > l.height-5 {
			fy += p.material.m * (l.height-5 - p.y)
		}

		if drag {
			vx := math.Abs(p.x - l.mouse.x)
			vy := math.Abs(p.y - l.mouse.y)
			if vx < 10.0 && 10.0 > vy {
				weight := (p.material.m * (1.0 - vx*0.10) *
					(1.0 - vy*0.10))
				fx += weight * (mdx - p.u)
				fy += weight * (mdy - p.v)
			}
		}
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid[int(p.cx)+i][int(p.cy)+j]
				phi := p.px[i] * p.py[j]
				n.ax += -(p.gx[i] * p.py[j] * pressure) + fx*phi
				n.ay += -(p.px[i] * p.gy[j] * pressure) + fy*phi
			}
		}
	}
}
func (l *Liquid) _step3() {
	var mu, mv float64
	for _, p := range l.particles {
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid[int(p.cx)+i][int(p.cy)+j]
				phi := p.px[i] * p.py[j]
				p.u += phi * n.ax
				p.v += phi * n.ay
			}
		}

		mu = p.material.m * p.u
		mv = p.material.m * p.v
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid[int(p.cx)+i][int(p.cy)+j]
				phi := p.px[i] * p.py[j]
				n.u += phi * mu
				n.v += phi * mv
			}
		}
	}
}
func (l *Liquid) _step4() {
	var gu, gv float64
	for _, p := range l.particles {
		gu = 0.0
		gv = 0.0
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid[int(p.cx)+i][int(p.cy)+j]
				phi := p.px[i] * p.py[j]
				gu += phi * n.u
				gv += phi * n.v
			}
		}
		p.x += gu
		p.y += gv
		p.u += 1.0 * (gu - p.u)
		p.v += 1.0 * (gv - p.v)
		if p.x < 1.0 {
			p.x = 1.0 + rand.Float64()*0.01
			p.u = 0.0
		} else if p.x > l.width-2 {
			p.x = l.width - 3 - rand.Float64()*0.01
			p.u = 0.0
		}
		if p.y < 1.0 {
			p.y = 1.0 + rand.Float64()*0.01
			p.v = 0.0
		} else if p.y > l.height-2 {
			p.y = l.height - 3 - rand.Float64()*0.01
			p.v = 0.0
		}
	}
}


func (l *Liquid) simulate(mouse MouseState) {

	drag := false
	mdx := float64(0.0)
	mdy := float64(0.0)
	if mouse.pressed && l.mouse.pressed {
		drag = true
		mdx = mouse.x - l.mouse.x
		mdy = mouse.y - l.mouse.y
	}
	l.mouse = mouse

	for i := 0; i < int(l.height); i++ {
		for j := 0; j < int(l.width); j++ {
			if l.grid[i][j].active {
				l.grid[i][j] = new(Node)
			}
		}
	}
	l._step1()
	l._density_summary(drag, mdx, mdy)

	for i := 0; i < int(l.height); i++ {
		for j := 0; j < int(l.width); j++ {
		    if l.grid[i][j].active && l.grid[i][j].m > 0.0 {
    			l.grid[i][j].ax /= l.grid[i][j].m
	    		l.grid[i][j].ay /= l.grid[i][j].m
	    		l.grid[i][j].ay += 0.03	    
		    }
		}
	}

	l._step3()
	
	for i := 0; i < int(l.height); i++ {
		for j := 0; j < int(l.width); j++ {
		    if l.grid[i][j].active && l.grid[i][j].m > 0.0 {
    			l.grid[i][j].u /= l.grid[i][j].m
	    		l.grid[i][j].v /= l.grid[i][j].m
		    }
		}
	}

	l._step4()
}

type Surface struct {
	surface *sdl.Surface
	pixels  []uint32
}

func MakeSurface(surf *sdl.Surface) *Surface {
	surf.Lock() // Get Lock before creating the surface slice.
	surface := &Surface{surf, nil}
	sliceHeader := (*reflect.SliceHeader)((unsafe.Pointer(&surface.pixels)))
	sliceHeader.Cap = int(surf.H * surf.W)
	sliceHeader.Len = int(surf.H * surf.W)
	sliceHeader.Data = uintptr(unsafe.Pointer(surf.Pixels))
	surf.Unlock()
	return surface
}

func DrawLine(surf *Surface, color sdl.Color, x1, y1, x2, y2 float64) {
	surf.surface.Lock() // Get Lock before creating the surface slice.

	dx := float64(math.Abs(float64(x2 - x1)))
	dy := float64(math.Abs(float64(y2 - y1)))
	var sx, sy int
	if x1 < x2 {
		sx = 1
	} else {
		sx = -1
	}
	if y1 < y2 {
		sy = 1
	} else {
		sy = -1
	}
	err := dx - dy
	for i := 0; i < 5; i++ {
		if x1 < 0 || y1 < 0 {
			break
		}
		if int32(x1) >= surf.surface.W || int32(y1) >= surf.surface.H {
			break
		}
		surf.pixels[int32(y1)*surf.surface.W+int32(x1)] = sdl.MapRGBA(
			surf.surface.Format, color.R, color.G, color.B, color.Unused)
		if int(x1) == int(x2) && int(y1) == int(y2) {
			break
		}
		e2 := 2 * err
		if e2 > -dy {
			err = err - dy
			x1 = x1 + float64(sx)
		}
		if e2 < dx {
			err = err + dx
			y1 = y1 + float64(sy)
		}
	}
	surf.surface.Unlock()
}

func DrawLinePrelocked(surf *Surface, color sdl.Color, x1, y1, x2, y2 float64) {
	dx := float64(math.Abs(float64(x2 - x1)))
	dy := float64(math.Abs(float64(y2 - y1)))
	var sx, sy int
	if x1 < x2 {
		sx = 1
	} else {
		sx = -1
	}
	if y1 < y2 {
		sy = 1
	} else {
		sy = -1
	}
	err := dx - dy
	for i := 0; i < 5; i++ {
		if x1 < 0 || y1 < 0 {
			break
		}
		if int32(x1) >= surf.surface.W || int32(y1) >= surf.surface.H {
			break
		}
		surf.pixels[int32(y1)*surf.surface.W+int32(x1)] = sdl.MapRGBA(
			surf.surface.Format, color.R, color.G, color.B, color.Unused)
		if int(x1) == int(x2) && int(y1) == int(y2) {
			break
		}
		e2 := 2 * err
		if e2 > -dy {
			err = err - dy
			x1 = x1 + float64(sx)
		}
		if e2 < dx {
			err = err + dx
			y1 = y1 + float64(sy)
		}
	}
}

/**
 * The main loop for the pygame interface. The pygame window will be 4 
 * times wider and 4 times taller than the width and height of the liquid 
 * simulation. It uses a standard double buffered sdl window. With pygame the
 * simulation speed and the framerate are locked together. You can use the
 * mouse to click and drag around the particles.
 */
func SdlMain(l *Liquid) {
	if sdl.Init(sdl.INIT_EVERYTHING) != 0 {
		panic(sdl.GetError())
	}

	defer sdl.Quit()

	canvas := sdl.SetVideoMode(int(l.width)*4, int(l.height)*4, 32, 0)

	if canvas == nil {
		panic(sdl.GetError())
	}
	
	surf := MakeSurface(canvas)
	mouse := MouseState{false, 0.0, 0.0}
	//mch := make(chan MouseState)
	eventtime := int64(0)
	simulatetime := int64(0)
	drawtime := int64(0)
	start := time.Now()
	t1 := time.Now()
	for frames := 0; ; frames++{
	    t1 = time.Now()
		select {		
		case event := <-sdl.Events:
			switch e := event.(type) {
			case sdl.QuitEvent:
			    fmt.Printf("%v frames\n", frames)
			    fmt.Printf("%v frames/s\n", float64(frames)/time.Since(start).Seconds())
			    fmt.Printf("%v time polling events\n", time.Duration(eventtime))
			    fmt.Printf("%v time simulating\n", time.Duration(simulatetime))
			    fmt.Printf("%v time drawing\n", time.Duration(drawtime))
				return
			case sdl.MouseButtonEvent:
				if e.State == sdl.PRESSED {
					mouse.pressed = true
				}
				if e.State == sdl.RELEASED {
					mouse.pressed = false
				}
			case sdl.MouseMotionEvent:
				mouse.x = float64(e.X / 4)
				mouse.y = float64(e.Y / 4)
			}
		default:
		    mouse.pressed = mouse.pressed
		}
		eventtime += time.Since(t1).Nanoseconds()
		
		t1 = time.Now()
        l.simulate(mouse)
        simulatetime += time.Since(t1).Nanoseconds()
		
		t1 = time.Now()
        canvas.FillRect(nil, 0x000000)
	    //draw simulation state
	    surf.surface.Lock()
	    for _, p := range l.particles {
		    DrawLinePrelocked(
			    surf,
			    p.color,
			    4*p.x, 4*p.y,
			    4*(p.x-p.u), 4*(p.y-p.v),
		    )
	    }
	    surf.surface.Unlock()
	    canvas.Flip()
		drawtime += time.Since(t1).Nanoseconds()
	}
}

func main() {
	/*
	   import argparse
	   PARSER = argparse.ArgumentParser(
	       prog='Liquid.py',
	       description='Material Point Method liquid simulation',
	   )
	   PARSER.add_argument('--width', 
	       help='The width of the simulation area', default=100)
	   PARSER.add_argument('--height', 
	       help='The height of the simulation area', default=100)
	   PARSER.add_argument('--columns', 
	       help='The number of particle columns', default=50)
	   PARSER.add_argument('--rows', 
	       help='The number of particle rows', default=80)
	   PARSER.add_argument('--n', 
	       help='The number of iterations to run the simulation.', 
	       default=200)
	   PARSER.add_argument('-i', '--interactive', 
	       help='Run the simulation interactively with pygame or pyglet',
	       choices=['pygame', 'pyglet'])
	   ARGS = PARSER.parse_args()
	*/
	liquid := MakeLiquid(100, 100, 50, 50)
	SdlMain(liquid)
}

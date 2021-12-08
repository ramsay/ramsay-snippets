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
	"fmt"
	"github.com/veandco/go-sdl2/sdl"
	"image/color"
	"math/rand"
	"time"
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
	m, rd, k, v, d, g float32
}

type Node struct {
	m, d, gx, gy, u, v, ax, ay float32
	active                     bool
}

// Particle Particles are value holders that manage the mathematical and physical
// attributes of an object
type Particle struct {
	material           *Material
	x, y, u, v, cx, cy float32
	px, py, gx, gy     [3]float32
	color              color.Color
}

func MakeParticle(material *Material, x, y, u, v float32) *Particle {
	return &Particle{
		material: material,
		x:        x,
		y:        y,
		u:        u,
		v:        v,
		color:    color.RGBA{B: 255, A: 255}}
}

type MouseState struct {
	pressed bool
	x, y    float32
}

type Liquid struct {
	width       float32
	height      float32
	pressed     bool
	pressedprev bool
	mouse       MouseState
	grid        *Nodemap
	particles   []*Particle
}

type Nodemap struct {
	width, height int
	nodes         []*Node
}

func NewNodemap(width int, height int) *Nodemap {
	nodes := make([]*Node, (width+1)*(height+1))
	for i := range nodes {
		nodes[i] = new(Node)
	}
	return &Nodemap{
		width:  width,
		height: height,
		nodes:  nodes,
	}
}

func (nm *Nodemap) GetNode(x, y int) *Node {
	return nm.nodes[nm.width*y+x]
}

func (nm *Nodemap) Reset() {
	emptyNode := &Node{}
	for i := range nm.nodes {
		*(nm.nodes[i]) = *emptyNode
	}
}

func MakeLiquid(width, height, rows, columns int) *Liquid {
	water := &Material{1.0, 1.0, 1.0, 1.0, 1.0, 1.0}
	particles := make([]*Particle, rows*columns)
	for r := 0; r < rows; r++ {
		for c := 0; c < columns; c++ {
			particles[r*columns+c] = MakeParticle(water, float32(r), float32(c), 0.0, 0.0)
		}
	}
	return &Liquid{
		float32(width),
		float32(height),
		false,
		false,
		MouseState{false, 0.0, 0.0},
		NewNodemap(width, height),
		particles,
	}

}

func _equation1(pressure, gravity *[3]float32, x float32) {
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
		particle.cx = float32(int(particle.x - 0.5))
		particle.cy = float32(int(particle.y - 0.5))

		_equation1(&particle.px, &particle.gx, particle.cx-particle.x)

		_equation1(&particle.py, &particle.gy, particle.cy-particle.y)

		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid.GetNode(int(particle.cx)+i, int(particle.cy)+j)
				// n := l.grid[int(particle.cx)+i][int(particle.cy)+j]
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

func (l *Liquid) _density_summary(drag bool, mdx, mdy float32) {
	var n01, n02, n11, n12 *Node
	var cx, cy, cxi, cyi int
	var pdx, pdy, C20, C02, C30, C03, csum1, csum2, C21, C31,
		C12, C13, C11, density, pressure, fx, fy, u, u2, u3, v, v2, v3 float32
	for _, p := range l.particles {
		cx = int(p.x)
		cy = int(p.y)
		cxi = cx + 1
		cyi = cy + 1

		n01 = l.grid.GetNode(cx, cy)
		n02 = l.grid.GetNode(cx, cyi)
		n11 = l.grid.GetNode(cxi, cy)
		n12 = l.grid.GetNode(cxi, cyi)

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

		u = p.x - float32(cx)
		u2 = u * u
		u3 = u * u2
		v = p.y - float32(cy)
		v2 = v * v
		v3 = v * v2
		density = n01.d + n01.gx*u + n01.gy*v + C20*u2 + C02*v2 +
			C30*u3 + C03*v3 + C21*u2*v + C31*u3*v + C12*u*
			v2 + C13*u*v3 + C11*u*v

		pressure = density - 1.0
		if pressure > 2.0 {
			pressure = 2.0
		}

		fx = 0.0
		fy = 0.0

		if p.x < 4.0 {
			fx += p.material.m * (4.0 - p.x)
		} else if p.x > l.width-5 {
			fx += p.material.m * (l.width - 5 - p.x)
		}
		if p.y < 4.0 {
			fy += p.material.m * (4.0 - p.y)
		} else if p.y > l.height-5 {
			fy += p.material.m * (l.height - 5 - p.y)
		}

		if drag {
			vx := Abs(p.x - l.mouse.x)
			vy := Abs(p.y - l.mouse.y)
			if vx < 10.0 && 10.0 > vy {
				weight := p.material.m * (1.0 - vx*0.10) *
					(1.0 - vy*0.10)
				fx += weight * (mdx - p.u)
				fy += weight * (mdy - p.v)
			}
		}
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid.GetNode(int(p.cx)+i, int(p.cy)+j)
				phi := p.px[i] * p.py[j]
				n.ax += -(p.gx[i] * p.py[j] * pressure) + fx*phi
				n.ay += -(p.px[i] * p.gy[j] * pressure) + fy*phi
			}
		}
	}
}
func (l *Liquid) _step3() {
	var mu, mv float32
	for _, p := range l.particles {
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid.GetNode(int(p.cx)+i, int(p.cy)+j)
				phi := p.px[i] * p.py[j]
				p.u += phi * n.ax
				p.v += phi * n.ay
			}
		}

		mu = p.material.m * p.u
		mv = p.material.m * p.v
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid.GetNode(int(p.cx)+i, int(p.cy)+j)
				phi := p.px[i] * p.py[j]
				n.u += phi * mu
				n.v += phi * mv
			}
		}
	}
}
func (l *Liquid) _step4() {
	var gu, gv float32
	for _, p := range l.particles {
		gu = 0.0
		gv = 0.0
		for i := 0; i < 3; i++ {
			for j := 0; j < 3; j++ {
				n := l.grid.GetNode(int(p.cx)+i, int(p.cy)+j)
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
			p.x = 1.0 + rand.Float32()*0.01
			p.u = 0.0
		} else if p.x > l.width-2 {
			p.x = l.width - 3 - rand.Float32()*0.01
			p.u = 0.0
		}
		if p.y < 1.0 {
			p.y = 1.0 + rand.Float32()*0.01
			p.v = 0.0
		} else if p.y > l.height-2 {
			p.y = l.height - 3 - rand.Float32()*0.01
			p.v = 0.0
		}
	}
}

func (l *Liquid) simulate(mouse MouseState) {

	drag := false
	mdx := float32(0.0)
	mdy := float32(0.0)
	if mouse.pressed && l.mouse.pressed {
		drag = true
		mdx = mouse.x - l.mouse.x
		mdy = mouse.y - l.mouse.y
	}
	l.mouse = mouse

	// Set all nodes back to empty state
	l.grid.Reset()
	l._step1()
	l._density_summary(drag, mdx, mdy)

	for i := 0; i < int(l.height); i++ {
		for j := 0; j < int(l.width); j++ {
			n := l.grid.GetNode(i, j)
			if n.active && n.m > 0.0 {

			}
			//if l.grid[i][j].active && l.grid[i][j].m > 0.0 {
			//	l.grid[i][j].ax /= l.grid[i][j].m
			//	l.grid[i][j].ay /= l.grid[i][j].m
			//	l.grid[i][j].ay += 0.03
			//}
		}
	}

	l._step3()

	for i := 0; i < int(l.height); i++ {
		for j := 0; j < int(l.width); j++ {
			n := l.grid.GetNode(i, j)
			if n.active && n.m > 0.0 {
				n.u /= n.m
				n.v /= n.m
			}
		}
	}

	l._step4()
}

func Abs(val float32) float32 {
	if val < 0 {
		return val * -1.0
	}
	return val
}

func DrawLine(surf *sdl.Surface, color color.Color, x1, y1, x2, y2 float32) {
	surf.Lock() // Get Lock before creating the surface slice.
	var (
		dx = Abs(x2 - x1)
		dy = Abs(y2 - y1)
		sx = float32(-1)
		sy = float32(-1)
	)
	if x1 < x2 {
		sx = 1
	}
	if y1 < y2 {
		sy = 1
	}

	err := dx - dy
	for i := 0; i < 5; i++ {
		if x1 < 0 || y1 < 0 {
			break
		}
		if int32(x1) >= surf.W || int32(y1) >= surf.H {
			break
		}
		surf.Set(int(x1), int(y1), color)
		//pixels[int32(y1)*surf.W+int32(x1)] = sdl.MapRGBA(
		//	surf.Format, color.R, color.G, color.B, 1)
		if int(x1) == int(x2) && int(y1) == int(y2) {
			break
		}
		e2 := 2 * err
		if e2 > -dy {
			err = err - dy
			x1 = x1 + sx
		}
		if e2 < dx {
			err = err + dx
			y1 = y1 + sy
		}
	}
	surf.Unlock()
}

func DrawLinePrelocked(surf *sdl.Surface, color color.Color, x1, y1, x2, y2 float32) {
	var (
		dx = Abs(x2 - x1)
		dy = Abs(y2 - y1)
		sx = float32(-1)
		sy = float32(-1)
	)
	if x1 < x2 {
		sx = 1
	}
	if y1 < y2 {
		sy = 1
	}
	err := dx - dy
	for i := 0; i < 5; i++ {
		if x1 < 0 || y1 < 0 {
			break
		}
		if int32(x1) >= surf.W || int32(y1) >= surf.H {
			break
		}
		surf.Set(int(x1), int(y1), color)
		// pixels[int32(y1)*surf.W+int32(x1)] = sdl.MapRGBA(surf.Format, color.R, color.G, color.B, 1)
		if int(x1) == int(x2) && int(y1) == int(y2) {
			break
		}
		e2 := 2 * err
		if e2 > -dy {
			err = err - dy
			x1 = x1 + sx
		}
		if e2 < dx {
			err = err + dx
			y1 = y1 + sy
		}
	}
}

func renderloop(stats *Stats, surf *sdl.Surface, renderer *sdl.Renderer, l *Liquid, mouse *MouseState, done chan bool) {
	ticker := time.NewTicker(50 * time.Millisecond)
	for stats.running {
		select {
		case <-ticker.C:
			stats.frames++
			stats.t = time.Now()
			l.simulate(*mouse)
			stats.simulateSeconds += time.Since(stats.t).Nanoseconds()

			stats.t = time.Now()
			//draw simulation state
			_ = surf.Lock()
			renderer.SetDrawColor(0, 0, 0, 255)
			renderer.FillRect(nil)
			renderer.SetDrawColor(0, 0, 255, 255)
			for _, p := range l.particles {
				_ = renderer.DrawLineF(4*p.x, 4*p.y, 4*(p.x-p.u), 4*(p.y-p.v))
			}
			surf.Unlock()
			renderer.Present()
			stats.drawSeconds += time.Since(stats.t).Nanoseconds()
		}
	}
	done <- true
}

type Stats struct {
	t               time.Time
	frames          int
	simulateSeconds int64
	drawSeconds     int64
	running         bool
}

// SdlMain /**
func SdlMain(l *Liquid) {
	if err := sdl.Init(sdl.INIT_EVERYTHING); err != nil {
		panic(err)
	}
	defer sdl.Quit()

	var (
		window   *sdl.Window
		surf     *sdl.Surface
		renderer *sdl.Renderer
		err      error
		stats    = Stats{running: true}
		mouse    = &MouseState{}
	)

	if window, err = sdl.CreateWindow(
		"test", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED,
		int32(l.width)*4, int32(l.height)*4, sdl.WINDOW_SHOWN); err != nil {
		panic(err)
	}
	defer window.Destroy()

	if surf, err = window.GetSurface(); err != nil {
		panic(err)
	}

	if renderer, err = window.GetRenderer(); err != nil {
		panic(err)
	}
	//if renderer, err = sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED); err != nil {
	//	_, _ = fmt.Fprintf(os.Stderr, "Failed to create renderer: %s\n", err)
	//	return // don't use os.Exit(3); otherwise, previous deferred calls will never run
	//}
	//renderer.Clear()
	//defer renderer.Destroy()
	//_ = surf.FillRect(nil, 0)
	//mch := make(chan MouseState)
	start := time.Now()
	renderDone := make(chan bool)

	go renderloop(&stats, surf, renderer, l, mouse, renderDone)

	for stats.running {
		for event := sdl.PollEvent(); event != nil; event = sdl.PollEvent() {
			switch e := event.(type) {
			case *sdl.QuitEvent:
				stats.running = false
				break
			case *sdl.MouseButtonEvent:
				if e.State == sdl.PRESSED {
					fmt.Println("Mouse pressed")
					// mouse.pressed = true
				}
				if e.State == sdl.RELEASED {
					fmt.Println("Mouse released")
					// mouse.pressed = false
				}
			case *sdl.MouseMotionEvent:
				fmt.Printf("Mouse motion = (%d, %d)\n", e.X/4, e.Y/4)
				// mouse.x = float32(e.X / 4)
				// mouse.y = float32(e.Y / 4)
			}
			// eventtime += time.Since(t1).Nanoseconds()
		}
	}

	// Wait for last render loop to finish
	<-renderDone

	fmt.Printf("%v frames\n", stats.frames)
	fmt.Printf("%v frames/s\n", float64(stats.frames)/time.Since(start).Seconds())
	// fmt.Printf("%v time polling events\n", time.Duration(eventtime))
	fmt.Printf("%v time simulating\n", time.Duration(stats.simulateSeconds))
	fmt.Printf("%v time drawing\n", time.Duration(stats.drawSeconds))
}

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
func main() {
	liquid := MakeLiquid(100, 100, 50, 50)
	SdlMain(liquid)
}

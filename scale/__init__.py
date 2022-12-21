import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import math
import json


erase = None
X,Y = 0,1
### Physics collision types
COLLTYPE_DEFAULT = 0
COLLTYPE_MOUSE = 1
COLLTYPE_RECT = 2
WIDTH = 1000
HEIGHT = 600
PX = 400
PY = 450
SCALE = 1

RECT_DEFAULT_HEIGHT=20.0
SCALESPEED = 0.0

SIZE = 20
TORQUE = 70000.0


def mouse_coll_func(arbiter, space, data):
    global erase

    s2 = arbiter.shapes[1]
    if s2.collision_type != COLLTYPE_MOUSE and (type(s2) == pm.Segment or type(s2)==pm.Poly):
        #s2.radius += 0.15
        erase = s2
        
    return False


def world2screen(v):
    x,y = v.x,v.y
    w = WIDTH
    h = HEIGHT
    rx = PX
    ry = PY
    s = SCALE
    return (s*(x-rx)+w/2,-1*s*(y-ry)+h/2)


def screen2world(v):
    x,y = v
    w = WIDTH
    h = HEIGHT
    rx = PX
    ry = PY
    s = SCALE
    return Vec2d((x-w/2)/s + rx,-1*(y-h/2)/s+ry)


def main():
    global erase, PX, PY, SCALE, SIZE, SCALESPEED
       
    pygame.init()
    whooshsnd = pygame.mixer.Sound("res/Whip 04.wav")
    jumpsnd = pygame.mixer.Sound("res/jumpsound.wav")
    bgmsnd = pygame.mixer.Sound("res/bgm.ogg")
    bgmsnd.play(-1)
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    
    ### Physics stuff
    space = pm.Space()
    space.gravity = Vec2d(0.0, -900.0)

    #Make US
    pbody = pm.Body(10, 100)
    pbody.position = PX,PY
    pshape = pm.Circle(pbody, SIZE, Vec2d(0,0))
    pshape.friction = 0.99 #0.5
    space.add(pbody, pshape)

    #bckimg = pygame.image.load("bck.jpg") 
    
    ## Balls
    balls = []
    
    ### Mouse
    mouse_body = pm.Body()
    mouse_shape = pm.Circle(mouse_body, 3, Vec2d(0,0))
    mouse_shape.collision_type = COLLTYPE_MOUSE
    space.add(mouse_body, mouse_shape)
    mouse_handler = space.add_collision_handler(COLLTYPE_MOUSE, COLLTYPE_DEFAULT)
    mouse_handler.begin = mouse_coll_func
    
    ### Static line
    line_point1 = None
    static_lines = []
    static_polys = []
    run_physics = True
    
    direction = 0.0
    
    counter = 0
    lasttime = 0
    
    #GET THE LINES
    try:
        f = open("res/level.json", 'rb')
        saved = json.load(f)
        f.close()
        for s in saved:
            if len(s) == 2:
                a,b = Vec2d(*s[0]), Vec2d(*s[1])
                body = pm.Body(body_type=pm.Body.STATIC)
                shape= pm.Segment(body, a, b, 0.0)
                shape.friction = float('inf')
                space.add(shape)
                static_lines.append(shape)
            elif len(s) == 4:
                pts = [Vec2d(*p) for p in s]
                #pts=map(screen2world,pts)
                body = pm.Body(body_type=pm.Body.STATIC)
                shape = pm.Poly(body, pts)
                shape.friction = 1.0
                space.add(body, shape)
                static_polys.append(shape)

    except Exception as e:
        a,b = Vec2d(-300,100), Vec2d(900,100)
        body = pm.Body(body_type=pm.Body.STATIC)
        shape= pm.Segment(body, a, b, 0.0)
        shape.friction = float('inf')
        space.add(body, shape)
        static_lines.append(shape)

    bckimg = pygame.image.load("res/introscr.jpg")
    screen.blit(bckimg, (0,0))
    pygame.display.flip()
    kgo = False
    while not kgo:
        for event in pygame.event.get():
            if event.type == QUIT:
                kgo = True
                running = False
            if event.type == KEYUP:
                kgo = True
                running = not event.key == K_ESCAPE

    while running:
        counter +=1
        if counter == 100000: counter = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            #elif event.type == KEYDOWN and event.key == K_RIGHT:
                #pbody.torque = -TORQUE
            #elif event.type == KEYUP and event.key == K_RIGHT:
            #    pbody.reset_forces()
            #elif event.type == KEYDOWN and event.key == K_LEFT:
            #    pbody.torque = +TORQUE
            #elif event.type == KEYUP and event.key == K_LEFT:
            #    pbody.reset_forces()
            elif event.type == KEYUP and event.key == K_z:
                #SAVE THE LINES AS ENDPOINTS
                tosave = []
                for l in static_lines:
                    tosave.append([(p.x, p.y) for p in (l.a, l.b)])
                for p in static_polys:
                    tosave.append([(p.x, p.y) for p in p.get_vertices()])
                f = open("res/level.json", 'wb')
                json.dump(tosave, f)
                f.close()

            elif event.type == KEYUP and event.key == K_r:
                PX = 400
                PY = 450
                SCALE = 1
                SIZE = 20
                space.gravity = Vec2d(0.0, -900.0)
                space.remove(pbody, pshape) #2345
                pbody = pm.Body(10, 100)
                pbody.position = 400,450
                pshape = pm.Circle(pbody, SIZE, Vec2d(0,0))
                pshape.friction = 0.99 #0.5
                space.add(pbody, pshape)

            elif event.type == KEYUP and event.key == K_x:
                if erase:
                    if type(erase) == pm.Segment:
                        space.remove(erase)
                        static_lines.remove(erase)
                        erase = None
                    elif type(erase) == pm.Poly:
                        space.remove(erase)
                        static_polys.remove(erase)
                        erase = None

            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            #elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            #    p = screen2world(event.pos)
            #    body = pm.Body(10, 100)
            #    body.position = p
            #    shape = pm.Circle(body, 10, Vec2d(0,0))
            #    shape.friction = 0.5
            #    space.add(body, shape)
            #    balls.append(shape)

            elif event.type == MOUSEBUTTONDOWN and event.button == 3 and not run_physics:
                if line_point1 is None:
                    line_point1 = screen2world(event.pos)

            elif event.type == MOUSEBUTTONDOWN and event.button == 4:
                SCALESPEED = 0.1
                if counter - lasttime > 20:
                    whooshsnd.play()
                    lasttime = counter

            elif event.type == MOUSEBUTTONDOWN and event.button == 5:
                SCALESPEED = -0.1
                if counter - lasttime > 20:
                    whooshsnd.play()
                    lasttime = counter

            elif event.type == MOUSEBUTTONDOWN and event.button == 3 and run_physics:
                jump = False
                l = []

                def get_contacts(arbiter, *args, **kwargs):
                    for cp in arbiter.contact_point_set.points:
                        l.append(cp.point_a)

                pbody.each_arbiter(get_contacts)

                for x in l:
                    a = (Vec2d(PX,PY)-x).get_angle_between(Vec2d(0,1))
                    if abs(a) < 20:
                        jump = True
                if jump:
                    dir = Vec2d(0,1)
                    dir = dir.scale_to_length(450.0/SCALE)
                    pbody.velocity += dir
                    jumpsnd.play()

            elif event.type == MOUSEBUTTONUP and event.button == 1 and pygame.key.get_mods() & KMOD_SHIFT:
                space.remove(pbody, pshape) #2345
                pbody = pm.Body(10, 100)
                pbody.position = screen2world(pygame.mouse.get_pos())
                pshape = pm.Circle(pbody, SIZE, Vec2d(0,0))
                pshape.friction = 0.99 #0.5
                space.add(pbody, pshape)

            elif event.type == MOUSEBUTTONUP and event.button == 3 and not run_physics:
                if line_point1:
                    line_point2 = screen2world(event.pos)

                    #print line_point1, line_point2
                    #body = pm.Body(float('inf'), float('inf'))
                    #shape= pm.Segment(body, line_point1, line_point2, 0.0)
                    #shape.friction = 0.99
                    #space.add_static(shape)
                    #static_lines.append(shape)

                    p1 = Vec2d(*world2screen(line_point1))
                    p2 = Vec2d(*world2screen(line_point2))
                    v = (p2-p1).perpendicular()
                    v = v.scale_to_length(RECT_DEFAULT_HEIGHT)
                    p3 = p1+v
                    p4 = p2+v
                    pts = [p1,p2,p4,p3]
                    pts=list(map(screen2world,pts))

                    body = pm.Body(body_type=pm.Body.STATIC)
                    shape = pm.Poly(body, pts)
                    shape.friction = 1.0
                    space.add(shape)
                    static_polys.append(shape)

                    line_point1 = None
            
            elif event.type == KEYDOWN and event.key == K_p:
                if run_physics:
                    save_scale = SCALE
                else:
                    SCALE = save_scale   
                run_physics = not run_physics
        p = pygame.mouse.get_pos()
        mouse_pos = screen2world(p)
        mouse_body.position = mouse_pos
        mouse_shape.unsafe_set_radius(3/SCALE)
        
        #    body = pm.Body(10, 10)
        #    body.position = mouse_pos
        #    shape = pm.Circle(body, 10, Vec2d(0,0))
        #    space.add(body, shape)
        #    balls.append(shape)
        
        dt = 1.0/60.0
        for x in range(1):
            space.step(dt)
            
        ### Update physics
        if run_physics:

            l = []

            def get_contacts(arbiter, *args, **kwargs):
                for cp in arbiter.contact_point_set.points:
                    l.append(cp.point_a)

            pbody.each_arbiter(get_contacts)

            for x in l:
                for y in l:
                    a = (Vec2d(PX,PY)-x).get_angle_between(Vec2d(PX,PY)-y)
                    if a > 177 and SCALESPEED < 0:
                        #print 'double no'
                        SCALESPEED = 0

            if len(l) > 2:
                for x in l:
                    for y in l:
                        for z in l:
                            a1 = abs((Vec2d(PX,PY)-x).get_angle_between(Vec2d(PX,PY)-y))
                            a2 = abs((Vec2d(PX,PY)-x).get_angle_between(Vec2d(PX,PY)-z))
                            a3 = abs((Vec2d(PX,PY)-y).get_angle_between(Vec2d(PX,PY)-z))
                            s1 = a1 + a2
                            s2 = a1 + a3
                            s3 = a2 + a3
                            s = min(s1,s2,s3)
                            if s > 128 and SCALESPEED < 0:
                                #print 'no'
                                SCALESPEED = 0
                                
            #print space.arbiters    
            #for arb in space.arbiters:
                #print arb.contacts
                #if arb.a == pshape:
                #    print arb.contacts
                #    l = [c.position for c in arb.contacts]
                #    print l
            
            ### Update the position of the camera
            PX,PY = pbody.position
            if SCALE > 1800 and SCALESPEED > 0: SCALESPEED = 0
            
            
            SCALESPEED = SCALESPEED/1.2
            SIZE *= 1/(SCALESPEED+1.0)
            space.gravity *= 1/(SCALESPEED+1.0)
            SCALE *= SCALESPEED+1.0
            pshape.unsafe_set_radius(SIZE)
            pbody.mass = SIZE*SIZE/40.0
            pbody.moment = pm.moment_for_circle(pbody.mass,0,pshape.radius)

            maxv=-100.0
            
            direction = 0.0
            if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[0] < WIDTH/2:
                if pbody.angular_velocity < 40:
                    pbody.angular_velocity += 7
            if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[0] > WIDTH/2:
                if pbody.angular_velocity > -40:
                    pbody.angular_velocity -= 7
            #pbody.torque = direction*TORQUE*min((pbody.angular_velocity - 1.0*maxv)/maxv, 1.0)
        else:
            ks = pygame.key.get_pressed()
            camerax = 0
            cameray = 0
            if ks[K_a]:
                camerax -= 1
            if ks[K_d]:
                camerax += 1
            if ks[K_s]:
                cameray -= 1
            if ks[K_w]:
                cameray += 1
            SCALESPEED = SCALESPEED/1.2
            SCALE *= SCALESPEED+1.0
            PX += camerax* 10/SCALE
            PY += cameray*10/SCALE
        
            
        ### Draw stuff
        screen.fill((220,220,240))
        
        for ball in balls:           
            r = ball.radius * SCALE
            v = ball.body.position
            rot = ball.body.rotation_vector
            p = world2screen(v)
            p2 = Vec2d(rot.x, -rot.y) * r * 0.9
            pygame.draw.circle(screen, THECOLORS["blue"], p, max(int(r),1), 1)
            pygame.draw.line(screen, THECOLORS["red"], p, p+p2)
        
        #draw the player
        r = SCALE*pshape.radius
        v = pbody.position
        rot = pbody.rotation_vector
        p = world2screen(v)
        p2 = Vec2d(rot.x, -rot.y) * r * 0.9
        p3 = p + p2
        
        pygame.draw.circle(screen, THECOLORS["lightblue"], (int(p[0]), int(p[1])), max(int(r),1))
        pygame.draw.circle(screen, THECOLORS["blue"], (int(p[0]), int(p[1])), max(int(r),1), 1)
        pygame.draw.line(screen, THECOLORS["red"], (int(p[0]), int(p[1])), (int(p3[0]), int(p3[1])))
            
        if line_point1 is not None:
            #p1 = world2screen(line_point1)
            #p2 = world2screen(mouse_pos)
            #pygame.draw.lines(screen, THECOLORS["black"], False, [p1,p2])
            
            p1 = Vec2d(*world2screen(line_point1))
            p2 = Vec2d(*world2screen(Vec2d(*mouse_pos)))
            if p1.get_distance(p2) > 5:
                v = (p2-p1).perpendicular()
                v = v.scale_to_length(RECT_DEFAULT_HEIGHT)
                p3 = p1+v
                p4 = p2+v
                pts = [p1,p2,p4,p3,p1]
                pygame.draw.lines(screen, THECOLORS["black"], False, pts)
                
        for line in static_lines:
            body = line.body
            
            pv1 = body.position + line.a.rotated(math.degrees(body.angle))
            pv2 = body.position + line.b.rotated(math.degrees(body.angle))
            p1 = world2screen(pv1)
            p2 = world2screen(pv2)
            pygame.draw.lines(screen, THECOLORS["black"], False, [p1,p2])

        screen_top_left = screen2world((0,0))
        screen_bottom_right = screen2world((WIDTH, HEIGHT))
        screen_bb = pm.BB(left=screen_top_left.x, bottom=screen_bottom_right.y, right=screen_bottom_right.x, top=screen_top_left.y)
        for shape in space.bb_query(screen_bb, pm.ShapeFilter()):
            if isinstance(shape, pm.Poly):
                body = shape.body
                ps = shape.get_vertices()
                ps.append(ps[0])
                ps = list(map(world2screen, ps))
                col = THECOLORS["black"]
                if erase == shape and not run_physics:
                    col = THECOLORS["red"]
                pygame.draw.polygon(screen, (180,180,180), ps)
                pygame.draw.lines(screen, col, False, ps)
        
        #pygame.draw.circle(screen, (0,0,0), pygame.mouse.get_pos(),mouse_shape.radius*SCALE,1)
        ### Flip screen
        pygame.display.flip()
        clock.tick(60)
        pygame.display.set_caption("fps: %10s\tScale: %10s"%(str(clock.get_fps()),SCALE))

        

import pygame
import math
from random import randint, uniform, choice, randrange

vector = pygame.math.Vector2
gravity = vector(0, 0.3)
WIDTH, HEIGHT = 1000, 1000

trail_colours = [(249, 199, 79), (249, 132, 74), (248, 150, 30), (243, 114, 44), (249, 65, 68)]
white = (0, 0, 0)
dynamic_offset = 1
static_offset = 5

pygame.init()


class Firework:

    def __init__(self):
        self.colour = (255, 255, 255)
        self.colours = (choice(((255, 21, 22), (253, 148, 21), (254, 246, 23), (249, 132, 74), (62, 232, 21),
                                (22, 160, 232), (150, 20, 230), (142, 134, 147), (255, 255, 255))), white, white)
        self.firework = Particle(randrange(100, WIDTH - 100, 100), HEIGHT, True, self.colour)
        self.exploded = False
        self.particles = []
        self.min_max_particles = vector(100, 200)

    def update(self, win):
        if not self.exploded:
            self.firework.apply_force(gravity)
            self.firework.move()
            for tf in self.firework.trails:
                tf.show(win)

            self.show(win)

            if self.firework.vel.y >= -2:
                self.exploded = True
                self.explode()
        else:
            for particle in self.particles:
                particle.apply_force(vector(gravity.x + uniform(-1, 1) / 20, gravity.y / 2 + (randint(1, 8) / 100)))
                particle.move()
                for t in particle.trails:
                    t.show(win)
                particle.show(win)

    def explode(self):
        amount = randint(int(self.min_max_particles.x), int(self.min_max_particles.y))
        for i in range(amount):
            self.particles.append(Particle(self.firework.pos.x, self.firework.pos.y, False, self.colours))
            pygame.mixer.Channel(0).play(pygame.mixer.Sound('firework.wav'))

    def show(self, win):
        pygame.draw.circle(win, self.colour, (int(self.firework.pos.x), int(self.firework.pos.y)), self.firework.size)

    def remove(self):
        if self.exploded:
            for p in self.particles:
                if p.remove is True:
                    self.particles.remove(p)

            if len(self.particles) == 0:
                return True
            else:
                return False


class Particle:

    def __init__(self, x, y, firework, colour):
        self.firework = firework
        self.pos = vector(x, y)
        self.origin = vector(x, y)
        self.radius = 20
        self.remove = False
        self.explosion_radius = randrange(15, 30, 5)
        self.life = 0
        self.acc = vector(0, 0)
        self.trails = []
        self.prev_posx = [-10] * 10
        self.prev_posy = [-10] * 10

        if self.firework:
            self.vel = vector(0, -randint(18, 23))
            self.size = 4
            self.colour = colour
            for i in range(5):
                self.trails.append(Trail(i, self.size, True))
                pygame.mixer.Channel(1).play(pygame.mixer.Sound('liftoff.wav'))
        else:
            self.vel = vector(uniform(-1, 1), uniform(-1, 1))
            self.vel.x *= 30
            self.vel.y *= 30
            self.size = randint(1, 3)
            self.colour = choice(colour)
            for i in range(5):
                self.trails.append(Trail(i, self.size, False))

    def apply_force(self, force):
        self.acc += force

    def move(self):
        if not self.firework:
            self.vel.x *= 0.8
            self.vel.y *= 0.8

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        if self.life == 0 and not self.firework:
            distance = math.sqrt((self.pos.x - self.origin.x) ** 2 + (self.pos.y - self.origin.y) ** 2)
            if distance > self.explosion_radius:
                self.remove = True

        self.decay()

        self.trail_update()

        self.life += 1

    def show(self, win):
        pygame.draw.circle(win, (self.colour[0], self.colour[1], self.colour[2], 0), (int(self.pos.x), int(self.pos.y)),
                           self.size)

    def decay(self):
        if 50 > self.life > 10:
            ran = randint(0, 30)
            if ran == 0:
                self.remove = True
        elif self.life > 50:
            ran = randint(0, 5)
            if ran == 0:
                self.remove = True

    def trail_update(self):
        self.prev_posx.pop()
        self.prev_posx.insert(0, int(self.pos.x))
        self.prev_posy.pop()
        self.prev_posy.insert(0, int(self.pos.y))

        for n, t in enumerate(self.trails):
            if t.dynamic:
                t.get_pos(self.prev_posx[n + dynamic_offset], self.prev_posy[n + dynamic_offset])
            else:
                t.get_pos(self.prev_posx[n + static_offset], self.prev_posy[n + static_offset])


class Trail:

    def __init__(self, n, size, dynamic):
        self.pos_in_line = n
        self.pos = vector(-10, -10)
        self.dynamic = dynamic

        if self.dynamic:
            self.colour = trail_colours[n]
            self.size = int(size - n / 2)
        else:
            self.colour = (255, 255, 255)
            self.size = size - 2
            if self.size < 0:
                self.size = 0

    def get_pos(self, x, y):
        self.pos = vector(x, y)

    def show(self, win):
        pygame.draw.circle(win, self.colour, (int(self.pos.x), int(self.pos.y)), self.size)


def update(win, fireworks):
    for fw in fireworks:
        fw.update(win)
        if fw.remove():
            fireworks.remove(fw)

    pygame.display.update()


screen = pygame.display.set_mode((WIDTH, HEIGHT))

display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
# display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

clock = pygame.time.Clock()

fireworks = [Firework() for i in range(2)]
running = True

run = True
while run:

    clock.tick(60)

    screen.fill((0, 0, 0))

    if randint(0, 80) == 20:
        fireworks.append(Firework())

    update(screen, fireworks)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

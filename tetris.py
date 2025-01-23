import pygame
import random
WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
score = 0
COLORS = [
    (255, 0, 0),  # Красный
    (0, 255, 0),  # Зеленый
    (0, 0, 255),  # Синий
    (255, 255, 0),  # Желтый
    (255, 165, 0),  # Оранжевый
    (153, 50, 204)  # Лавандовый
]
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 0, 0], [1, 1, 1]]  # L
]
class Particle:
    def __init__(self, x, y, vx, vy, lifetime, size=10):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.lifetime = lifetime
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
    def is_alive(self):
        return self.lifetime > 0
class ParticleSystem:
    def __init__(self):
        self.particles = []
    def add_particle(self, x, y):
        size = 3
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 1)
        lifetime = random.randint(30, 60)
        self.particles.append(Particle(x, y, vx, vy, lifetime, size))
    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(screen, (255, 255, 255), (int(particle.x), int(particle.y)), particle.size)
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
class Tetris:
    def __init__(self, particle_system, hit_sound):
        self.grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_shape = self.new_shape()
        self.current_color = self.new_color()
        self.current_x = GRID_WIDTH // 2 - 1
        self.current_y = 0
        self.particle_system = particle_system
        self.hit_sound = hit_sound
    def new_shape(self):
        return random.choice(SHAPES)
    def new_color(self):
        return random.choice(COLORS)
    def rotate_shape(self):
        self.current_shape = [list(row) for row in zip(*self.current_shape[::-1])]
    def valid_position(self, dx=0, dy=0):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_x + x + dx
                    new_y = self.current_y + y + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or
                            (new_y >= 0 and self.grid[new_y][new_x] is not None)):
                        return False
        return True
    def merge_shape(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_y + y][self.current_x + x] = self.current_color
                    self.hit_sound.play()
                    particle_x = (self.current_x + x) * GRID_SIZE + GRID_SIZE // 2
                    particle_y = (self.current_y + y + 1) * GRID_SIZE
                    self.particle_system.add_particle(particle_x, particle_y)
    def clear_lines(self):
        global score
        lines_cleared = 0
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell is not None for cell in row)]
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [None] * GRID_WIDTH)
            lines_cleared += 1
        score += lines_cleared * 100
    def drop(self):
        if self.valid_position(dy=1):
            self.current_y += 1
        else:
            #self.merge_shape()
            #hit_sound.play()
            self.clear_lines()
            self.current_shape = self.new_shape()
            self.current_color = self.new_color()
            self.current_x = GRID_WIDTH // 2 - 1
            self.current_y = 0
            if not self.valid_position():
                print("Game Over!")
                pygame.quit()
    def drop_immediately(self):
        while self.valid_position(dy=1):
            self.current_y += 1
        self.merge_shape()
        self.clear_lines()
def draw_grid(screen, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color is not None:
                pygame.draw.rect(screen, color,
                                 (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
def draw_shape(screen, shape, x, y, color):
    for y_offset, row in enumerate(shape):
        for x_offset, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color,
                                 ((x + x_offset) * GRID_SIZE,
                                  (y + y_offset) * GRID_SIZE,
                                  GRID_SIZE, GRID_SIZE))
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    particle_system = ParticleSystem()
    hit_sound = pygame.mixer.Sound("nintendostacksound.wav")
    tetris = Tetris(particle_system, hit_sound)
    pygame.mixer.music.load("Hiiragi Magnetite テトリス - Tetoris.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5 )
    font = pygame.font.Font(None, 36)
    drop_time = 0
    drop_interval = 1000
    level = 1
    global score
    score = 0
    last_time = pygame.time.get_ticks()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and tetris.valid_position(dx=-1):
                    tetris.current_x -= 1
                if event.key == pygame.K_RIGHT and tetris.valid_position(dx=1):
                    tetris.current_x += 1
                if event.key == pygame.K_DOWN:
                    tetris.drop()
                if event.key == pygame.K_UP:
                    tetris.rotate_shape()
                if event.key == pygame.K_SPACE:
                    tetris.drop_immediately()
        screen.fill(BLACK)
        particle_system.update()
        draw_grid(screen, tetris.grid)
        draw_shape(screen, tetris.current_shape, tetris.current_x, tetris.current_y, tetris.current_color)
        particle_system.draw(screen)
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()
        current_time = pygame.time.get_ticks()
        drop_time += current_time - last_time
        last_time = current_time
        if drop_time >= drop_interval:
            tetris.drop()
            drop_time = 0
            if score >= level * 100:
                level += 1
                drop_interval = max(100, drop_interval - 100)
    pygame.quit()
if __name__ == "__main__":
    main()

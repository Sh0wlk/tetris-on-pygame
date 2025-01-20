import pygame
import random

WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
BLACK = (0, 0, 0)
score = 0

COLORS = [
    (255, 0, 0),  # Красный
    (0, 255, 0),  # Зеленый
    (0, 0, 255),  # Синий
    (255, 255, 0),  # Желтый
    (255, 165, 0),  # Оранжевый
    (153, 50, 204) # Лавандовый
]

# Фигуры
SHAPES = [
    [[1, 1, 1, 1]],  # l
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # Т
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 0, 0, 0], [1, 1, 1]] # Г
]


class Tetris:
    def __init__(self):
        self.grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_shape = self.new_shape()
        self.current_color = self.new_color()
        self.current_x = GRID_WIDTH // 2 - 1
        self.current_y = 0

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
            self.merge_shape()
            self.clear_lines()
            self.current_shape = self.new_shape()
            self.current_color = self.new_color()
            self.current_x = GRID_WIDTH // 2 - 1
            self.current_y = 0
            if not self.valid_position():
                pygame.quit()

    def drop_immediately(self):
        while self.valid_position(dy=1):
            self.current_y += 1
        self.merge_shape()
        self.clear_lines()


def draw_grid(screen, grid):
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

    background = pygame.image.load("funnybocchi.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    tetris = Tetris()

    pygame.mixer.music.load("Hiiragi Magnetite テトリス - Tetoris.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)

    font = pygame.font.Font(None, 36)

    while True:
        screen.blit(background, (0, 0))
        draw_grid(screen, tetris.grid)
        draw_shape(screen, tetris.current_shape, tetris.current_x, tetris.current_y,
                   tetris.current_color)

        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        tetris.drop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and tetris.valid_position(dx=-1):
                    tetris.current_x -= 1
                if event.key == pygame.K_RIGHT and tetris.valid_position(dx=1):
                    tetris.current_x += 1
                if event.key == pygame.K_DOWN:
                    tetris.drop()  # Ускоренное падение
                if event.key == pygame.K_UP:
                    tetris.rotate_shape()
                if event.key == pygame.K_SPACE:  # Обработчик нажатия пробела
                    tetris.drop_immediately()

        clock.tick(10)  # Ограничение кадров в секунду


if __name__ == "__main__":
    main()
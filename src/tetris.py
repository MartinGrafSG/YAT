import pygame
import random
from Shapes import *
 
pygame.font.init()
 
block_size = 40
play_width = 10 * block_size
play_height = 20 * block_size

s_width = 1000
s_height = 1000
 
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height
 
class Piece(object):
    rows = 20  # y
    columns = 10  # x
 
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3
 
def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]
 
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid
 
def convert_shape_format(shape) -> None:
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
 
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
 
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
 
    return positions
 
def valid_space(shape, grid) -> bool:
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)
 
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
 
    return True
 
def check_lost(positions) -> bool:
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False
 
def get_shape() -> Piece:
    global shapes, shape_colors
 
    return Piece(5, 0, random.choice(shapes))
 
def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
 
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))
 
def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*block_size), (sx + play_width, sy + i * block_size))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))  # vertical lines
 
def clear_rows(grid, locked) -> int:
    # need to see if row is clear then shift every other row above down one
    filledRowsCount = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            filledRowsCount += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if filledRowsCount > 0:
        print("inc = ", str(filledRowsCount), "\n")
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + filledRowsCount)
                locked[newKey] = locked.pop(key)
    return filledRowsCount
 
def drawSideInfo(shape, surface, score, level):
    font = pygame.font.SysFont('comicsans', 30)
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2
    
    label = font.render('Next Shape', 1, (255,255,255))
    surface.blit(label, (sx + 10, sy- block_size))

    label = font.render('Level: ' + str(level), 1, (255,255,255))
    surface.blit(label, (sx + 10, sy- block_size - 300))

    label = font.render('Score: ' + str(score), 1, (255,255,255))
    surface.blit(label, (sx + 10, sy - block_size - 200))
 
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)
 
    
 
def draw_window(surface):
    surface.fill((0,0,0))

    # Tetris Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255,255,255))
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), block_size))

    # draw grid and border
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* block_size, top_left_y + i * block_size, block_size, block_size), 0)
 
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

def handle_events(piece: Piece):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.display.quit()
            pygame.mixer.music.pause()
            quit()

        if event.type == pygame.KEYDOWN:
            handle_keyDown(event, piece)

def handle_keyDown(event, piece : Piece):
    if event.key == pygame.K_LEFT:
        piece.x -= 1
        if not valid_space(piece, grid):
            piece.x += 1

    elif event.key == pygame.K_RIGHT:
        piece.x += 1
        if not valid_space(piece, grid):
            piece.x -= 1

    elif event.key == pygame.K_DOWN:
        # move shape down
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1

    elif event.key == pygame.K_SPACE:
        while valid_space(piece, grid):
            piece.y += 1
        piece.y -= 1
        print(convert_shape_format(piece))
    
    else:
        # rotate shape
        piece.rotation = piece.rotation + 1 % len(piece.shape)
        if not valid_space(piece, grid):
            piece.rotation = piece.rotation - 1 % len(piece.shape)
    return
 
def main():
    global grid
 
    locked_positions = {}  # (x,y):(255,0,0)
    grid = create_grid(locked_positions)
 
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    startTick = pygame.time.get_ticks()
    fall_time = 0 
    pygame.mixer.init(44100, -16, 2, 2048)
    pygame.mixer.music.load("src\Tetris.mp3")
    pygame.mixer.music.play(-1)
    score = 0
    level = 0
    fall_speed = 0.6
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
 
        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
 
        handle_events(current_piece)
 
        shape_pos = convert_shape_format(current_piece)
 
        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
 
        # IF PIECE HIT GROUND
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
 
            filledRowsCount = clear_rows(grid, locked_positions)
            score += filledRowsCount * 25
 
        currentTick = pygame.time.get_ticks()
        gameDurationInSecs = (currentTick - startTick)/1000
        if gameDurationInSecs >= 60:
            level += 1
            fall_speed = fall_speed * 0.9
            startTick = currentTick
        draw_window(window)
        drawSideInfo(next_piece, window, score, level)
        pygame.display.update()
        
        # Check if user lost
        if check_lost(locked_positions):
            run = False
 
    draw_text_middle("You Lost", 40, (255,255,255), window)
    pygame.display.update()
    pygame.time.delay(2000)
 
 
def main_menu():
    run = True
    while run:
        window.fill((0,0,0))
        draw_text_middle('Irgendeine Taste drücken ;-)', 60, (255, 255, 255), window)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
 
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()
 
 
window = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
 
main_menu()  # start game
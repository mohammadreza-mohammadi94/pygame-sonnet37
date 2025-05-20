import pygame
import random
import time
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 30
GRID_WIDTH = 10  # Standard Tetris grid width
GRID_HEIGHT = 20  # Standard Tetris grid height
PLAY_WIDTH = GRID_WIDTH * GRID_SIZE
PLAY_HEIGHT = GRID_HEIGHT * GRID_SIZE
PLAY_X = (WIDTH - PLAY_WIDTH) // 2
PLAY_Y = HEIGHT - PLAY_HEIGHT - 20
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino shapes and colors
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

SHAPE_COLORS = [
    CYAN,    # I
    YELLOW,  # O
    MAGENTA, # T
    GREEN,   # S
    RED,     # Z
    BLUE,    # J
    ORANGE   # L
]

class Tetromino:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.shape = SHAPES[shape_idx]
        self.color = SHAPE_COLORS[shape_idx]
        self.rotation = 0

    def rotate(self):
        # Create a new rotated shape
        rows = len(self.shape)
        cols = len(self.shape[0])
        
        # For 'O' piece, rotation does nothing
        if self.shape_idx == 1:
            return
        
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
                
        # Check if rotation is valid before applying
        old_shape = self.shape
        self.shape = rotated
        
        if not self.is_valid_position(self.x, self.y, self.shape):
            self.shape = old_shape

    def is_valid_position(self, x, y, shape):
        # Check if the tetromino is in a valid position
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j] == 0:
                    continue
                
                pos_x = x + j
                pos_y = y + i
                
                # Check boundaries
                if pos_x < 0 or pos_x >= GRID_WIDTH or pos_y >= GRID_HEIGHT:
                    return False
                
                # Check if position is already filled in the grid
                if pos_y >= 0 and grid[pos_y][pos_x] != BLACK:
                    return False
        
        return True

    def move(self, dx, dy, grid):
        # Try to move the tetromino
        if self.is_valid_position(self.x + dx, self.y + dy, self.shape):
            self.x += dx
            self.y += dy
            return True
        return False
    
    def get_positions(self):
        positions = []
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j] == 1:
                    positions.append((self.y + i, self.x + j))
        return positions

def create_grid():
    # Create an empty grid
    return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def merge_tetromino(grid, tetromino):
    # Add the tetromino to the grid
    for i in range(len(tetromino.shape)):
        for j in range(len(tetromino.shape[i])):
            if tetromino.shape[i][j] == 1:
                grid[tetromino.y + i][tetromino.x + j] = tetromino.color
    return grid

def clear_rows(grid):
    # Check for filled rows and clear them
    rows_cleared = 0
    for i in range(GRID_HEIGHT):
        if BLACK not in grid[i]:
            # Row is filled
            rows_cleared += 1
            # Move all rows above down
            for j in range(i, 0, -1):
                grid[j] = grid[j-1].copy()
            # Add new empty row at the top
            grid[0] = [BLACK for _ in range(GRID_WIDTH)]
    
    return rows_cleared, grid

def is_game_over(grid):
    # Check if any piece in the top row is filled
    return any(grid[0][i] != BLACK for i in range(GRID_WIDTH))

def draw_grid(surface, grid):
    # Draw the grid
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            pygame.draw.rect(
                surface, 
                grid[i][j], 
                pygame.Rect(
                    PLAY_X + j * GRID_SIZE, 
                    PLAY_Y + i * GRID_SIZE, 
                    GRID_SIZE, 
                    GRID_SIZE
                )
            )
            # Draw grid lines
            pygame.draw.rect(
                surface, 
                GRAY, 
                pygame.Rect(
                    PLAY_X + j * GRID_SIZE, 
                    PLAY_Y + i * GRID_SIZE, 
                    GRID_SIZE, 
                    GRID_SIZE
                ), 
                1
            )

def draw_tetromino(surface, tetromino):
    # Draw the current tetromino
    for i in range(len(tetromino.shape)):
        for j in range(len(tetromino.shape[i])):
            if tetromino.shape[i][j] == 1:
                pygame.draw.rect(
                    surface, 
                    tetromino.color,
                    pygame.Rect(
                        PLAY_X + (tetromino.x + j) * GRID_SIZE, 
                        PLAY_Y + (tetromino.y + i) * GRID_SIZE, 
                        GRID_SIZE, 
                        GRID_SIZE
                    )
                )
                # Draw outline
                pygame.draw.rect(
                    surface, 
                    BLACK, 
                    pygame.Rect(
                        PLAY_X + (tetromino.x + j) * GRID_SIZE, 
                        PLAY_Y + (tetromino.y + i) * GRID_SIZE, 
                        GRID_SIZE, 
                        GRID_SIZE
                    ), 
                    1
                )

def draw_next_piece(surface, shape_idx):
    # Draw the next piece preview
    font = pygame.font.SysFont('arial', 24)
    label = font.render("Next Piece:", True, WHITE)
    surface.blit(label, (WIDTH - 200, 100))
    
    shape = SHAPES[shape_idx]
    color = SHAPE_COLORS[shape_idx]
    
    # Calculate center position for the preview
    center_x = WIDTH - 150
    center_y = 180
    
    for i in range(len(shape)):
        for j in range(len(shape[i])):
            if shape[i][j] == 1:
                pygame.draw.rect(
                    surface,
                    color,
                    pygame.Rect(
                        center_x + j * GRID_SIZE, 
                        center_y + i * GRID_SIZE, 
                        GRID_SIZE, 
                        GRID_SIZE
                    )
                )
                pygame.draw.rect(
                    surface,
                    BLACK,
                    pygame.Rect(
                        center_x + j * GRID_SIZE, 
                        center_y + i * GRID_SIZE, 
                        GRID_SIZE, 
                        GRID_SIZE
                    ),
                    1
                )

def draw_score(surface, score, level, lines):
    # Draw the score, level and lines cleared
    font = pygame.font.SysFont('arial', 24)
    
    score_label = font.render(f"Score: {score}", True, WHITE)
    level_label = font.render(f"Level: {level}", True, WHITE)
    lines_label = font.render(f"Lines: {lines}", True, WHITE)
    
    surface.blit(score_label, (WIDTH - 200, 250))
    surface.blit(level_label, (WIDTH - 200, 280))
    surface.blit(lines_label, (WIDTH - 200, 310))

def draw_game_area(surface):
    # Draw the game area outline
    pygame.draw.rect(
        surface, 
        WHITE, 
        pygame.Rect(
            PLAY_X - 1, 
            PLAY_Y - 1, 
            PLAY_WIDTH + 2, 
            PLAY_HEIGHT + 2
        ), 
        1
    )

def main():
    # Main game function
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    global grid
    grid = create_grid()
    
    # Game variables
    score = 0
    level = 1
    lines_cleared_total = 0
    fall_speed = 0.5  # Time in seconds between falls
    last_fall_time = time.time()
    
    # Create first tetromino
    current_piece_idx = random.randint(0, len(SHAPES) - 1)
    current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0, current_piece_idx)
    
    # Generate next piece
    next_piece_idx = random.randint(0, len(SHAPES) - 1)
    
    game_over = False
    paused = False
    
    # Game loop
    running = True
    while running:
        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
                        grid = create_grid()
                        score = 0
                        level = 1
                        lines_cleared_total = 0
                        fall_speed = 0.5
                        current_piece_idx = random.randint(0, len(SHAPES) - 1)
                        current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0, current_piece_idx)
                        next_piece_idx = random.randint(0, len(SHAPES) - 1)
                        game_over = False
                    elif event.key == pygame.K_q:
                        running = False
                        pygame.quit()
                        sys.exit()
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.move(-1, 0, grid)
                elif event.key == pygame.K_RIGHT:
                    current_piece.move(1, 0, grid)
                elif event.key == pygame.K_DOWN:
                    current_piece.move(0, 1, grid)
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while current_piece.move(0, 1, grid):
                        pass
                    grid = merge_tetromino(grid, current_piece)
                    lines, grid = clear_rows(grid)
                    
                    # Update score based on lines cleared
                    if lines == 1:
                        score += 100 * level
                    elif lines == 2:
                        score += 300 * level
                    elif lines == 3:
                        score += 500 * level
                    elif lines == 4:
                        score += 800 * level
                    
                    lines_cleared_total += lines
                    level = lines_cleared_total // 10 + 1
                    fall_speed = max(0.1, 0.5 - (level - 1) * 0.05)
                    
                    # Get the next piece
                    current_piece_idx = next_piece_idx
                    current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0, current_piece_idx)
                    next_piece_idx = random.randint(0, len(SHAPES) - 1)
                    
                    # Check for game over
                    if not current_piece.is_valid_position(current_piece.x, current_piece.y, current_piece.shape):
                        game_over = True
                
                elif event.key == pygame.K_p:
                    paused = not paused
        
        if paused or game_over:
            # Draw everything but don't update game state
            screen.fill(BLACK)
            draw_game_area(screen)
            draw_grid(screen, grid)
            draw_score(screen, score, level, lines_cleared_total)
            draw_next_piece(screen, next_piece_idx)
            
            font = pygame.font.SysFont('arial', 40)
            if paused:
                pause_label = font.render("PAUSED", True, WHITE)
                screen.blit(pause_label, (WIDTH // 2 - pause_label.get_width() // 2, HEIGHT // 2))
            elif game_over:
                go_label = font.render("GAME OVER", True, RED)
                restart_label = pygame.font.SysFont('arial', 24).render("Press R to restart or Q to quit", True, WHITE)
                screen.blit(go_label, (WIDTH // 2 - go_label.get_width() // 2, HEIGHT // 2 - 30))
                screen.blit(restart_label, (WIDTH // 2 - restart_label.get_width() // 2, HEIGHT // 2 + 30))
            
            pygame.display.update()
            clock.tick(FPS)
            continue
            
        # Check if it's time for the piece to fall
        if time.time() - last_fall_time > fall_speed:
            if not current_piece.move(0, 1, grid):
                # The piece can't move down anymore
                grid = merge_tetromino(grid, current_piece)
                lines, grid = clear_rows(grid)
                
                # Update score based on lines cleared
                if lines == 1:
                    score += 100 * level
                elif lines == 2:
                    score += 300 * level
                elif lines == 3:
                    score += 500 * level
                elif lines == 4:
                    score += 800 * level
                
                lines_cleared_total += lines
                level = lines_cleared_total // 10 + 1
                fall_speed = max(0.1, 0.5 - (level - 1) * 0.05)
                
                # Get the next piece
                current_piece_idx = next_piece_idx
                current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0, current_piece_idx)
                next_piece_idx = random.randint(0, len(SHAPES) - 1)
                
                # Check for game over
                if not current_piece.is_valid_position(current_piece.x, current_piece.y, current_piece.shape):
                    game_over = True
            
            last_fall_time = time.time()
        
        # Draw everything
        screen.fill(BLACK)
        draw_game_area(screen)
        draw_grid(screen, grid)
        draw_tetromino(screen, current_piece)
        draw_score(screen, score, level, lines_cleared_total)
        draw_next_piece(screen, next_piece_idx)
        
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
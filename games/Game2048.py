import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 500, 600
GRID_SIZE = 4
CELL_SIZE = 100
CELL_PADDING = 10
GRID_WIDTH = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * CELL_PADDING
GRID_HEIGHT = GRID_WIDTH
GRID_X = (WIDTH - GRID_WIDTH) // 2
GRID_Y = 100

# Colors
BACKGROUND = (187, 173, 160)
EMPTY_CELL = (205, 193, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (119, 110, 101)

# Tile colors based on value
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (60, 58, 50),
}

# Text colors
TEXT_COLORS = {
    2: DARK_GRAY, 4: DARK_GRAY,
    8: WHITE, 16: WHITE, 32: WHITE, 64: WHITE,
    128: WHITE, 256: WHITE, 512: WHITE, 1024: WHITE, 2048: WHITE,
    4096: WHITE, 8192: WHITE
}

class Game2048:
    def __init__(self):
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.best_score = 0
        self.game_won = False
        self.game_over = False
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_title = pygame.font.Font(None, 72)
        
        # Add two initial tiles
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        """Add a random tile (2 or 4) to an empty cell"""
        empty_cells = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.board[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def move_left(self):
        """Move and merge tiles to the left"""
        moved = False
        for i in range(GRID_SIZE):
            # Extract non-zero values
            row = [self.board[i][j] for j in range(GRID_SIZE) if self.board[i][j] != 0]
            
            # Merge adjacent equal values
            merged_row = []
            j = 0
            while j < len(row):
                if j < len(row) - 1 and row[j] == row[j + 1]:
                    # Merge tiles
                    merged_value = row[j] * 2
                    merged_row.append(merged_value)
                    self.score += merged_value
                    if merged_value == 2048 and not self.game_won:
                        self.game_won = True
                    j += 2
                else:
                    merged_row.append(row[j])
                    j += 1
            
            # Pad with zeros
            merged_row.extend([0] * (GRID_SIZE - len(merged_row)))
            
            # Check if row changed
            if merged_row != [self.board[i][j] for j in range(GRID_SIZE)]:
                moved = True
            
            # Update board
            for j in range(GRID_SIZE):
                self.board[i][j] = merged_row[j]
        
        return moved

    def move_right(self):
        """Move and merge tiles to the right"""
        # Reverse each row, move left, then reverse again
        for i in range(GRID_SIZE):
            self.board[i].reverse()
        
        moved = self.move_left()
        
        for i in range(GRID_SIZE):
            self.board[i].reverse()
        
        return moved

    def move_up(self):
        """Move and merge tiles up"""
        # Transpose, move left, transpose back
        self.transpose()
        moved = self.move_left()
        self.transpose()
        return moved

    def move_down(self):
        """Move and merge tiles down"""
        # Transpose, move right, transpose back
        self.transpose()
        moved = self.move_right()
        self.transpose()
        return moved

    def transpose(self):
        """Transpose the board matrix"""
        self.board = [[self.board[j][i] for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

    def can_move(self):
        """Check if any move is possible"""
        # Check for empty cells
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.board[i][j] == 0:
                    return True
        
        # Check for possible merges
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                current = self.board[i][j]
                # Check right neighbor
                if j < GRID_SIZE - 1 and self.board[i][j + 1] == current:
                    return True
                # Check bottom neighbor
                if i < GRID_SIZE - 1 and self.board[i + 1][j] == current:
                    return True
        
        return False

    def make_move(self, direction):
        """Make a move in the specified direction"""
        if self.game_over:
            return
        
        moved = False
        if direction == 'left':
            moved = self.move_left()
        elif direction == 'right':
            moved = self.move_right()
        elif direction == 'up':
            moved = self.move_up()
        elif direction == 'down':
            moved = self.move_down()
        
        if moved:
            self.add_random_tile()
            if not self.can_move():
                self.game_over = True
        
        # Update best score
        if self.score > self.best_score:
            self.best_score = self.score

    def reset(self):
        """Reset the game"""
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.game_won = False
        self.game_over = False
        self.add_random_tile()
        self.add_random_tile()

    def draw_cell(self, surface, value, x, y):
        """Draw a single cell"""
        # Get colors
        bg_color = TILE_COLORS.get(value, TILE_COLORS[8192]) if value != 0 else EMPTY_CELL
        text_color = TEXT_COLORS.get(value, WHITE) if value != 0 else DARK_GRAY
        
        # Draw cell background
        cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, bg_color, cell_rect, border_radius=6)
        
        # Draw text if cell has value
        if value != 0:
            # Choose font size based on number of digits
            if value < 100:
                font = self.font_large
            elif value < 1000:
                font = self.font_medium
            else:
                font = self.font_small
            
            text = font.render(str(value), True, text_color)
            text_rect = text.get_rect(center=cell_rect.center)
            surface.blit(text, text_rect)

    def draw(self, surface):
        """Draw the entire game"""
        surface.fill(BACKGROUND)
        
        # Draw title
        title_text = self.font_title.render("2048", True, DARK_GRAY)
        surface.blit(title_text, (50, 20))
        
        # Draw scores
        score_text = self.font_medium.render(f"Score: {self.score}", True, DARK_GRAY)
        best_text = self.font_medium.render(f"Best: {self.best_score}", True, DARK_GRAY)
        surface.blit(score_text, (250, 30))
        surface.blit(best_text, (250, 60))
        
        # Draw grid background
        grid_rect = pygame.Rect(GRID_X, GRID_Y, GRID_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(surface, DARK_GRAY, grid_rect, border_radius=6)
        
        # Draw cells
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = GRID_X + CELL_PADDING + j * (CELL_SIZE + CELL_PADDING)
                y = GRID_Y + CELL_PADDING + i * (CELL_SIZE + CELL_PADDING)
                self.draw_cell(surface, self.board[i][j], x, y)
        
        # Draw game over or win message
        if self.game_over:
            self.draw_overlay(surface, "Game Over!", "Press R to restart")
        elif self.game_won:
            self.draw_overlay(surface, "You Win!", "Press C to continue or R to restart")
        
        # Draw instructions
        instructions = [
            "Use arrow keys to move tiles",
            "When two tiles with the same number touch,",
            "they merge into one!",
            "Press R to restart at any time"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, DARK_GRAY)
            surface.blit(text, (20, HEIGHT - 80 + i * 20))

    def draw_overlay(self, surface, title, subtitle):
        """Draw game over or win overlay"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        title_text = self.font_title.render(title, True, WHITE)
        subtitle_text = self.font_medium.render(subtitle, True, WHITE)
        
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        
        surface.blit(title_text, title_rect)
        surface.blit(subtitle_text, subtitle_rect)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    
    game = Game2048()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_c and game.game_won:
                    game.game_won = False  # Continue playing after winning
                elif not game.game_over and not game.game_won:
                    if event.key == pygame.K_LEFT:
                        game.make_move('left')
                    elif event.key == pygame.K_RIGHT:
                        game.make_move('right')
                    elif event.key == pygame.K_UP:
                        game.make_move('up')
                    elif event.key == pygame.K_DOWN:
                        game.make_move('down')
        
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
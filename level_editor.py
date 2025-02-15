import pygame
import csv
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 25

# Colors
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (200, 25, 25)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
# ...existing code...
ORANGE = (255, 165, 0)
SQUARE = (0, 255, 0)  # Color for the square

# Game variables
ROWS = HEIGHT // TILE_SIZE
COLS = WIDTH // TILE_SIZE
current_tile = 1  # Default tile to draw is an obstacle
level = 1

# Create an empty level grid
world_data = [[-1 for _ in range(COLS)] for _ in range(ROWS)]

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Level Editor")

# Clock for frame rate
clock = pygame.time.Clock()

# Function to draw the grid
def draw_grid():
    for x in range(0, WIDTH, TILE_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

# Function to draw the world
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile == 1:  # Obstacle tile
                pygame.draw.rect(screen, BLUE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 2:  # Kill power-up
                pygame.draw.rect(screen, RED, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 3 or tile == 4:  # Teleporter
                pygame.draw.rect(screen, YELLOW, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 5:  # Finish area
                pygame.draw.rect(screen, PURPLE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 6:  # Square
                pygame.draw.rect(screen, SQUARE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Main loop
running = True
while running:
    screen.fill(GREEN)

    # Draw grid and world
    draw_grid()
    draw_world()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Place/remove tiles
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // TILE_SIZE
            grid_y = mouse_y // TILE_SIZE
            if grid_x < COLS and grid_y < ROWS:
                world_data[grid_y][grid_x] = current_tile  # Place current tile

        if pygame.mouse.get_pressed()[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // TILE_SIZE
            grid_y = mouse_y // TILE_SIZE
            if grid_x < COLS and grid_y < ROWS:
                world_data[grid_y][grid_x] = -1  # Remove tile

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_tile = 1  # Obstacle
            elif event.key == pygame.K_2:
                current_tile = 2  # Kill power-up
            elif event.key == pygame.K_3:
                current_tile = 3  # Teleporter entry
            elif event.key == pygame.K_4:
                current_tile = 4  # Teleporter exit
            elif event.key == pygame.K_5:
                current_tile = 5  # Finish area
            elif event.key == pygame.K_6:
                current_tile = 6  # Square
            elif event.key == pygame.K_s:  # Save level
                with open(f"level{level}.csv", "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(world_data)
                print(f"Level {level} saved!")

            elif event.key == pygame.K_l:  # Load level
                try:
                    with open(f"level{level}.csv", "r") as file:
                        reader = csv.reader(file)
                        world_data = [[int(tile) for tile in row] for row in reader]
                    print(f"Level {level} loaded!")
                except FileNotFoundError:
                    print(f"Level {level}.csv not found.")

    # Display instructions
    font = pygame.font.SysFont("Futura", 24)
    save_text = font.render("1: Obstacle, 2: Kill Power-Up, 3: Teleporter Entry, 4: Teleporter Exit, 5: Finish Area, 6: Square", True, ORANGE)
    screen.blit(save_text, (10, HEIGHT - 60))
    save_text2 = font.render("S: Save, L: Load, Right-click: Erase", True, ORANGE)
    screen.blit(save_text2, (10, HEIGHT - 30))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
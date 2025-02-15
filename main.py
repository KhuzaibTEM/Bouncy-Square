import pygame
import csv
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 25

# Colors
GREEN = (144, 201, 120)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)

# List of colors for squares
SQUARE_COLORS = [RED, BLUE, YELLOW, PURPLE, ORANGE]

# Load level from CSV file
def load_level(level):
    try:
        with open(f"level{level}.csv", "r") as file:
            reader = csv.reader(file)
            return [[int(tile) for tile in row] for row in reader]
    except FileNotFoundError:
        print(f"Level {level}.csv not found! Exiting.")
        sys.exit()

# Game variables
level = 1
world_data = load_level(level)

# Square properties
SQUARE_SIZE = 25
squares = []

# Initialize squares based on level data
color_index = 0
for y, row in enumerate(world_data):
    for x, tile in enumerate(row):
        if tile == 6:  # Square tile
            squares.append({
                "x": x * TILE_SIZE,
                "y": y * TILE_SIZE,
                "dx": 5,
                "dy": 5,
                "color": SQUARE_COLORS[color_index],  # Assign color in pattern
                "trail": [],
                "dead": False,
                "overlay": None
            })
            color_index = (color_index + 1) % len(SQUARE_COLORS)  # Cycle through colors
            world_data[y][x] = -1  # Remove the square tile from the world data

# Power-up images
kill_powerup_img = pygame.image.load("feature_imgs/knife.png")
teleporter_img = pygame.image.load("feature_imgs/teleporter.png")
finish_img = pygame.image.load("finish_line/finish.png")

# Load skull image with transparency support
skull_img = pygame.image.load("feature_imgs/skull.png")

# Load overlay images for each square
overlay_images = {
    RED: pygame.image.load("square_knife/red_knife.png"),
    BLUE: pygame.image.load("square_knife/blue_knife.png"),
    YELLOW: pygame.image.load("square_knife/yellow_knife.png"),
    PURPLE: pygame.image.load("square_knife/purple_knife.png"),
    ORANGE: pygame.image.load("square_knife/orange_knife.png"),
}

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Squares Game")

# Clock for frame rate
clock = pygame.time.Clock()

# Load sound
pygame.mixer.music.load("audio/instrumental_song.mp3")
pygame.mixer.music.play()
pygame.mixer.music.pause()
playback_position = 0

kill_sound = pygame.mixer.Sound("audio/kill_sound.mp3")

# Game state variables
is_colliding = False
collision_timer = 0
kill_powerup_active = [False] * len(squares)
win_timer = None
winning_square = None
dead_squares = []  # List to keep track of dead squares

# Function to draw the world (including power-ups)
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile == 1:  # Obstacle
                pygame.draw.rect(screen, BLUE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 2:  # Kill power-up
                screen.blit(kill_powerup_img, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == 3 or tile == 4:  # Teleporter
                screen.blit(teleporter_img, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == 5:  # Finish block
                screen.blit(finish_img, (x * TILE_SIZE, y * TILE_SIZE))

# Function to draw the contrail
def draw_contrail(square):
    trail = square["trail"]
    for i, (x, y) in enumerate(trail):
        # Calculate alpha (transparency) based on the position in the trail
        alpha = int(255 * (1 - i / len(trail)))
        lighter_color = (
            min(square["color"][0] + 40, 255),  # Increase red
            min(square["color"][1] + 40, 255),  # Increase green
            min(square["color"][2] + 40, 255),  # Increase blue
            alpha  # Transparency
        )
        # Calculate the size of the contrail square
        # Oldest squares (beginning of the trail) should be smaller
        size = SQUARE_SIZE * (1 - (len(trail) - i) / len(trail))
        # Create a surface with transparency
        trail_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(trail_surface, lighter_color, (0, 0, size, size))
        # Center the contrail square around the original position
        screen.blit(trail_surface, (x + (SQUARE_SIZE - size) / 2, y + (SQUARE_SIZE - size) / 2))

# Main game loop
running = True
while running:
    screen.fill(GREEN)

    # Draw the world
    draw_world()

    # Process each square
    for i, square in enumerate(squares):
        if win_timer:  # Stop movement after a win
            break

        # Skip processing if the square is dead
        if square["dead"]:
            continue

        # Update square position
        square["x"] += square["dx"]
        square["y"] += square["dy"]

        # Add current position to the trail
        square["trail"].append((square["x"], square["y"]))
        if len(square["trail"]) > 10:  # Limit trail length to 10
            square["trail"].pop(0)

        # Create a rectangle for the square
        square_rect = pygame.Rect(square["x"], square["y"], SQUARE_SIZE, SQUARE_SIZE)

        # Handle collisions with the borders
        if square["x"] <= 0 or square["x"] + SQUARE_SIZE >= WIDTH:
            square["dx"] = -square["dx"]
            pygame.mixer.music.unpause()

        if square["y"] <= 0 or square["y"] + SQUARE_SIZE >= HEIGHT:
            square["dy"] = -square["dy"]
            pygame.mixer.music.unpause()

        # Handle collisions with world objects
        for y, row in enumerate(world_data):
            for x, tile in enumerate(row):
                obj_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if square_rect.colliderect(obj_rect):
                    if tile == 1:  # Obstacle
                        overlap_x = min(square_rect.right - obj_rect.left, obj_rect.right - square_rect.left)
                        overlap_y = min(square_rect.bottom - obj_rect.top, obj_rect.bottom - square_rect.top)
                        if overlap_x < overlap_y:
                            square["dx"] = -square["dx"]
                            if square["dx"] > 0:
                                square["x"] += overlap_x
                            else:
                                square["x"] -= overlap_x
                        else:
                            square["dy"] = -square["dy"]
                            if square["dy"] > 0:
                                square["y"] += overlap_y
                            else:
                                square["y"] -= overlap_y

                        if not is_colliding:
                            pygame.mixer.music.unpause()
                            pygame.mixer.music.play(start=playback_position)
                            is_colliding = True
                            collision_timer = time.time()

                    elif tile == 2:  # Kill power-up
                        kill_powerup_active[i] = True
                        square["overlay"] = overlay_images[square["color"]]  # Set the overlay image
                        world_data[y][x] = -1
                    elif tile == 3:  # Teleporter entry
                        exit_tiles = [(r, c) for r, row in enumerate(world_data) for c, t in enumerate(row) if t == 4]
                        if exit_tiles:
                            exit_y, exit_x = exit_tiles[0]
                            square["x"] = exit_x * TILE_SIZE
                            square["y"] = exit_y * TILE_SIZE
                    elif tile == 5:  # Finish block
                        win_timer = time.time()
                        winning_square = i

        # Handle "kill" power-up collisions
        if kill_powerup_active[i]:
            for j, other_square in enumerate(squares):
                if i != j and not other_square["dead"]:  # Only kill alive squares
                    other_square_rect = pygame.Rect(other_square["x"], other_square["y"], SQUARE_SIZE, SQUARE_SIZE)
                    if square_rect.colliderect(other_square_rect):
                        if kill_powerup_active[j]:  # Both squares have the "kill" power-up
                            kill_sound.play()
                            other_square["dead"] = True  # Mark the other square as dead
                            square["dead"] = True  # Mark the current square as dead
                            dead_squares.append((other_square["x"], other_square["y"], other_square["color"]))  # Add to dead squares list with color
                            dead_squares.append((square["x"], square["y"], square["color"]))  # Add to dead squares list with color
                            kill_powerup_active[i] = False  # Deactivate the power-up for the current square
                            kill_powerup_active[j] = False  # Deactivate the power-up for the other square
                            square["overlay"] = None  # Remove the overlay image for the current square
                            other_square["overlay"] = None  # Remove the overlay image for the other square
                        else:
                            kill_sound.play()
                            other_square["dead"] = True  # Mark the other square as dead
                            dead_squares.append((other_square["x"], other_square["y"], other_square["color"]))  # Add to dead squares list with color
                            kill_powerup_active[i] = False  # Deactivate the power-up for the current square
                            square["overlay"] = None  # Remove the overlay image for the current square

        # Draw the contrail
        draw_contrail(square)

        # Draw the square if not dead
        if not square["dead"]:
            if square["overlay"]:
                screen.blit(square["overlay"], (square["x"], square["y"]))  # Draw the overlay image
            else:
                pygame.draw.rect(screen, square["color"], square_rect)

    # Draw skulls for dead squares
    for x, y, color in dead_squares:
        pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))  # Draw the square's color
        screen.blit(skull_img, (x, y))  # Draw the skull image on top

    # Stop the sound after 0.5 second if no collision is detected
    if is_colliding and time.time() - collision_timer >= 0.3:
        pygame.mixer.music.pause()
        if playback_position >= 30:  # Restart playback position after 30 seconds (change as needed)
            playback_position = 0
        playback_position += 0.6  # Move to the next 0.5s segment
        is_colliding = False
        collision_timer = 0

    # Handle win logic
    if win_timer:
        font = pygame.font.SysFont("Arial", 36)
        win_text = font.render(f"Square {winning_square + 1} Wins!", True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - 100, HEIGHT // 2))
        if time.time() - win_timer > 5:
            running = False

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
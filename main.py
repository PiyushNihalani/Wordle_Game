import pygame
import sys
import random
from words import *
import json
import os

pygame.init()
pygame.mixer.init()

# Constants

WIDTH, HEIGHT = 635, 780

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
BACKGROUND = pygame.image.load("assets/Starting Tiles.png")
BACKGROUND_RECT = BACKGROUND.get_rect(center=(317, 320))
ICON = pygame.image.load("assets/Icon.png")

pygame.display.set_caption("Wordle!")
pygame.display.set_icon(ICON)

font = pygame.font.SysFont(None, 48)  # Adjust font size as needed
heading_text = font.render('WORDLE', True, (0, 0, 0))  # Black text

# Load button icons
settings_icon = pygame.image.load('assets/settings.png')
stats_icon = pygame.image.load('assets/stats.png')
help_icon = pygame.image.load('assets/help.png')

# Resize icons (if needed)
settings_icon = pygame.transform.scale(settings_icon, (30, 30))
stats_icon = pygame.transform.scale(stats_icon, (30, 30))
help_icon = pygame.transform.scale(help_icon, (30, 30))

# Define button positions (adjust these positions as per your layout)
heading_position = (WIDTH // 2 - heading_text.get_width() // 2, 20)  # Centered heading below top
settings_rect = settings_icon.get_rect(topleft=(550,20))  # Place settings button
stats_rect = stats_icon.get_rect(topleft=(500, 20))        # Place stats button
help_rect = help_icon.get_rect(topleft=(80, 20))

GREEN = "#6aaa64"
YELLOW = "#c9b458"
GREY = "#787c7e"
OUTLINE = "#d3d6da"
FILLED_OUTLINE = "#878a8c"

CORRECT_WORD = random.choice(WORDS)

ALPHABET = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

GUESSED_LETTER_FONT = pygame.font.Font("assets/FreeSansBold.otf", 50)
AVAILABLE_LETTER_FONT = pygame.font.Font("assets/FreeSansBold.otf", 25)

SCREEN.fill("white")
SCREEN.blit(BACKGROUND, BACKGROUND_RECT)
SCREEN.blit(heading_text, heading_position)

    # Blit (draw) the icons on the screen
SCREEN.blit(stats_icon, stats_rect)
SCREEN.blit(help_icon, help_rect)
SCREEN.blit(settings_icon, settings_rect)
pygame.display.update()

LETTER_X_SPACING = 84
LETTER_Y_SPACING = 71#156
LETTER_SIZE = 75

# Global variables

guesses_count = 0

# guesses is a 2D list that will store guesses. A guess will be a list of letters.
# The list will be iterated through and each letter in each guess will be drawn on the screen.
guesses = [[]] * 6

current_guess = []
current_guess_string = ""
current_letter_bg_x = 113

key_press_sound = pygame.mixer.Sound("key_press.wav")  # Short sound effect
win_sound = pygame.mixer.Sound("win_sound.mp3")        # Win sound
lose_sound = pygame.mixer.Sound("lose_sound.mp3")      # Lose sound

# Load background music
pygame.mixer.music.load("bg_music.mp3")  # Your background music file
pygame.mixer.music.set_volume(0.1)        # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)

# Indicators is a list storing all the Indicator object. An indicator is that button thing with all the letters you see.
indicators = []

stats_visible = False

game_result = ""

sound_enabled = True  # Variable to track sound state

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    
    if sound_enabled:
        # Resume background music
        pygame.mixer.music.unpause()
    else:
        # Stop any currently playing sound effects and pause the background music
        pygame.mixer.stop()  # This stops all sound effects
        pygame.mixer.music.pause()


class Letter:
    def __init__(self, text, bg_position):
        # Initializes all the variables, including text, color, position, size, etc.
        self.bg_color = "white"
        self.text_color = "black"
        self.bg_position = bg_position
        self.bg_x= bg_position[0]
        self.bg_y=bg_position[1]
        self.bg_rect = (bg_position[0], self.bg_y,LETTER_SIZE,LETTER_SIZE)
        self.text = text
        self.text_position = (self.bg_x+37 , self.bg_position[1]+35)
        self.text_surface = GUESSED_LETTER_FONT.render(self.text , True , self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.text_position)

    def draw(self):
        # Puts the letter and text on the screen at the desired positions.
        pygame.draw.rect(SCREEN, self.bg_color, self.bg_rect)
        if self.bg_color == "white":
            pygame.draw.rect(SCREEN, FILLED_OUTLINE, self.bg_rect, 3)
        self.text_surface = GUESSED_LETTER_FONT.render(self.text, True , self.text_color)
        SCREEN.blit(self.text_surface,self.text_rect)

    def delete(self):
        # Fills the letter's spot with the default square, emptying it.
        pygame.draw.rect(SCREEN , "white" , self.bg_rect)
        pygame.draw.rect(SCREEN , OUTLINE, self.bg_rect, 3)
        pygame.display.update()

class Indicator:
    def __init__(self, x, y, letter):
        # Initializes variables such as color, size, position, and letter.
        self.x =x
        self.y = y
        self.text = letter
        self.rect =(self.x,self.y,35,50)
        self.bg_color = OUTLINE

    def draw(self):
        # Puts the indicator and its text on the screen at the desired position.
        pygame.draw.rect(SCREEN,self.bg_color,self.rect)
        self.text_surface = AVAILABLE_LETTER_FONT.render(self.text, True, "white")
        self.text_rect = self.text_surface.get_rect(center=(self.x+17, self.y+25))
        SCREEN.blit(self.text_surface, self.text_rect)
        pygame.display.update()

# Drawing the indicators on the screen.

indicator_x,indicator_y = 95,590

for i in range(3):
    for letter in ALPHABET[i]:
        new_indicator = Indicator(indicator_x, indicator_y, letter)
        indicators.append(new_indicator)
        new_indicator.draw()
        indicator_x += 45
    indicator_y += 65
    if i == 0:
        indicator_x = 125
    elif i == 1:
        indicator_x = 180


def check_guess(guess_to_check):
    global current_letter_bg_x, current_guess_string, current_guess, guesses_count, game_result
    correct_letters_count = 0  # Track number of correct letters in correct positions
    game_decided = False

    for i in range(5):
        lowercase_letter = guess_to_check[i].text.lower()
        if lowercase_letter in CORRECT_WORD:
            if lowercase_letter == CORRECT_WORD[i]:
                guess_to_check[i].bg_color = GREEN
                correct_letters_count += 1  # Increment for each correct letter in the correct position
                for indicator in indicators:
                    if indicator.text == lowercase_letter.upper():
                        indicator.bg_color = GREEN
                        indicator.draw()
                guess_to_check[i].text_color = "white"
            else:
                guess_to_check[i].bg_color = YELLOW
                for indicator in indicators:
                    if indicator.text == lowercase_letter.upper():
                        indicator.bg_color = YELLOW
                        indicator.draw()
                guess_to_check[i].text_color = "white"
                game_decided = True
        else:
            guess_to_check[i].bg_color = GREY
            for indicator in indicators:
                if indicator.text == lowercase_letter.upper():
                    indicator.bg_color = GREY
                    indicator.draw()
            guess_to_check[i].text_color = "white"
            game_decided = True
        guess_to_check[i].draw()
        pygame.display.update()

    # Check if all letters are correct
    if correct_letters_count == 5:
        game_result = "W"
        if sound_enabled:
            win_sound.play()
    else:
        game_result = ""

    guesses_count += 1
    current_guess = []
    current_guess_string = ""
    current_letter_bg_x = 110

    if guesses_count == 6 and game_result == "":
        game_result = "L"
        if sound_enabled:
            lose_sound.play()

    # Update stats after each game result
    if game_result == "W":
        update_stats(game_won=True)
    elif game_result == "L":
        update_stats(game_won=False)


def show_stats():
    global stats_visible
    stats_visible = True  # Set the state to indicate stats are visible

    # Load current stats
    stats = load_stats()
    wins = stats["games_won"]
    total_games = stats["total_games"]
    losses = total_games - wins
    best_streak = stats["best_streak"]
    current_streak = stats["current_streak"]

    # Create a new surface for the overlay
    stats_overlay = pygame.Surface((WIDTH, HEIGHT))
    stats_overlay.set_alpha(128)  # Set transparency of the overlay
    stats_overlay.fill((255, 255, 255))  # Fill with white

    # Create font for the stats text
    stats_font = pygame.font.Font("assets/FreeSansBold.otf", 24)

    # Draw stats text on the overlay
    stats_text = stats_font.render(f"Games Played: {total_games}", True, (0, 0, 0))
    stats_overlay.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 - 100))
    stats_text = stats_font.render(f"Wins: {wins}", True, (0, 0, 0))
    stats_overlay.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 - 50))
    stats_text = stats_font.render(f"Losses: {losses}", True, (0, 0, 0))
    stats_overlay.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2))
    stats_text = stats_font.render(f"Best Streak: {best_streak}", True, (0, 0, 0))
    stats_overlay.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 50))
    stats_text = stats_font.render(f"Current Streak: {current_streak}", True, (0, 0, 0))
    stats_overlay.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 100))

    # Display the overlay
    SCREEN.blit(stats_overlay, (0, 0))
    pygame.display.update()

    # Wait for the user to close the stats screen
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                waiting = False

    # After closing, redraw the main screen
    stats_visible = False  # Reset the state
    draw_main_screen()
    pygame.display.update()  # Ensure main screen is updated

    # Process any pending events
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Check for the next click event to allow reopening the stats
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return  # Exit the loop and allow other processing to continue
            # Optionally handle other key events or interactions here
        pygame.time.wait(10)  # Prevent CPU overloading with a small wait


def load_stats():
    try:
        with open('stats.json', 'r') as file:
            stats = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create it with default stats
        stats = {
            "total_games": 0,
            "games_won": 0,
            "games_lost": 0,  # Add games_lost here
            "best_streak": 0,
            "current_streak": 0
        }
        save_stats(stats)
    return stats

# Function to save stats to the JSON file
def save_stats(stats):
    with open('stats.json', 'w') as file:
        json.dump(stats, file)

# Function to update the stats after a game is played
def update_stats(game_won):
    stats = load_stats()
    stats["total_games"] += 1
    if game_won:
        stats["games_won"] += 1
        stats["current_streak"] += 1
        if stats["current_streak"] > stats["best_streak"]:
            stats["best_streak"] = stats["current_streak"]
    else:
        stats["games_lost"] += 1  # Increment games_lost if the player loses
        stats["current_streak"] = 0  # Reset streak if the game is lost
    save_stats(stats)

def reset_stats():
    # Delete the stats.json file if it exists
    if os.path.exists("stats.json"):
        os.remove("stats.json")  # Delete the stats file

def show_instructions():
    # Create a transparent overlay for the instructions
    instructions_overlay = pygame.Surface((WIDTH, HEIGHT))
    instructions_overlay.set_alpha(128)  # Set transparency
    instructions_overlay.fill((0, 0, 0))  # Black overlay

    # Set font for instructions text
    instructions_font = pygame.font.Font("assets/FreeSansBold.otf", 24)

    # Define the instructions text
    instructions_lines = [
        "How to Play Wordle:",
        "1. Guess the WORDLE in 6 tries.",
        "2. Each guess must be a valid 5-letter word.",
        "3. The color of the tiles will change to show",
        "   how close your guess was to the word.",
        "",
        "Green: Letter is in the correct spot.",
        "Yellow: Letter is in the word but in the wrong spot.",
        "Grey: Letter is not in the word.",
        "",
        "Press any key to go back."
    ]

    # Blit each line of the instructions onto the overlay
    y_offset = 150
    for line in instructions_lines:
        text_surface = instructions_font.render(line, True, (255, 255, 255))  # White text for dark background
        instructions_overlay.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
        y_offset += 40  # Adjust the vertical space between lines

    # Display the overlay
    SCREEN.blit(instructions_overlay, (0, 0))
    pygame.display.update()

    # Wait for any key press or mouse click to exit the instructions screen
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Detect any key press
                waiting = False  # Exit the instructions screen
            if event.type == pygame.MOUSEBUTTONDOWN:  # Detect mouse click
                waiting = False  # Exit the instructions screen

    # Clear the instructions screen and return to the main game
    draw_main_screen()  # Clear the screen (or re-render game state)

def show_settings():
    # Create a transparent overlay for the settings
    settings_overlay = pygame.Surface((WIDTH, HEIGHT))
    settings_overlay.set_alpha(128)  # Set transparency
    settings_overlay.fill((0, 0, 0))  # Black overlay

    # Set font for settings text
    settings_font = pygame.font.Font("assets/FreeSansBold.otf", 24)

    # Define the settings options
    settings_options = [
        "Settings Menu",
        "1. Reset Stats",
        "2. Toggle Sound (Current: " + ("Unmuted" if sound_enabled else "Muted") + ")",
        "Press any key to go back."
    ]

    # Blit each line of the settings onto the overlay
    y_offset = 150
    for line in settings_options:
        text_surface = settings_font.render(line, True, (255, 255, 255))  # White text for dark background
        settings_overlay.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
        y_offset += 40  # Adjust the vertical space between lines

    # Display the overlay
    SCREEN.blit(settings_overlay, (0, 0))
    pygame.display.update()

    # Wait for any key press to exit the settings screen
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
                if event.key == pygame.K_1:
                    reset_stats()
                elif event.key == pygame.K_2:
                    toggle_sound()

    # Clear the settings screen and return to the main game
    draw_main_screen()  # Clear the screen (or re-render game state)


def play_again():
    # Puts the play again text on the screen.
    pygame.draw.rect(SCREEN, "white", (10, 580, 1000, 600))
    play_again_font = pygame.font.Font("assets/FreeSansBold.otf", 40)
    play_again_text = play_again_font.render("Press ENTER to Play Again!", True, "black")
    play_again_rect = play_again_text.get_rect(center=(WIDTH/2, 700))
    word = CORRECT_WORD.upper()
    word_was_text = play_again_font.render(f"The word was {word}!", True, "black")
    word_was_rect = word_was_text.get_rect(center=(WIDTH/2, 650))
    SCREEN.blit(word_was_text, word_was_rect)
    SCREEN.blit(play_again_text, play_again_rect)
    pygame.display.update()

def reset():
    # Resets all global variables to their default states.
    global CORRECT_WORD,guesses,guesses_count,game_result,current_guess,current_guess_string
    SCREEN.fill("white")
    SCREEN.blit(BACKGROUND,BACKGROUND_RECT)
    SCREEN.blit(heading_text, heading_position)
    SCREEN.blit(stats_icon, stats_rect)
    SCREEN.blit(help_icon, help_rect)
    SCREEN.blit(settings_icon, settings_rect)
    guesses_count=0
    CORRECT_WORD = random.choice(WORDS)
    guesses = [[]] * 6
    current_guess = []
    current_guess_string = ""
    game_result = ""
    pygame.display.update()
    for indicator in indicators:
        indicator.bg_color = OUTLINE
        indicator.draw()


def create_new_letter():
    # Creates a new letter and adds it to the guess.
    global current_guess_string, current_letter_bg_x
    current_guess_string += key_pressed
    # new_letter = Letter(key_pressed , (current_letter_bg_x , 71.5))
    if guesses_count > 0:
        new_letter = Letter(key_pressed, (current_letter_bg_x + 2, guesses_count*84.5 + LETTER_Y_SPACING))
    else:
        new_letter = Letter(key_pressed, (current_letter_bg_x, guesses_count*84.5 + LETTER_Y_SPACING))
    current_letter_bg_x +=LETTER_X_SPACING
    guesses[guesses_count].append(new_letter)
    current_guess.append(new_letter)
    for guess in guesses:
        for letter in guess:
            letter.draw()
    pygame.display.update()

def delete_letter():
    # Deletes the last letter from the guess.
    global current_guess_string,current_letter_bg_x
    guesses[guesses_count][-1].delete()
    guesses[guesses_count].pop()
    current_guess_string = current_guess_string[:-1]
    current_guess.pop()
    current_letter_bg_x -= LETTER_X_SPACING


def draw_main_screen():
    SCREEN.fill("white")
    SCREEN.blit(BACKGROUND, BACKGROUND_RECT)
    SCREEN.blit(heading_text, heading_position)
    SCREEN.blit(stats_icon, stats_rect)
    SCREEN.blit(help_icon, help_rect)
    SCREEN.blit(settings_icon, settings_rect)

    # Draw all the guesses
    for guess in guesses:
        for letter in guess:
            letter.draw()
    
    # Draw the indicators
    for indicator in indicators:
        indicator.draw()

    pygame.display.update()  # Update the display


# In the main loop:
while True:
    if game_result != "":
        play_again()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if help_rect.collidepoint(event.pos):  # Detect if help icon is clicked
                if(sound_enabled):
                    key_press_sound.play()
                show_instructions()  # Show the instructions when help icon is clicked
            elif stats_rect.collidepoint(event.pos) and not stats_visible:
                if(sound_enabled):
                    key_press_sound.play()
                show_stats()  # Show stats when stats icon is clicked
            elif settings_rect.collidepoint(event.pos):
                if(sound_enabled):
                    key_press_sound.play()
                show_settings()  # Show the settings menu when the settings icon is clicked
            # Additional conditions can be added as needed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if game_result != "":
                    reset()
                else:
                    if len(current_guess_string) == 5 and current_guess_string.lower() in WORDS:
                        check_guess(current_guess)
            elif event.key == pygame.K_BACKSPACE:
                if len(current_guess_string) > 0:
                    delete_letter()
            else:
                key_pressed = event.unicode.upper()
                if key_pressed in "QWERTYUIOPASDFGHJKLZXCVBNM" and key_pressed != "":
                    if len(current_guess_string) < 5:
                        create_new_letter()


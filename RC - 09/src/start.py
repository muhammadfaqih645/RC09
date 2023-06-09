import pygame
import cv2
import os
import random
from src.music import *
from src.tile import *

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
FPS = 60
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

class Start():
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.level_complete = False

        self.all_food = [f for f in os.listdir('assets/cards/') if os.path.join('assets/cards/', f)]
        self.img_width, self.img_height = (128, 128)
        self.padding = 20
        self.margin_top = 160
        self.cols = 4
        self.rows = 2
        self.width = WINDOW_WIDTH

        self.__score = 0
        self.tiles_group = pygame.sprite.Group()

        self.flipped = []
        self.flipped_group = []
        self.frame_count = 0
        self.block_game = False
        self.timecounter = 0
        self.countdown = '{:02d}:{:02d}'.format(0, 0)

        self.generate_level(self.difficulty)

        self.is_video_playing = True
        self.get_video()

        self.btn_click = Sound_effect("assets/sound/arrow.mp3")
        self.game_over_sound = Sound_effect("assets/sound/gameover.mp3")

    def add_score(self) :
        self.__score += 100

    def view_score (self) :
        return self.__score

    def timer(self):
        self.mins = self.time // 60
        self.secs = self.time % 60
        self.countdown = '{:02d}:{:02d}'.format(self.mins, self.secs)
        print(self.countdown, end ='\r')
        self.timecounter += 1
        if self.timecounter == FPS :
            self.time -= 1
            self.timecounter = 0
    
    def set_timer(self, time):
        self.time = time
    
    def add_timer(self):
        self.time = self.time + (10 * 2 * self.difficulty + 10)
    
    def add_flipped_group(self, flipped):
        self.flipped_group.extend(flipped)

    def update(self, event_list):
        self.draw()
        self.user_input(event_list)
        self.check_level_complete(event_list)

    def check_level_complete(self, event_list):
        if not self.level_complete :
            self.timer()
            if not self.block_game:
                for event in event_list:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for tile in self.tiles_group:
                            if tile.rect.collidepoint(event.pos) and tile not in self.flipped_group:
                                self.flipped.append(tile)
                                tile.show()
                                if len(self.flipped) == 2:
                                    if self.flipped[0].name != self.flipped[1].name:
                                        self.block_game = True
                                    elif self.flipped[0].position() != self.flipped[1].position():
                                        self.add_score()
                                        self.add_flipped_group(self.flipped)
                                        self.flipped = []
                                        for tile in self.tiles_group:
                                            if tile.shown:
                                                self.level_complete = True
                                            else:
                                                self.level_complete = False
                                                break
                                        if self.level_complete :
                                            self.add_timer()
                                    else:
                                        self.false_cards.play()
                                        self.block_game = True
            else:
                self.frame_count += 1
                if self.frame_count == FPS/2:
                    self.frame_count = 0
                    self.block_game = False
                    for tile in self.tiles_group:
                        if tile in self.flipped:
                            tile.hide()
                    self.flipped = []

    def generate_level(self, level):
        self.food = self.select_random_food(level)
        self.level_complete = False
        self.rows = level + 1
        self.cols = 4
        self.generate_tileset(self.food)

    def generate_tileset(self, food):
        self.cols = self.rows = self.cols if self.cols >= self.rows else self.rows

        TILES_WIDTH = (self.img_width * self.cols + self.padding * 3)
        LEFT_MARGIN = RIGHT_MARGIN = (self.width - TILES_WIDTH) // 2
        self.tiles_group.empty()

        for i in range(len(food)):
            x = LEFT_MARGIN + ((self.img_width + self.padding) * (i % self.cols))
            y = self.margin_top + (i // self.rows * (self.img_height + self.padding))
            tile = Tile(food[i], x, y)
            self.tiles_group.add(tile)

    def select_random_food(self, level):
        food = random.sample(self.all_food, (level + level + 2))
        food_copy = food.copy()
        food.extend(food_copy)
        random.shuffle(food)
        return food

    def user_input(self, event_list):
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.level_complete:
                    self.generate_level(self.difficulty)
                elif event.key == pygame.K_ESCAPE:
                    self.level_complete = True
                    self.add_timer()
                
    def next_level(self):
        next_levelimages = pygame.image.load("assets/images/nextlevel.png")
        next_levelimages = pygame.transform.scale(next_levelimages, (600, 300))
        posisiX = 600 
        posisiY = 200
        next_level_rect = next_levelimages.get_rect(midtop = (posisiX,posisiY))
        screen.blit(next_levelimages, next_level_rect)

    def draw(self):
        screen.fill(BLACK)

        title_font = pygame.font.Font('assets/fonts/font.ttf', 44)
        content_font = pygame.font.Font('assets/fonts/font.ttf', 24)

        title_text = title_font.render('Memory Cards Game', True, WHITE)
        title_rect = title_text.get_rect(midtop=(WINDOW_WIDTH // 2, 10))

        timer_text = content_font.render('Time : '+ self.countdown, True, RED)
        timer_rect = timer_text.get_rect(midtop=(WINDOW_WIDTH // 2 - 100, 80))

        score_text = content_font.render('Score : ' + str(self.view_score()), True, WHITE)
        score_rect = score_text.get_rect(midtop=(WINDOW_WIDTH // 2 + 100, 80))

        info_text = content_font.render('Find Pair of the Cards', True, WHITE)
        info_rect = info_text.get_rect(midtop=(WINDOW_WIDTH // 2, 120))
        
        next_text = content_font.render('Press Space Button to Continue', True, WHITE, RED)
        next_rect = next_text.get_rect(midbottom=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 290))
        
        if self.is_video_playing:
            if self.success:
                screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0, 0))
            else:
                self.get_video()
        else:
            screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0, 0))

        screen.blit(title_text, title_rect)
        screen.blit(timer_text, timer_rect)
        screen.blit(score_text, score_rect)
        screen.blit(info_text, info_rect)

        self.tiles_group.draw(screen)
        self.tiles_group.update()

        if self.level_complete:
            screen.blit(next_text, next_rect)
            self.next_level()

    def get_video(self):
        self.img = cv2.imread('assets/images/playbg.jpg')
        self.img = cv2.resize(self.img,dsize=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.success = True
        self.shape = self.img.shape[1::-1]
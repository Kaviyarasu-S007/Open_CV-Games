import pygame
from pygame.locals import *
import random
from tkinter import *
import cv2
from cvzone.HandTrackingModule import HandDetector

# Initialize Pygame
pygame.init()

# Initialize Pygame mixer for sound
pygame.mixer.init()

detector = HandDetector(detectionCon=0.8, maxHands=1)

video = cv2.VideoCapture(0)

win = Tk()

# create window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# colors
gray = (100, 100, 100)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (139, 69, 19)  #brown

# Load sounds
bike_sound = pygame.mixer.Sound("Images/bikes.mp3")
road_noise = pygame.mixer.Sound("Images/road.mp3")
crash_sound = pygame.mixer.Sound("Images/crashs.mp3")

# game setting
gameover = False
speed = 8
score = 0

# marker size
marker_width = 10
marker_height = 50

# road and edge markers
road = (100, 0, 300, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# x coordinates of lanes
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# for animation of lane markers
lane_marker_move_y = 0

# bike image
class Vehicle(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # fitting bike images
        image_scale = 60 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        # objects place
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

# fitting objects
class Object(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # fitting bike images
        image_scale = 110 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        # objects place
        self.rect = self.image.get_rect()
        self.rect.center = [40, y]

class PlayerVehicle(Vehicle):

    def __init__(self, x, y):
        image = pygame.image.load('Images/bike2.png')
        super().__init__(image, x, y)

# players start position
player_x = 250
player_y = 400

# player bike
player_group = pygame.sprite.Group()
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load other vehicles
image_filenames = ['bike.png', 'car.png', 'bike3.png', 'bike4.png', 'bike5.png', 'bike6.png', 'bike7.png', 'truck.png',
                   'trailer.png', 'taxi.png', 'van.png']
obj_filenames = ['tree1.png', 'tree2.png', 'tree3.png', 'bush1.png', 'bush2.png', 'bush3.png', 'bush4.png', 'bush5.png',
                 'build1.png', 'build2.png', 'build3.png', 'build4.png', 'stone1.png']
vehicle_images = []
obj_images = []
for image_filename in image_filenames:
    image = pygame.image.load('Images/' + image_filename)
    vehicle_images.append(image)

# object insert
for obj_filename in obj_filenames:
    image1 = pygame.image.load('Images/' + obj_filename)
    obj_images.append(image1)

# sprite group for vehicles
vehicle_group = pygame.sprite.Group()
obj_group = pygame.sprite.Group()

# Load crash
crash = pygame.image.load('Images/crash.png')
crash_rect = crash.get_rect()

# game loop
clock = pygame.time.Clock()
fps = 120
running = True

# Play the road noise continuously
pygame.mixer.music.load("Images/road.mp3")
pygame.mixer.music.play(-1)

while running:
    clock.tick(fps)
    ret, frame = video.read()
    hands, img = detector.findHands(frame)

    if hands:
        lmlist = hands[0]
        #print(lmlist)
        FINGERUP = detector.fingersUp(lmlist)
        print(FINGERUP)

    # Handle player movement based on finger gestures
    if FINGERUP == [0, 1, 1, 0, 0]:
        # Move left, but stop at the left edge marker
        if player.rect.left - 30 >= left_edge_marker[0] + left_edge_marker[2]:
            player.rect.x -= 30
            bike_sound.play()

    if FINGERUP == [0, 1, 1, 1, 0]:
        # Move right, but stop at the right edge marker
        if player.rect.right + 30 <= right_edge_marker[0]:
            player.rect.x += 30
            bike_sound.play()

    # Check if the bike has reached the road edge
    if player.rect.left <= left_edge_marker[0] + left_edge_marker[2]:
        player.rect.left = left_edge_marker[0] + left_edge_marker[2]
        # Play crash sound when hitting the left edge
        crash_sound.play()

    if player.rect.right >= right_edge_marker[0]:
        player.rect.right = right_edge_marker[0]
        # Play crash sound when hitting the right edge
        crash_sound.play()

    for vehicle in vehicle_group:
        if pygame.sprite.collide_rect(player, vehicle):
            gameover = True
            if FINGERUP == [0, 1, 1, 0, 0]:
                player.rect.left = vehicle.rect.left
                crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            elif FINGERUP == [0, 1, 1, 1, 0]:
                player.rect.right = vehicle.rect.left
                crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

            for obj in obj_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    gameover = True

    # draw the grass(background)
    screen.fill(yellow)

    # draw road
    pygame.draw.rect(screen, gray, road)

    # draw the edge markers(side lines)
    pygame.draw.rect(screen, red, left_edge_marker)
    pygame.draw.rect(screen, red, right_edge_marker)

    # draw the lanes(center lines)
    lane_marker_move_y += speed * 2  # speed
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    # draw the bike
    player_group.draw(screen)

    # add two vehicles
    if len(vehicle_group) < 2:
        # ensure the gap b/t vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False
        if add_vehicle:
            # select random lane
            lane = random.choice(lanes)

            # select random vehicles
            image = random.choice(vehicle_images)
            image1 = random.choice(obj_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)
            obj = Object(image1, lane, height / -2)
            obj_group.add(obj)

    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        # remove vehicle once it goes off screen
        if vehicle.rect.top >= height:
            vehicle.kill()

            # add to score
            score += 1

            # speed up game after 5 vehicles
            if score > 0 and score % 5 == 0:
                speed += 1

    for obj in obj_group:
        obj.rect.y += speed

        # remove vehicle once it goes off screen
        if obj.rect.top >= height:
            obj.kill()

            # add to score
            score += 1

            # speed up game after 5 vehicles
            if score > 0 and score % 5 == 0:
                speed += 1

    # draw the vehicles
    vehicle_group.draw(screen)
    obj_group.draw(screen)

    # display score
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Score' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, 450)
    screen.blit(text, text_rect)

    # check if collison occurs
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]

    # display game over
    if gameover:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, red, (0, 50, width, 100))

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game Over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

        # Play crash sound when game over
        crash_sound.play()

    pygame.display.update()

    # check for replay
    while gameover:
        clock.tick(fps)

        for event in pygame.event.get():

            if event.type == QUIT:
                gameover = False
                running = False

            # get input from player
            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False  # game restarts
                    speed = 8
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    # exit from game(loop)
                    gameover = False
                    running = False

# Stop the road noise when exiting the game
pygame.mixer.music.stop()

# pygame.quit()



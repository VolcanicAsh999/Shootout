import pygame
import time
import sys

pygame.init()

screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
pygame.display.set_caption('Shootout')

player1x, player1y = 80, 110
player2x, player2y = screen.get_width() - 100, 110

DEFAULT_LIVES = 5

class Player:
    def __init__(self, x, y, key_left, key_right, key_jump, key_shoot, color):
        self.drect = pygame.Rect(x, y, 20, 20)
        self.rect = pygame.Rect(x, y-5, 20, 20)
        self.color = pygame.Color(color)
        self.dy = 0
        self.jumping = True
        self.ypos = 0
        self.keys = [key_left, key_right, key_jump, key_shoot]
        self.facing = (1 if color == 'red' else -1)
        self.movex = 0
        self.dx = 0

    def render(self, game, keys_pressed):
        self.draw(game)
        keys_held = pygame.key.get_pressed()
        if keys_held[self.keys[0]]:
            self.move(game, -0.3)
            if self.facing == -1: self.facing = 1
        if keys_held[self.keys[1]]:
            self.move(game, 0.3)
            if self.facing == 1: self.facing = -1
        if keys_held[self.keys[2]]:
            self.jump(game)
        for key in keys_pressed:
            if key == self.keys[3]:
                self.shoot(game)
        self.fall(game)
        self.check_out_of_bounds(game)
        self.check_stuck(game)
        if self.dx > 0:
            self.dx -= 0.1
            self.rect = self.rect.move(self.dx * 10, 0)
            for platform in game.platforms:
                if platform.rect.colliderect(pygame.Rect(self.rect.x, self.rect.y - 10, 20, 20)):
                    self.rect = self.rect.move(self.dx * -10, 0)
                    return
            self.drect = pygame.Rect(self.rect.x, self.rect.y, 20, 20)
        elif self.dx < 0:
            self.dx += 0.1
            self.rect = self.rect.move(self.dx * 10, 0)
            for platform in game.platforms:
                if platform.rect.colliderect(pygame.Rect(self.rect.x, self.rect.y - 10, 20, 20)):
                    self.rect = self.rect.move(self.dx * -10, 0)
                    return
            self.drect = pygame.Rect(self.rect.x, self.rect.y, 20, 20)

    def draw(self, game):
        pygame.draw.rect(game.screen, self.color, self.drect)

    def move(self, game, x):
        self.movex += x
        if self.movex >= 1 or self.movex <= -1:
            self.rect = self.rect.move(self.movex, 0)
            for platform in game.platforms:
                if platform.rect.colliderect(pygame.Rect(self.rect.x, self.rect.y - 10, 20, 20)):
                    self.rect = self.rect.move(-self.movex, 0)
                    self.movex = 0
                    return
            self.drect = pygame.Rect(self.rect.x, self.rect.y, 20, 20)
            self.movex = 0

    def fall(self, game):
        self.dy += 0.01
        if self.dy > 1: self.dy = 1
        self.rect = self.rect.move(0, int(self.dy))
        for platform in game.platforms:
            if platform.rect.colliderect(pygame.Rect(self.rect.x + 3, self.rect.y + 20, 13, 1)):
                self.rect = self.rect.move(0, -int(self.dy))
                self.dy = 0
                if self.jumping: self.jumping = False
                return
            elif self.jumping and platform.rect.colliderect(pygame.Rect(self.rect.x + 3, self.rect.y - 1, 13, 1)):
                self.rect = self.rect.move(0, -int(self.dy))
                self.dy = 0
                self.jumping = False
                return
        self.ypos -= int(self.dy)
        self.drect = pygame.Rect(self.rect.x, self.rect.y, 20, 20)

    def jump(self, game):
        for platform in game.platforms:
            if platform.rect.colliderect(pygame.Rect(self.rect.x, self.rect.y + 10, 20, 20)):
                self.jumping = True
                self.dy = -2
                self.ypos += 2
                self.rect = self.rect.move(0, self.dy)
                self.drect = pygame.Rect(self.rect.x, self.rect.y, 20, 20)

    def check_out_of_bounds(self, game):
        if self.rect.y > screen.get_height():
            game.die(self)
        if self.rect.x < 2:
            self.rect = self.rect.move(screen.get_width()-3, -3)
            self.drect = self.drect.move(screen.get_width()-3, -3)
        if self.rect.x > screen.get_width() - 2:
            self.rect = self.rect.move(-screen.get_width()+3, -3)
            self.rect = self.rect.move(-screen.get_width()+3, -3)

    def check_stuck(self, game):
        for platform in game.platforms:
            if platform.rect.colliderect(pygame.Rect(self.rect.x + 10, self.rect.y - 1, 1, 1)):
                self.rect = self.rect.move(0, 10)
                self.drect = self.drect.move(0, 10)
            elif platform.rect.colliderect(pygame.Rect(self.rect.x + 10, self.rect.y + 20, 1, 1)):
                self.rect = self.rect.move(0, -3)
                self.drect = self.drect.move(0, -3)

    def shoot(self, game):
        team = game.get_team(self)
        game.bullets.append(Bullet(self.rect.x + (self.facing * -20), self.rect.y, ('blue' if team == 1 else 'red'), -self.facing))

class Platform:
    def __init__(self, x, y, width):
        self.rect = pygame.Rect(x, y, width, 10)
        self.color = pygame.Color('black')

    def render(self, game):
        self.draw(game)
    def draw(self, game):
        pygame.draw.rect(game.screen, self.color, self.rect)

class Wall(Platform):
    def __init__(self, x, y, height):
        super().__init__(x, y, 10)
        self.rect.height = height

class Bullet:
    def __init__(self, x, y, color, dir):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.dir = dir
        self.color = pygame.Color(color)
        self.team = (1 if color == 'blue' else 2)

    def render(self, game):
        self.rect.x += self.dir
        if self.team == 1 and pygame.sprite.collide_rect(self, game.player2):
            #game.player2.move(game, self.dir * 50)
            game.player2.dx = self.dir * 1.7
            game.player2.dy = -1.3
            game.player2.ypos += 1.3
            game.player2.rect = game.player2.rect.move(0, -1.3)
            game.player2.drect = game.player2.drect.move(0, -1.3)
            game.player2.jumping = True
            game.bullets.remove(self)
        elif self.team == 2 and pygame.sprite.collide_rect(self, game.player1):
            #game.player1.move(game, self.dir * 50)
            game.player1.dx = self.dir * 1.7
            game.player1.dy = -1.3
            game.player1.ypos += 1.3
            game.player1.rect = game.player1.rect.move(0, -1.3)
            game.player1.drect = game.player1.drect.move(0, -1.3)
            game.player1.jumping = True
            game.bullets.remove(self)
        elif self.rect.x < 0 or self.rect.x > game.screen.get_width():
            game.bullets.remove(self)
        for platform in game.platforms:
            if type(platform) == Wall:
                if self.rect.colliderect(platform.rect):
                    game.bullets.remove(self)
        self.draw(game)
        
    def draw(self, game):
        pygame.draw.rect(game.screen, self.color, self.rect)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.platforms = []
        self.bullets = []
        self.p1lives = DEFAULT_LIVES
        self.p2lives = DEFAULT_LIVES
        self.player1 = Player(player1x, player1y, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, 'blue')
        self.player2 = Player(player2x, player2y, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, 'red')
        self.platforms.extend([
            Platform(60, 140, 120),
            Platform(self.screen.get_width() - 180, 140, 120),
            Platform((self.screen.get_width() // 2) - 90, 200, 180),
            Platform(0, 260, 60),
            Platform(self.screen.get_width() - 60, 260, 60),
            Platform((self.screen.get_width() // 2) - 140, 260, 280),
            Platform(70, 320, 100),
            Platform(self.screen.get_width() - 170, 320, 100),
            Platform((self.screen.get_width() // 2) - 30, 380, 60),
            Platform(self.screen.get_width() - 140, 380, 140),
            Platform(0, 380, 140),
        ])
        self.platforms.extend([
            Wall((self.screen.get_width() // 2) - 5, 30, 170),
        ])
        self.get_team = lambda x: 1 if (x == self.player1) else 2
        self.keys = []
        self.font = pygame.font.SysFont('Open Sans', 36)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                self.keys.append(event.key)
        self.render()
        self.keys.clear()

    def render(self):
        self.screen.fill(pygame.Color('white'))
        self.player1.render(self, self.keys)
        self.player2.render(self, self.keys)
        for platform in self.platforms:
            platform.render(self)
        for bullet in self.bullets:
            bullet.render(self)
        self.screen.blit(self.font.render('Lives: %s' % self.p1lives, 1, pygame.Color('blue')), (3, 0))
        self.screen.blit(self.font.render('Lives: %s' % self.p2lives, 1, pygame.Color('red')), (self.screen.get_width() - 101, 0))
        pygame.display.update()

    def loop(self):
        while True: self.update()

    def die(self, player):
        if player == self.player1:
            self.p1lives -= 1
            self.player1.rect.x, self.player1.rect.y = player1x, player1y
            self.player1.drect.x, self.player1.drect.y = player1x, player1y - 5
            self.player1.dx = 0
        elif player == self.player2:
            self.p2lives -= 1
            self.player2.rect.x, self.player2.rect.y = player2x, player2y
            self.player2.drect.x, self.player2.drect.y = player2x, player2y - 5
            self.player2.dx = 0
        if self.p1lives <= 0:
            self.p2wins()
        elif self.p2lives <= 0:
            self.p1wins()

    def p1wins(self):
        self.screen.fill((255, 255, 255, 255))
        screen.blit(pygame.font.SysFont('Open Sans', 48).render('Player 1 Wins!', 1, (0, 0, 0, 0)), (200, 150))
        pygame.display.update()
        self.p1lives = DEFAULT_LIVES
        self.p2lives = DEFAULT_LIVES
        self.player2.rect.x, self.player2.rect.y = player2x, player2y
        self.player2.drect.x, self.player2.drect.y = player2x, player2y - 5
        self.player1.rect.x, self.player1.rect.y = player1x, player1y
        self.player1.drect.x, self.player1.drect.y = player1x, player1y - 5
        time.sleep(3)
        self.intro()
        
    def p2wins(self):
        self.screen.fill((255, 255, 255, 255))
        screen.blit(pygame.font.SysFont('Open Sans', 48).render('Player 2 Wins!', 1, (0, 0, 0, 0)), (200, 150))
        pygame.display.update()
        self.p1lives = DEFAULT_LIVES
        self.p2lives = DEFAULT_LIVES
        self.player2.rect.x, self.player2.rect.y = player2x, player2y
        self.player2.drect.x, self.player2.drect.y = player2x, player2y - 5
        self.player1.rect.x, self.player1.rect.y = player1x, player1y
        self.player1.drect.x, self.player1.drect.y = player1x, player1y - 5
        time.sleep(3)
        self.intro()

    def intro(self):
        pressed = False
        font = pygame.font.SysFont('Open Sans', 48)
        while not pressed:
            screen.fill(pygame.Color('white'))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pressed = True
            screen.blit(font.render('Press', 1, pygame.Color('black')), (270, 150))
            screen.blit(font.render('SPACE', 1, pygame.Color('black')), (260, 200))
            pygame.display.update()
            

def main():
    game = Game(screen)
    game.intro()
    game.loop()

if __name__ == '__main__':
    main()

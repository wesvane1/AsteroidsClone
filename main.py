import pygame
import random

# Game Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH//2, SCREEN_HEIGHT-20))
        self.speed = 5
        self.lives = 3  # Player starts with 3 lives

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        return Laser(self.rect.midtop, friendly=True)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(midtop=pos)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, friendly=True):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = 10
        self.friendly = friendly

    def update(self):
        if self.friendly:
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.drop_count = 0

    def update(self):
        self.rect.x += self.direction
        self.drop_count += 1

        if self.drop_count % 60 == 0:
            self.direction *= -1
            self.rect.y += 20

    def shoot(self):
        # Random chance of shooting
        if random.randint(1, 1000) == 1:
            return EnemyBullet(self.rect.midbottom)
        return None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        
        self.all_sprites = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # Load sounds
        self.shoot_sound = pygame.mixer.Sound('shoot.wav')
        self.explosion_sound = pygame.mixer.Sound('explosion.wav')
        self.invaderkilled_sound = pygame.mixer.Sound('invaderkilled.wav')
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Create alien formation
        for row in range(5):
            for col in range(10):
                alien = Alien(100 + col * 60, 50 + row * 50)
                self.all_sprites.add(alien)
                self.aliens.add(alien)

        self.score = 0
        self.font = pygame.font.Font(None, 36)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                laser = self.player.shoot()
                self.all_sprites.add(laser)
                self.lasers.add(laser)
                self.shoot_sound.play()  # Play shooting sound
        return True

    def update(self):
        self.player.move()
        self.all_sprites.update()
        
        # Enemy random shooting
        for alien in self.aliens:
            bullet = alien.shoot()
            if bullet:
                self.all_sprites.add(bullet)
                self.enemy_bullets.add(bullet)
        
        # Player laser hits aliens
        hits = pygame.sprite.groupcollide(self.lasers, self.aliens, True, True)
        if hits:
            self.invaderkilled_sound.play()  # Play invader killed sound
        self.score += len(hits) * 10
        
        # Enemy bullets hit player
        player_bullet_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if player_bullet_hits:
            self.player.lives -= len(player_bullet_hits)
            self.explosion_sound.play()  # Play explosion sound
        
        # Aliens touch player lose a life
        alien_touch_hits = pygame.sprite.spritecollide(self.player, self.aliens, False)
        if alien_touch_hits:
            self.player.lives -= len(alien_touch_hits)
            self.explosion_sound.play()  # Play explosion sound
        
        # Check game over conditions
        if self.player.lives <= 0:
            self.show_lose_screen()
            return False
        
        # Check win condition
        if not self.aliens:
            self.show_win_screen()
            return False
        
        return True

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # Draw score and lives
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        lives_text = self.font.render(f'Lives: {self.player.lives}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        
        pygame.display.flip()

    def show_win_screen(self):
        self.screen.fill(BLACK)
        win_text = self.font.render('You Win!', True, WHITE)
        score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
        self.screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        pygame.display.flip()
        pygame.time.wait(3000)

    def show_lose_screen(self):
        self.screen.fill(BLACK)
        lose_text = self.font.render('Game Over!', True, WHITE)
        score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
        self.screen.blit(lose_text, (SCREEN_WIDTH//2 - lose_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        pygame.display.flip()
        pygame.time.wait(3000)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            running = self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

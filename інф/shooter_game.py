from pygame import *
from random import randint
from time import time as timer

# Шрифти і написи
font.init()
font1 = font.Font(None, 80)
win = font1.render('YOU WIN', True, (255, 255, 255))
lose = font1.render('YOU LOSE', True, (180, 0, 0))
font2 = font.Font(None, 36)

# Музика
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

img_back = 'galaxy.jpg'
img_hero = 'rocket.png'
img_bullet = 'bullet.png'
img_enemy = 'ufo.png'
img_ast = 'asteroid.png'
img_bust = 'upgrade.png'
img_upgrade = 'upgradee.png'

score = 0
goal = 20
lost = 0
max_lost = 3
life = 3

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.speed_original = player_speed  # Зберігаємо оригінальну швидкість
        self.speed_boosted = player_speed * 2  # Подвоюємо швидкість для прискорення
        self.boost_time = 0  # Час, коли почалося прискорення
        self.boost_duration = 5  # Тривалість прискорення в секундах
        self.asteroid_busting_time = 0  # Час, коли почалося ламання астероїдів
        self.asteroid_busting_duration = 10  # Тривалість можливості ламати астероїди

    def update(self):
        # Якщо прискорення активне, перевіряємо, чи закінчився час прискорення
        if self.boost_time > 0 and timer() - self.boost_time >= self.boost_duration:
            self.speed = self.speed_original  # Повертаємо оригінальну швидкість
            self.boost_time = 0  # Завершуємо прискорення

        # Якщо можливість ламати астероїди активна, перевіряємо, чи закінчився час
        if self.asteroid_busting_time > 0 and timer() - self.asteroid_busting_time >= self.asteroid_busting_duration:
            self.asteroid_busting_time = 0  # Завершуємо можливість ламати астероїди

        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

    def activate_boost(self):
        self.speed = self.speed_boosted  # Збільшуємо швидкість
        self.boost_time = timer()  # Запускаємо таймер прискорення

    def activate_asteroid_busting(self):
        self.asteroid_busting_time = timer()  # Запускаємо таймер для ламання астероїдів

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

        # Перевірка колізій з астероїдами
        if ship.asteroid_busting_time > 0:  # Якщо активне руйнування астероїдів
            for asteroid in asteroids:
                if self.rect.colliderect(asteroid.rect):  # Якщо пуля перетинається з астероїдом
                    asteroid.kill()  # Ламаємо астероїд

win_width = 700
win_height = 500
display.set_caption('Shooter')
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)

monsters = sprite.Group()
for i in range(1, 4):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(1, 3):
    asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 70, 50, randint(1, 7))
    asteroids.add(asteroid)

upgrades = sprite.Group()
for i in range(1, 3):
    upgrade = Enemy(img_bust, randint(30, win_width - 30), -40, 70, 50, randint(1, 5))
    upgrades.add(upgrade)

upgrades2 = sprite.Group()
for i in range(1, 3):
    upgrade2 = Enemy(img_upgrade, randint(30, win_width - 30), -40, 70, 50, randint(1, 5))
    upgrades2.add(upgrade2)

bullets = sprite.Group()

finish = False
run = True
rel_time = False
num_fire = 0

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and not rel_time:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()

                if num_fire >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True

    if not finish:
        window.blit(background, (0, 0))

        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update()
        upgrades.update()
        upgrades2.update()

        ship.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        upgrades.draw(window)
        upgrades2.draw(window)

        if rel_time:
            now_time = timer()
            if now_time - last_time < 3:
                reload = font2.render('Wait, reload...', 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                rel_time = False

        collisions = sprite.groupcollide(monsters, bullets, True, True)
        for c in collisions:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if sprite.spritecollide(ship, monsters, True) or sprite.spritecollide(ship, asteroids, True):
            life -= 1  # Зменшуємо кількість життів
            if life == 0 or lost >= max_lost:
                finish = True
                window.blit(lose, (200, 200))  # Вивести "YOU LOSE"

        if sprite.spritecollide(ship, upgrades, True):  # Якщо корабель торкнувся апгрейду
            ship.activate_boost()  # Активуємо прискорення

        if sprite.spritecollide(ship, upgrades2, True):  # Якщо корабель торкнувся апгрейду для ламання астероїдів
            ship.activate_asteroid_busting()  # Активуємо можливість ламати астероїди

        if score >= goal:
            finish = True
            window.blit(win, (200, 200))  # Вивести "YOU WIN"

        text = font2.render("Рахунок:" + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))
        text_lose = font2.render("Пропущено:" + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        life_color = (0, 150, 0) if life == 3 else (150, 150, 0) if life == 2 else (150, 0, 0)
        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10))

        display.update()

    else:
        finish = False
        score = 0
        lost = 0
        num_fire = 0
        life = 3
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for a in asteroids:
            a.kill()
        for u in upgrades:
            u.kill()
        for t in upgrades2:
            t.kill()

        time.delay(3000)
        for i in range(1, 4):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
            monsters.add(monster)
        for i in range(1, 3):
            asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 70, 50, randint(1, 7))
            asteroids.add(asteroid)
        for i in range(1, 3):
            upgrade = Enemy(img_bust, randint(30, win_width - 30), -40, 70, 50, randint(2, 4))
            upgrades.add(upgrade)
        for i in range(1, 3):
            upgrade2 = Enemy(img_upgrade, randint(30, win_width - 30), -40, 70, 50, randint(2, 4))
            upgrades2.add(upgrade2)

    time.delay(50)
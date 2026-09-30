import math
import array
import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick

# Game Engine

WHITE = (255, 255, 255)
PURPLES = [(76, 29, 149), (109, 40, 217), (139, 92, 246), (167, 139, 250), (196, 181, 253)]

THEMES = {
    "dark": {
        "bg": (10, 10, 15), "text": (255, 255, 255),
        "paddle": (255, 255, 255), "ball": (255, 255, 255),
        "bricks": PURPLES, "overlay": (0, 0, 0), "accent": (196, 181, 253),
    },
    "light": {
        "bg": (250, 247, 255), "text": (30, 10, 50),
        "paddle": (91, 33, 182), "ball": (91, 33, 182),
        "bricks": PURPLES, "overlay": (255, 255, 255), "accent": (109, 40, 217),
    },
}

# Task 3: difficulty presets (ball speed, paddle width)
DIFFICULTY = {
    "Easy":   {"speed": 3, "paddle": 140},
    "Medium": {"speed": 4, "paddle": 100},
    "Hard":   {"speed": 6, "paddle": 70},
}


def make_beep(freq, ms, volume=0.4):
    """Task 4: build a short beep in code (no audio files needed)."""
    rate = 22050
    n = int(rate * ms / 1000)
    buf = array.array("h")
    for i in range(n):
        fade = 1 - i / n
        buf.append(int(32767 * volume * fade * math.sin(2 * math.pi * freq * i / rate)))
    return pygame.mixer.Sound(buffer=buf.tobytes())


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 56)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.left = False
        self.right = False
        self.theme = "dark"
        self._init_sound()
        self.start_game("Medium")

    # ---------- Task 4: sound ----------
    def _init_sound(self):
        self.sounds = {}
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.sounds = {
                "brick": make_beep(660, 80),
                "hit": make_beep(330, 60),
                "win": make_beep(880, 400),
                "lose": make_beep(160, 500),
            }
        except Exception as e:
            print("Sound disabled:", e)

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # ---------- setup / restart ----------
    def start_game(self, difficulty):
        cfg = DIFFICULTY[difficulty]
        self.difficulty = difficulty
        self.speed = cfg["speed"]
        self.paddle = Paddle(self.width // 2 - cfg["paddle"] // 2, self.height - 30, cfg["paddle"], 14)
        self.ball = Ball(self.width // 2, self.height - 50, radius=8)
        self.ball.vx, self.ball.vy = self.speed, -self.speed
        self.rows, self.cols = 5, 8
        self.bricks = self._build_bricks(self.rows, self.cols)
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.paused = False
        self.in_menu = False
        self.result = None  # "win" or "lose"

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60
        brick_w = (self.width - margin * 2 - gap * (cols - 1)) // cols
        brick_h = 22
        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)
                bricks.append(Brick(x, y, brick_w, brick_h))
        return bricks

    # ---------- input ----------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.left = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.right = True
            elif event.key == pygame.K_t:
                self.theme = "light" if self.theme == "dark" else "dark"
            elif event.key in (pygame.K_p, pygame.K_SPACE) and not self.game_over and not self.in_menu:
                self.paused = not self.paused
            elif event.key == pygame.K_m and not self.game_over and not self.in_menu:
                self.in_menu = True
                self.paused = False
            elif self.game_over or self.in_menu:
                # Task 3: replay menu
                if event.key == pygame.K_1:
                    self.start_game("Easy")
                elif event.key == pygame.K_2:
                    self.start_game("Medium")
                elif event.key == pygame.K_3:
                    self.start_game("Hard")
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.left = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.right = False
        elif event.type == pygame.MOUSEMOTION and not (self.game_over or self.paused or self.in_menu):
            # bonus: mouse also moves the paddle
            self.paddle.x = max(0, min(event.pos[0] - self.paddle.width // 2,
                                       self.width - self.paddle.width))

    def handle_input(self):
        if self.game_over or self.paused or self.in_menu:
            return
        keys = pygame.key.get_pressed()
        if self.left or keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)
        if self.right or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

    def update(self):
        if self.game_over or self.paused or self.in_menu:
            return

        self.ball.move()

        b = self.ball

        # walls (clamped so the ball can't get stuck in them)
        if b.x - b.radius <= 0:
            b.x = b.radius
            b.vx = abs(b.vx)
            self.play("hit")
        elif b.x + b.radius >= self.width:
            b.x = self.width - b.radius
            b.vx = -abs(b.vx)
            self.play("hit")
        if b.y - b.radius <= 0:
            b.y = b.radius
            b.vy = abs(b.vy)
            self.play("hit")

        # Task 1: paddle - only bounce when moving down, angle by hit position
        pr = self.paddle.rect()
        if b.rect().colliderect(pr) and b.vy > 0:
            offset = (b.x - (pr.x + pr.width / 2)) / (pr.width / 2)  # -1..1
            offset = max(-1, min(1, offset))
            b.vy = -abs(b.vy)
            b.vx = offset * self.speed * 1.5
            if abs(b.vx) < 1:
                b.vx = 1 if b.vx >= 0 else -1
            b.y = pr.top - b.radius
            self.play("hit")

        # Task 1: bricks - bounce off the side actually hit
        for brick in self.bricks:
            if brick.alive and b.rect().colliderect(brick.rect()):
                brick.alive = False
                self.score += 1
                self.play("brick")
                br = brick.rect()
                overlap_x = min(b.x + b.radius - br.left, br.right - (b.x - b.radius))
                overlap_y = min(b.y + b.radius - br.top, br.bottom - (b.y - b.radius))
                if overlap_x < overlap_y:
                    b.vx *= -1   # hit left/right side
                else:
                    b.vy *= -1   # hit top/bottom
                break

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
                self.play("lose")
            else:
                self._reset_ball()

        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"
            self.play("win")

    def _reset_ball(self):
        self.ball.x, self.ball.y = self.width // 2, self.height - 50
        self.ball.vx, self.ball.vy = self.speed, -self.speed

    def _center(self, screen, font, text, y, color=WHITE):
        surf = font.render(text, True, color)
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))

    def render(self, screen):
        t = THEMES[self.theme]
        screen.fill(t["bg"])

        pygame.draw.rect(screen, t["paddle"], self.paddle.rect())
        pygame.draw.circle(screen, t["ball"], (int(self.ball.x), int(self.ball.y)), self.ball.radius)

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                pygame.draw.rect(screen, t["bricks"][row % len(t["bricks"])], brick.rect())

        screen.blit(self.font.render(f"Score: {self.score}", True, t["text"]), (10, 10))
        screen.blit(self.font.render(f"Lives: {self.lives}", True, t["text"]), (self.width - 130, 10))
        self._center(screen, self.small_font, "T Theme   P Pause   M Menu", 14, t["text"])

        # Task 2: end screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*t["overlay"], 200))
            screen.blit(overlay, (0, 0))
            title = "YOU WIN!" if self.result == "win" else "GAME OVER"
            self._center(screen, self.big_font, title, 160, t["accent"])
            self._center(screen, self.font, f"Final Score: {self.score}", 240, t["text"])
            self._center(screen, self.small_font, "Play again:", 310, t["text"])
            self._center(screen, self.small_font, "1 - Easy    2 - Medium    3 - Hard", 345, t["text"])
            self._center(screen, self.small_font, "Esc - Exit", 385, t["text"])

        # Pause / menu screens
        if self.paused or self.in_menu:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*t["overlay"], 200))
            screen.blit(overlay, (0, 0))
            if self.paused:
                self._center(screen, self.big_font, "PAUSED", 180, t["accent"])
                self._center(screen, self.small_font, "P / Space - Resume", 270, t["text"])
                self._center(screen, self.small_font, "M - Stop game (menu)", 305, t["text"])
            else:
                self._center(screen, self.big_font, "MENU", 160, t["accent"])
                self._center(screen, self.small_font, "Choose difficulty:", 260, t["text"])
                self._center(screen, self.small_font, "1 - Easy    2 - Medium    3 - Hard", 300, t["text"])
                self._center(screen, self.small_font, "Esc - Exit", 340, t["text"])

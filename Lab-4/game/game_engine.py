import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)
BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle = Paddle(width // 2 - 50, height - 30, 100, 14)

        self.ball = Ball(width // 2, height - 50, radius=8)
        self.ball.vx, self.ball.vy = 4, -4

        self.rows, self.cols = 5, 8
        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False
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

    def handle_event(self, event):
        # This game only needs continuously-held-key input for the
        # paddle, handled in handle_input each frame.
        pass

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

    def update(self):
        if self.game_over:
            return

        self.ball.move()

        b = self.ball

        # walls (clamped so the ball can't get stuck in them)
        if b.x - b.radius <= 0:
            b.x = b.radius
            b.vx = abs(b.vx)
        elif b.x + b.radius >= self.width:
            b.x = self.width - b.radius
            b.vx = -abs(b.vx)
        if b.y - b.radius <= 0:
            b.y = b.radius
            b.vy = abs(b.vy)

        # Task 1: paddle - only bounce when moving down, angle by hit position
        pr = self.paddle.rect()
        if b.rect().colliderect(pr) and b.vy > 0:
            offset = (b.x - (pr.x + pr.width / 2)) / (pr.width / 2)  # -1..1
            offset = max(-1, min(1, offset))
            b.vy = -abs(b.vy)
            b.vx = offset * 6
            if abs(b.vx) < 1:
                b.vx = 1 if b.vx >= 0 else -1
            b.y = pr.top - b.radius

        # Task 1: bricks - bounce off the side actually hit
        for brick in self.bricks:
            if brick.alive and b.rect().colliderect(brick.rect()):
                brick.alive = False
                self.score += 1
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
            else:
                self._reset_ball()

        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"

    def _reset_ball(self):
        self.ball.x, self.ball.y = self.width // 2, self.height - 50
        self.ball.vx, self.ball.vy = 4, -4

    def render(self, screen):
        screen.fill(BG)

        pygame.draw.rect(screen, WHITE, self.paddle.rect())
        pygame.draw.circle(screen, WHITE, (int(self.ball.x), int(self.ball.y)), self.ball.radius)

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over and not getattr(self, "_game_over_logged", False):
            # NOTE: no proper end screen yet - see Task 2 in the README.
            if self.result == "win":
                print("You win! Final score:", self.score)
            else:
                print("Game over! Final score:", self.score)
            self._game_over_logged = True

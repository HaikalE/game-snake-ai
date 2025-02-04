import pygame
import sys
import random
import math

# Inisialisasi Pygame
pygame.init()

# Konfigurasi window dan grid
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT

# Batas maksimum partikel (agar tidak freeze karena terlalu banyak partikel)
MAX_PARTICLES = 200

# Flag untuk fullscreen / windowed
FULLSCREEN = True
if FULLSCREEN:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption("Game Snake AI vs AI - Visual Upgrade")
clock = pygame.time.Clock()
FPS = 30  # Untuk pergerakan smooth

# Flag debug
DEBUG_MODE = True

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
DARK_BLUE = (10, 10, 30)
ORANGE = (255, 140, 0)

# Inisialisasi font
font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 60)
try:
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", CELL_SIZE + 4)
except:
    emoji_font = pygame.font.SysFont(None, CELL_SIZE + 4)

# Fungsi blend untuk gradient
def blend_color(color, blend, factor):
    return tuple(int(color[i]*(1 - factor) + blend[i]*factor) for i in range(3))

# ----- Efek Partikel -----
class Particle:
    # Partikel umum (misalnya saat makanan dimakan, shield pecah, atau bonus fire berakhir)
    def __init__(self, pos, color):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.lifetime = random.randint(20, 40)
        self.color = color
        self.size = random.randint(2, 4)

    def update(self):
        self.pos += self.velocity
        self.lifetime -= 1
        if self.size > 0:
            self.size -= 0.1
        if (self.pos.x < -10 or self.pos.x > WINDOW_WIDTH + 10 or
                self.pos.y < -10 or self.pos.y > WINDOW_HEIGHT + 10):
            self.lifetime = 0

    def draw(self, surface):
        if self.lifetime > 0 and self.size > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            alpha = min(max(self.lifetime * 6, 0), 255)
            pygame.draw.circle(s, self.color + (alpha,), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.pos.x - self.size, self.pos.y - self.size))

class FreezeParticle:
    # Partikel khusus untuk efek freeze
    def __init__(self, pos):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        self.lifetime = random.randint(30, 50)
        self.size = random.randint(3, 6)
        self.color = (150, 220, 255)  # Biru muda

    def update(self):
        self.pos += self.velocity
        self.lifetime -= 1
        if self.size > 0:
            self.size -= 0.05

    def draw(self, surface):
        if self.lifetime > 0 and self.size > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            alpha = min(max(self.lifetime * 5, 0), 255)
            pygame.draw.circle(s, self.color + (alpha,), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.pos.x - self.size, self.pos.y - self.size))

class FireParticle:
    # Partikel khusus untuk efek fire
    def __init__(self, pos):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(2, 5)
        self.color = ORANGE

    def update(self):
        self.pos += self.velocity
        self.lifetime -= 1
        if self.size > 0:
            self.size -= 0.1

    def draw(self, surface):
        if self.lifetime > 0 and self.size > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            alpha = min(max(self.lifetime * 6, 0), 255)
            pygame.draw.circle(s, self.color + (alpha,), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.pos.x - self.size, self.pos.y - self.size))

class InvisibilityParticle:
    # Partikel khusus untuk efek invisibility
    def __init__(self, pos):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(2, 4)
        self.color = (200, 200, 255)  # Warna lembut

    def update(self):
        self.pos += self.velocity
        self.lifetime -= 1
        if self.size > 0:
            self.size -= 0.1

    def draw(self, surface):
        if self.lifetime > 0 and self.size > 0:
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            alpha = min(max(self.lifetime * 6, 0), 255)
            pygame.draw.circle(s, self.color + (alpha,), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.pos.x - self.size, self.pos.y - self.size))

particles = []             # Partikel umum
freeze_particles = []      # Partikel untuk freeze
fire_particles = []        # Partikel untuk fire
invis_particles = []       # Partikel untuk invisibility

# ----- Fungsi Utilitas -----
def cell_rect(cell):
    x, y = cell
    return pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def manhattan(cell1, cell2):
    return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])

def predict_future_positions(snake, steps=3):
    predicted = []
    current = snake.get_grid_position()
    d = (int(round(snake.desired_direction.x)), int(round(snake.desired_direction.y)))
    for i in range(steps):
        current = (current[0] + d[0], current[1] + d[1])
        if current[0] < 0 or current[0] >= GRID_WIDTH or current[1] < 0 or current[1] >= GRID_HEIGHT:
            break
        predicted.append(current)
    return predicted

def count_free_space(cell, snakes, obstacles, depth=3):
    visited = set()
    queue = [(cell, 0)]
    free = 0
    while queue:
        current, d = queue.pop(0)
        if d > depth:
            continue
        if current in visited:
            continue
        visited.add(current)
        if not is_collision(current, snakes, obstacles):
            free += 1
        for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
                queue.append((neighbor, d + 1))
    return free

# ----- Kelas Snake -----
class Snake:
    def __init__(self, name, color, start_cell, desired_direction, intelligence=0.8,
                 max_speed=2.0, max_acceleration=0.3, bait_threshold=4):
        self.name = name
        self.color = color
        self.pos = pygame.math.Vector2(start_cell[0] * CELL_SIZE + CELL_SIZE/2,
                                       start_cell[1] * CELL_SIZE + CELL_SIZE/2)
        self.velocity = pygame.math.Vector2(desired_direction).normalize() * max_speed
        self.desired_direction = pygame.math.Vector2(desired_direction).normalize()
        self.base_max_speed = max_speed
        self.max_acceleration = max_acceleration
        self.mass = 1.0
        self.body = [start_cell]
        self.grow = False
        self.score = 0
        self.intelligence = intelligence
        self.bait_threshold = bait_threshold
        self.experience = 0.0

        # Timer/efek power-up (dalam frame)
        self.speed_boost_timer = 0     # Speed Boost
        self.slow_timer = 0            # Slow Trap (efek negatif)
        self.shield_timer = 0          # Shield
        self.invisible_timer = 0       # Invisibility
        self.freeze_timer = 0          # Freeze (jika > 0, snake beku)
        self.fire_timer = 0            # Fire (efek selama 10 detik)
        # Flag untuk menandai bonus fire yang sudah diterima
        self.fire_bonus_active = False

        self.mode = "defensive"  # Mode default

    def get_grid_position(self):
        cell_x = int(self.pos.x) // CELL_SIZE
        cell_y = int(self.pos.y) // CELL_SIZE
        return cell_x, cell_y

    def get_danger_factor(self, snakes, obstacles):
        head = self.get_grid_position()
        dir_x = int(round(self.desired_direction.x))
        dir_y = int(round(self.desired_direction.y))
        d = 0
        while True:
            d += 1
            next_cell = (head[0] + dir_x*d, head[1] + dir_y*d)
            if (next_cell[0] < 0 or next_cell[0] >= GRID_WIDTH or
                next_cell[1] < 0 or next_cell[1] >= GRID_HEIGHT or
                is_collision(next_cell, snakes, obstacles)):
                break
            if d >= 10:
                break
        threshold = 5
        factor = min(d/threshold, 1.0)
        return factor

    def update_physics(self, snakes, obstacles):
        # Cek apakah fire power up sudah habis
        if self.fire_bonus_active and self.fire_timer <= 0:
            # Hapus bonus fire: kurangi score 10 dan hapus 10 segmen (jika memungkinkan)
            self.score = max(0, self.score - 10)
            for _ in range(10):
                if len(self.body) > 1:
                    self.body.pop()
            self.fire_bonus_active = False

        # Jika sedang beku, hanya update timer (tidak bergerak)
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.speed_boost_timer > 0:
                self.speed_boost_timer -= 1
            if self.slow_timer > 0:
                self.slow_timer -= 1
            if self.shield_timer > 0:
                self.shield_timer -= 1
            if self.invisible_timer > 0:
                self.invisible_timer -= 1
            if self.fire_timer > 0:
                self.fire_timer -= 1
            return

        # Normal: Jika tidak invisibility, lakukan perhitungan seperti biasa.
        danger = self.get_danger_factor(snakes, obstacles)
        boost_multiplier = 1.5 if self.speed_boost_timer > 0 else 1.0
        if self.slow_timer > 0:
            boost_multiplier *= 0.5
        effective_max_speed = self.base_max_speed * boost_multiplier * (0.5 + 0.5 * danger)
        desired_velocity = self.desired_direction * effective_max_speed

        force = desired_velocity - self.velocity
        max_force = self.max_acceleration * self.mass
        if force.length() > max_force:
            force.scale_to_length(max_force)
        acceleration = force / self.mass
        friction_coeff = 0.05
        friction = -friction_coeff * self.velocity
        net_acceleration = acceleration + friction
        self.velocity += net_acceleration
        if self.velocity.length() > effective_max_speed:
            self.velocity.scale_to_length(effective_max_speed)
        self.pos += self.velocity

        # Update timer power-up
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.invisible_timer > 0:
            self.invisible_timer -= 1
        if self.fire_timer > 0:
            self.fire_timer -= 1

        current_cell = self.get_grid_position()
        if current_cell != self.body[0]:
            self.body.insert(0, current_cell)
            if not self.grow:
                self.body.pop()
            else:
                self.grow = False
            self.experience += 0.01
            self.intelligence = min(1.0, self.intelligence + 0.00005)

    def change_desired_direction(self, new_direction):
        new_dir = pygame.math.Vector2(new_direction).normalize()
        if len(self.body) > 1 and new_dir == -pygame.math.Vector2(self.desired_direction):
            return
        self.desired_direction = new_dir

    def draw(self, surface):
        # Untuk snake yang sedang invisibility, tampilkan dengan transparansi rendah
        alpha = 50 if self.invisible_timer > 0 else 255

        # Gambar bayangan 3D
        shadow_offset = 3
        head_pos = (int(self.pos.x), int(self.pos.y))
        shadow_surf = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0,0,0,120), (CELL_SIZE*2, CELL_SIZE*2), CELL_SIZE)
        surface.blit(shadow_surf, (head_pos[0]-CELL_SIZE*2+shadow_offset, head_pos[1]-CELL_SIZE*2+shadow_offset))

        # Gambar badan snake (gradient)
        if len(self.body) > 1:
            for idx, cell in enumerate(self.body[1:]):
                center = (cell[0]*CELL_SIZE+CELL_SIZE//2, cell[1]*CELL_SIZE+CELL_SIZE//2)
                factor = idx/(len(self.body)-1)
                cell_color = blend_color(self.color, (255,255,255), factor)
                s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                s.set_alpha(alpha)
                pygame.draw.circle(s, cell_color, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2)
                surface.blit(s, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE))
        # Glow di kepala
        glow_surf = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, self.color+(100,), (CELL_SIZE*2, CELL_SIZE*2), CELL_SIZE)
        surface.blit(glow_surf, (head_pos[0]-CELL_SIZE*2, head_pos[1]-CELL_SIZE*2))
        # Gambar kepala
        s_head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s_head.set_alpha(alpha)
        pygame.draw.circle(s_head, self.color, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2)
        surface.blit(s_head, (head_pos[0]-CELL_SIZE//2, head_pos[1]-CELL_SIZE//2))
        # Jika shield aktif, gambar border kuning
        if self.shield_timer > 0:
            pygame.draw.circle(surface, YELLOW, head_pos, CELL_SIZE//2+3, 2)
        # Jika freeze aktif, overlay es
        if self.freeze_timer > 0:
            freeze_overlay = pygame.Surface((CELL_SIZE*2, CELL_SIZE*2), pygame.SRCALPHA)
            freeze_overlay.fill((150,220,255,100))
            surface.blit(freeze_overlay, (head_pos[0]-CELL_SIZE, head_pos[1]-CELL_SIZE))
        # Jika fire aktif, overlay api
        if self.fire_timer > 0:
            fire_overlay = pygame.Surface((CELL_SIZE*2, CELL_SIZE*2), pygame.SRCALPHA)
            fire_overlay.fill((255,100,0,100))
            surface.blit(fire_overlay, (head_pos[0]-CELL_SIZE, head_pos[1]-CELL_SIZE))

    def collision_with_self(self):
        head = self.body[0]
        return head in self.body[1:]

# ----- Fungsi Spawn -----
def spawn_food(snakes, obstacles, powerups):
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        collision = False
        for snake in snakes:
            if pos in snake.body:
                collision = True
                break
        if pos in obstacles:
            collision = True
        if any(p["pos"] == pos for p in powerups):
            collision = True
        if not collision:
            return pos

def spawn_powerup(snakes, obstacles, food, powerups):
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        collision = False
        for snake in snakes:
            if pos in snake.body:
                collision = True
                break
        if pos == food:
            collision = True
        if any(p["pos"] == pos for p in powerups):
            collision = True
        if pos in obstacles:
            collision = True
        if not collision:
            types = ["speed", "slow", "shield", "invisible", "growth", "freeze", "fire"]
            selected_type = random.choice(types)
            return {"pos": pos, "type": selected_type}

def is_collision(cell, snakes, obstacles):
    x, y = cell
    if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
        return True
    for snake in snakes:
        if cell in snake.body:
            return True
    if cell in obstacles:
        return True
    return False

def get_safe_directions(snake, snakes, obstacles):
    directions = [(0,-1), (0,1), (-1,0), (1,0)]
    safe_moves = []
    head = snake.get_grid_position()
    # Jika snake sedang invisibility, abaikan obstacle dan snake lawan
    if snake.invisible_timer > 0:
        for d in directions:
            new_cell = (head[0]+d[0], head[1]+d[1])
            # Pastikan tidak keluar frame dan tidak menabrak tubuh sendiri
            if 0 <= new_cell[0] < GRID_WIDTH and 0 <= new_cell[1] < GRID_HEIGHT:
                if new_cell not in snake.body[1:]:
                    safe_moves.append(d)
        return safe_moves

    # Jika tidak invisibility, perhitungan seperti semula:
    for d in directions:
        new_cell = (head[0]+d[0], head[1]+d[1])
        if (0 <= new_cell[0] < GRID_WIDTH and 0 <= new_cell[1] < GRID_HEIGHT and
            new_cell not in snake.body[1:] and
            not is_collision(new_cell, [s for s in snakes if s != snake], obstacles)):
            safe_moves.append(d)
    return safe_moves

def detect_potential_collisions(snake, snakes, obstacles):
    head = snake.get_grid_position()
    directions = [(0,-1), (0,1), (-1,0), (1,0)]
    potential = []
    for d in directions:
        new_cell = (head[0]+d[0], head[1]+d[1])
        if any(is_collision(new_cell, [s], obstacles) for s in snakes if s != snake):
            potential.append(d)
    return potential

# ----- Mode AI & Pemilihan Arah -----
def update_ai_mode(snake, food, snakes, obstacles, powerups):
    # Jika fire aktif, tetapkan mode aggressive
    if snake.fire_timer > 0:
        snake.mode = "aggressive"
        return
    # Jika invisible aktif, tetapkan mode "invisible"
    if snake.invisible_timer > 0:
        snake.mode = "invisible"
        return

    opponent = [s for s in snakes if s is not snake][0]
    head = snake.get_grid_position()
    opp_head = opponent.get_grid_position()
    safe_moves = get_safe_directions(snake, snakes, obstacles)
    if not safe_moves:
        snake.mode = "defensive"
        return
    if manhattan(head, opp_head) < 5 and len(snake.body) > len(opponent.body):
        snake.mode = "aggressive"
        return
    if powerups:
        # Jika ada growth power up, prioritaskan
        growth_pus = [pu for pu in powerups if pu["type"] == "growth"]
        if growth_pus:
            nearest_growth = min(growth_pus, key=lambda pu: manhattan(head, pu["pos"]))
            if manhattan(head, nearest_growth["pos"]) < 5:
                snake.mode = "opportunistic"
                return
        nearest_pu = min(powerups, key=lambda pu: manhattan(head, pu["pos"]))
        if manhattan(head, nearest_pu["pos"]) < 5:
            snake.mode = "opportunistic"
            return
    if manhattan(head, food) > 10:
        snake.mode = "explorative"
        return
    if len(snake.body) >= 10:
        snake.mode = "conservative"
        return
    if (opp_head[0] < 3 or opp_head[0] > GRID_WIDTH-4 or
        opp_head[1] < 3 or opp_head[1] > GRID_HEIGHT-4) and manhattan(head, opp_head) < 4:
        snake.mode = "trapping"
        return
    snake.mode = "defensive"

def ai_choose_direction(snake, food, snakes, obstacles, powerups):
    head = snake.get_grid_position()
    # Jika snake sedang invisible, gunakan algoritma sederhana:
    if snake.invisible_timer > 0:
        safe_moves = get_safe_directions(snake, snakes, obstacles)
        if not safe_moves:
            return snake.desired_direction
        best_move = safe_moves[0]
        best_score = float('inf')
        for move in safe_moves:
            new_cell = (head[0]+move[0], head[1]+move[1])
            # Hanya perhitungkan jarak ke makanan
            score = manhattan(new_cell, food)
            if score < best_score:
                best_score = score
                best_move = move
        return pygame.math.Vector2(best_move).normalize()

    # Untuk kondisi normal, update mode AI
    update_ai_mode(snake, food, snakes, obstacles, powerups)
    safe_moves = get_safe_directions(snake, snakes, obstacles)
    if not safe_moves:
        return snake.desired_direction
    opponent = [s for s in snakes if s is not snake][0]
    opponent_head = opponent.get_grid_position()
    predicted_positions = predict_future_positions(opponent, steps=3)
    dist_to_opponent = manhattan(head, opponent_head)
    if dist_to_opponent < 5:
        if snake.score < opponent.score:
            snake.mode = "aggressive"
        else:
            snake.mode = "defensive"
    if random.random() > snake.intelligence:
        return pygame.math.Vector2(random.choice(safe_moves)).normalize()
    potential = detect_potential_collisions(snake, snakes, obstacles)
    safe_moves = [m for m in safe_moves if m not in potential]
    if not safe_moves:
        safe_moves = get_safe_directions(snake, snakes, obstacles)
    best_move = safe_moves[0]
    best_score = float('inf')
    for move in safe_moves:
        new_cell = (head[0]+move[0], head[1]+move[1])
        food_dist = manhattan(new_cell, food)
        food_priority = food_dist * 2.5
        opp_head_dist = manhattan(new_cell, opponent_head)
        opp_factor = 5/(opp_head_dist+1)
        score = food_priority + opp_factor
        if new_cell == opponent_head:
            score += 50
        if opp_head_dist < 2:
            if len(opponent.body) > 1:
                min_body = min(manhattan(new_cell, cell) for cell in opponent.body[1:])
            else:
                min_body = 100
            if min_body >= 2:
                score += 10
            trap_bonus = 0
            if len(opponent.body) > 1:
                min_body = min(manhattan(new_cell, cell) for cell in opponent.body[1:])
                if opp_head_dist <= 3:
                    trap_bonus = 4 if min_body < 2 else 2*snake.experience/(min_body+1)
            score -= trap_bonus
        # Bonus atau penalti untuk power-up
        for pu in powerups:
            pu_dist = manhattan(new_cell, pu["pos"])
            if pu["type"] == "slow":
                score += 5/(pu_dist+1) if snake.mode=="defensive" else -5/(pu_dist+1)
            elif pu["type"] == "shield":
                score += -5/(pu_dist+1) if snake.mode=="aggressive" else 5/(pu_dist+1)
            elif pu["type"] == "invisible":
                score += 5/(pu_dist+1) if snake.mode=="defensive" else -5/(pu_dist+1)
            elif pu["type"] == "growth":
                # Prioritaskan growth power up lebih tinggi (plant)
                score -= 7/(pu_dist+1)
            elif pu["type"] == "freeze":
                if snake.mode=="aggressive":
                    score -= 8/(pu_dist+1)
                elif snake.mode=="opportunistic":
                    score -= 6/(pu_dist+1)
                elif snake.mode=="defensive":
                    score += 5/(pu_dist+1)
            elif pu["type"] == "fire":
                # Untuk fire, tidak perlu tambahan score di AI karena mode sudah aggressive
                score -= 7/(pu_dist+1)
        for pos in predicted_positions:
            dist_pred = manhattan(new_cell, pos)
            if snake.mode=="defensive":
                score += 5/(dist_pred+1)
            elif snake.mode=="aggressive":
                score -= 3/(dist_pred+1)
            if snake.mode=="aggressive":
                score -= 5/(opp_head_dist+1)
            elif snake.mode=="defensive":
                score += 5/(opp_head_dist+1)
            elif snake.mode=="explorative":
                free_space = count_free_space(new_cell, snakes, obstacles, depth=3)
                score -= free_space * 0.5
            elif snake.mode=="conservative":
                center = (GRID_WIDTH//2, GRID_HEIGHT//2)
                score -= manhattan(new_cell, center)*0.3
            elif snake.mode=="opportunistic":
                if powerups:
                    nearest_pu = min(powerups, key=lambda pu: manhattan(new_cell, pu["pos"]))
                    score -= 5/(manhattan(new_cell, nearest_pu["pos"])+1)
            elif snake.mode=="trapping":
                if len(opponent.body)>1:
                    min_body = min(manhattan(new_cell, cell) for cell in opponent.body[1:])
                    score -= 5/(min_body+1)
        if score < best_score:
            best_score = score
            best_move = move
    return pygame.math.Vector2(best_move).normalize()

def draw_scores(surface, snakes, elapsed_time):
    s1 = font.render(f"{snakes[0].name}: {snakes[0].score}", True, WHITE)
    s2 = font.render(f"{snakes[1].name}: {snakes[1].score}", True, WHITE)
    timer = font.render(f"Time: {elapsed_time}s", True, WHITE)
    surface.blit(s1, (10,10))
    surface.blit(s2, (WINDOW_WIDTH - s2.get_width() - 10, 10))
    surface.blit(timer, ((WINDOW_WIDTH - timer.get_width())//2, 10))

def spawn_obstacles(snakes, food, powerups, count=20):
    obstacles = set()
    safe_zone = set()
    safe_radius = 3
    for snake in snakes:
        start = snake.body[0]
        for dx in range(-safe_radius, safe_radius+1):
            for dy in range(-safe_radius, safe_radius+1):
                cell = (start[0]+dx, start[1]+dy)
                if 0<=cell[0]<GRID_WIDTH and 0<=cell[1]<GRID_HEIGHT:
                    safe_zone.add(cell)
    for dx in range(-1,2):
        for dy in range(-1,2):
            cell = (food[0]+dx, food[1]+dy)
            if 0<=cell[0]<GRID_WIDTH and 0<=cell[1]<GRID_HEIGHT:
                safe_zone.add(cell)
    for pu in powerups:
        for dx in range(-1,2):
            for dy in range(-1,2):
                cell = (pu["pos"][0]+dx, pu["pos"][1]+dy)
                if 0<=cell[0]<GRID_WIDTH and 0<=cell[1]<GRID_HEIGHT:
                    safe_zone.add(cell)
    num_clusters = max(1, count//5)
    for _ in range(num_clusters):
        attempts = 0
        while attempts < 100:
            cx = random.randint(0, GRID_WIDTH-1)
            cy = random.randint(0, GRID_HEIGHT-1)
            if (cx,cy) not in safe_zone and (cx,cy) not in obstacles:
                break
            attempts += 1
        else:
            continue
        cluster_size = random.randint(3,7)
        cluster_cells = {(cx,cy)}
        frontier = [(cx,cy)]
        while frontier and len(cluster_cells) < cluster_size:
            cell = random.choice(frontier)
            neighbors = [(cell[0]+1, cell[1]), (cell[0]-1, cell[1]),
                         (cell[0], cell[1]+1), (cell[0], cell[1]-1)]
            random.shuffle(neighbors)
            found = False
            for n in neighbors:
                if (0<=n[0]<GRID_WIDTH and 0<=n[1]<GRID_HEIGHT and
                    n not in safe_zone and n not in obstacles and n not in cluster_cells):
                    cluster_cells.add(n)
                    frontier.append(n)
                    found = True
                    break
            if not found:
                frontier.remove(cell)
        obstacles.update(cluster_cells)
    while len(obstacles) < count:
        cell = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if cell not in safe_zone and cell not in obstacles:
            obstacles.add(cell)
    return list(obstacles)

def draw_food(surface, food):
    center = (food[0]*CELL_SIZE+CELL_SIZE//2, food[1]*CELL_SIZE+CELL_SIZE//2)
    max_radius = CELL_SIZE//2
    for r in range(max_radius, 0, -1):
        factor = r/max_radius
        color = ( int(YELLOW[0]*(1-factor)+RED[0]*factor),
                  int(YELLOW[1]*(1-factor)+RED[1]*factor),
                  int(YELLOW[2]*(1-factor)+RED[2]*factor) )
        pygame.draw.circle(surface, color, center, r)

def draw_obstacles(surface, obstacles):
    for pos in obstacles:
        rect = cell_rect(pos)
        obs_surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        base_color = GRAY
        obs_surf.fill(base_color)
        pattern_color = (70,70,70)
        for i in range(-CELL_SIZE, CELL_SIZE, 4):
            start_pos = (i,0) if i>=0 else (0,-i)
            end_pos = (CELL_SIZE, CELL_SIZE-i) if i>=0 else (CELL_SIZE+i, CELL_SIZE)
            pygame.draw.line(obs_surf, pattern_color, start_pos, end_pos, 1)
        pygame.draw.rect(obs_surf, (50,50,50), obs_surf.get_rect(), 1)
        surface.blit(obs_surf, rect.topleft)

def draw_powerups(surface, powerups):
    emoji_map = {
        "speed": "🚀",
        "slow": "🐢",
        "shield": "🛡️",
        "invisible": "👻",
        "growth": "🌱",
        "freeze": "❄️",
        "fire": "🔥"
    }
    for pu in powerups:
        pos = pu["pos"]
        center = (pos[0]*CELL_SIZE+CELL_SIZE//2, pos[1]*CELL_SIZE+CELL_SIZE//2)
        emoji = emoji_map.get(pu["type"], "?")
        txt = emoji_font.render(emoji, True, WHITE)
        rect = txt.get_rect(center=center)
        surface.blit(txt, rect.topleft)

def draw_background(surface):
    for y in range(WINDOW_HEIGHT):
        ratio = y/ WINDOW_HEIGHT
        r = int(DARK_BLUE[0]*(1-ratio)+BLACK[0]*ratio)
        g = int(DARK_BLUE[1]*(1-ratio)+BLACK[1]*ratio)
        b = int(DARK_BLUE[2]*(1-ratio)+BLACK[2]*ratio)
        pygame.draw.line(surface, (r,g,b), (0,y), (WINDOW_WIDTH,y))

def draw_text_center(surface, text, font, color, y):
    txt = font.render(text, True, color)
    x = (WINDOW_WIDTH - txt.get_width())//2
    surface.blit(txt, (x,y))

def main_menu():
    menu = True
    while menu:
        draw_background(screen)
        draw_text_center(screen, "SNAKE AI vs AI", large_font, GREEN, WINDOW_HEIGHT//4)
        draw_text_center(screen, "1. Start Game", font, WHITE, WINDOW_HEIGHT//2)
        draw_text_center(screen, "2. Information", font, WHITE, WINDOW_HEIGHT//2+40)
        draw_text_center(screen, "3. Quit", font, WHITE, WINDOW_HEIGHT//2+80)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    menu = False
                elif event.key == pygame.K_2:
                    info_screen()
                elif event.key == pygame.K_3:
                    pygame.quit(); sys.exit()
        clock.tick(15)

def info_screen():
    info = True
    scroll_offset = 0
    info_lines = [
        "Game Snake AI vs AI - Learning, Trapping & Mode",
        "Dua ular AI berkompetisi untuk makan, trap,",
        "dan menghindari serangan lawan.",
        "",
        "Fitur Visual Baru:",
        "- Partikel animasi saat makanan dimakan.",
        "- Efek glow di kepala dan bayangan 3D.",
        "- Transisi warna gradient di badan ular.",
        "- Latar belakang gradient dinamis.",
        "",
        "Fitur Mode AI:",
        "- Agresif: Menyerang lawan jika aman dan lawan lebih pendek.",
        "- Defensif: Menghindari bahaya bila ruang gerak terbatas.",
        "- Eksploratif: Menjelajah area baru bila makanan jauh.",
        "- Konservatif: Menjaga ruang gerak bila tubuh sudah panjang.",
        "- Oportunistik: Memanfaatkan power-up dan peluang.",
        "- Penjepit: Menjebak lawan di area sempit.",
        "",
        "Power-Up (ditampilkan dengan emoji):",
        "🚀 Speed Boost: Naikkan kecepatan sementara.",
        "🐢 Slow Trap: Perlambat kecepatan (efek negatif).",
        "🛡️ Shield: Melindungi dari tabrakan (satu kali pakai).",
        "👻 Invisibility: Abaikan obstacle & snake lawan (kecuali border).",
        "🌱 Growth Boost: +3 score & +3 panjang, prioritas lebih tinggi dari makanan.",
        "❄️ Freeze: Bekukan lawan selama beberapa detik.",
        "🔥 Fire: +10 score & +10 panjang (bonus fire akan dikurangi 10 saat selesai), mode aggressive.",
        "",
        "Controls:",
        "  1: Start Game",
        "  2: Information",
        "  3: Quit",
        "",
        "Gunakan panah atas/bawah atau scroll mouse untuk info lebih lanjut.",
        "Press ESC to return to Main Menu."
    ]
    line_spacing = 30
    title_y = 50
    text_start_y = 150
    total_text = len(info_lines)*line_spacing
    while info:
        draw_background(screen)
        draw_text_center(screen, "Information", large_font, YELLOW, title_y)
        y = text_start_y + scroll_offset
        for line in info_lines:
            txt = font.render(line, True, WHITE)
            x = (WINDOW_WIDTH - txt.get_width())//2
            screen.blit(txt, (x,y))
            y += line_spacing
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y*10
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    scroll_offset -= 10
                elif event.key == pygame.K_UP:
                    scroll_offset += 10
                elif event.key == pygame.K_ESCAPE:
                    info = False
        if total_text + text_start_y + scroll_offset < WINDOW_HEIGHT:
            scroll_offset = WINDOW_HEIGHT - total_text - text_start_y
        if scroll_offset > 0:
            scroll_offset = 0
        clock.tick(15)

def game_over_screen(snakes, elapsed_time, outcome):
    over = True
    result = "Game Over!" if outcome is None else outcome
    while over:
        draw_background(screen)
        draw_text_center(screen, "GAME OVER", large_font, RED, WINDOW_HEIGHT//4)
        score_text = f"{snakes[0].name}: {snakes[0].score}   |   {snakes[1].name}: {snakes[1].score}"
        draw_text_center(screen, score_text, font, WHITE, WINDOW_HEIGHT//2-20)
        draw_text_center(screen, f"Time: {elapsed_time}s", font, WHITE, WINDOW_HEIGHT//2+10)
        draw_text_center(screen, result, font, YELLOW, WINDOW_HEIGHT//2+40)
        draw_text_center(screen, "1. Restart   2. Main Menu   3. Quit", font, WHITE, WINDOW_HEIGHT//2+80)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    over = False; return "restart"
                elif event.key == pygame.K_2:
                    over = False; return "menu"
                elif event.key == pygame.K_3:
                    pygame.quit(); sys.exit()
        clock.tick(15)

# ----- GAME LOOP -----
def game_loop():
    snake1 = Snake("Sang Hijau", GREEN, (5,5), (1,0), intelligence=1.0)
    snake2 = Snake("Sang Biru", BLUE, (GRID_WIDTH-6, GRID_HEIGHT-6), (-1,0), intelligence=0.8)
    snakes = [snake1, snake2]
    powerups = []
    food = spawn_food(snakes, [], powerups)
    obstacles = spawn_obstacles(snakes, food, powerups, count=20)
    powerup_spawn_timer = 0
    game_over = False
    outcome = None
    start_ticks = pygame.time.get_ticks()
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        elapsed_time = (pygame.time.get_ticks()-start_ticks)//1000
        if powerup_spawn_timer <= 0:
            powerups.append(spawn_powerup(snakes, obstacles, food, powerups))
            powerup_spawn_timer = FPS * 10
        else:
            powerup_spawn_timer -= 1

        # Update AI
        for snake in snakes:
            new_dir = ai_choose_direction(snake, food, snakes, obstacles, powerups)
            snake.change_desired_direction(new_dir)
        # Update fisika snake
        for snake in snakes:
            snake.update_physics(snakes, obstacles)
        
        # --- Cek Tabrakan Objek (dinding, self, obstacle) ---
        for snake in snakes:
            head = snake.get_grid_position()
            head_center = (head[0]*CELL_SIZE+CELL_SIZE/2, head[1]*CELL_SIZE+CELL_SIZE/2)
            # Tabrakan dengan dinding (selalu berlaku)
            if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
                if snake.shield_timer > 0:
                    snake.shield_timer = 0
                    for _ in range(20):
                        particles.append(Particle(head_center, YELLOW))
                else:
                    game_over = True
                    outcome = f"{snake.name} menabrak dinding."
            # Jika snake tidak invisibility, cek self collision dan obstacle
            if snake.invisible_timer <= 0:
                if snake.collision_with_self():
                    if snake.shield_timer > 0:
                        snake.shield_timer = 0
                        for _ in range(20):
                            particles.append(Particle(head_center, YELLOW))
                    else:
                        game_over = True
                        outcome = f"{snake.name} menabrak dirinya sendiri."
                if head in obstacles:
                    if snake.shield_timer > 0:
                        snake.shield_timer = 0
                        for _ in range(20):
                            particles.append(Particle(head_center, YELLOW))
                    else:
                        game_over = True
                        outcome = f"{snake.name} menabrak obstacle."
        if game_over:
            break

        # --- Cek Tabrakan antar Snake ---
        # Jika salah satu snake dalam invisible mode, abaikan collision antar snake
        if not (snake1.invisible_timer > 0 or snake2.invisible_timer > 0):
            s1_head = snake1.get_grid_position()
            s2_head = snake2.get_grid_position()
            s1_center = (s1_head[0]*CELL_SIZE+CELL_SIZE/2, s1_head[1]*CELL_SIZE+CELL_SIZE/2)
            s2_center = (s2_head[0]*CELL_SIZE+CELL_SIZE/2, s2_head[1]*CELL_SIZE+CELL_SIZE//2)
            # Head-to-head collision
            if s1_head == s2_head:
                if snake1.shield_timer > 0 and snake2.shield_timer <= 0:
                    snake1.shield_timer = 0
                    for _ in range(20):
                        particles.append(Particle(s1_center, YELLOW))
                    game_over = True
                    outcome = f"{snake2.name} menabrak shield {snake1.name}, {snake2.name} menang."
                elif snake2.shield_timer > 0 and snake1.shield_timer <= 0:
                    snake2.shield_timer = 0
                    for _ in range(20):
                        particles.append(Particle(s2_center, YELLOW))
                    game_over = True
                    outcome = f"{snake1.name} menabrak shield {snake2.name}, {snake1.name} menang."
                elif snake1.shield_timer > 0 and snake2.shield_timer > 0:
                    snake1.shield_timer = 0
                    snake2.shield_timer = 0
                    for _ in range(20):
                        particles.append(Particle(s1_center, YELLOW))
                        particles.append(Particle(s2_center, YELLOW))
                    game_over = True
                    outcome = "Seri! Kedua kepala bertabrakan dengan shield."
                else:
                    game_over = True
                    outcome = "Seri! Kedua kepala bertabrakan."
            elif s1_head in snake2.body[1:]:
                if snake2.shield_timer > 0:
                    snake2.shield_timer = 0
                    for _ in range(20):
                        particles.append(Particle(s2_center, YELLOW))
                game_over = True
                outcome = f"{snake1.name} menabrak {snake2.name} dan kalah."
            elif s2_head in snake1.body[1:]:
                if snake1.shield_timer > 0:
                    snake1.shield_timer = 0
                    for _ in range(20):
                        particles.append(Particle(s1_center, YELLOW))
                game_over = True
                outcome = f"{snake2.name} menabrak {snake1.name} dan kalah."

        if game_over:
            break

        # Cek makan makanan
        for snake in snakes:
            if snake.get_grid_position() == food:
                snake.grow = True
                snake.score += 1
                food_center = (food[0]*CELL_SIZE+CELL_SIZE/2, food[1]*CELL_SIZE+CELL_SIZE/2)
                for _ in range(15):
                    particles.append(Particle(food_center, RED))
                if len(particles) > MAX_PARTICLES:
                    particles[:] = particles[-MAX_PARTICLES:]
                food = spawn_food(snakes, obstacles, powerups)
        # Cek powerup
        for snake in snakes:
            for pu in powerups[:]:
                if snake.get_grid_position() == pu["pos"]:
                    if pu["type"] == "speed":
                        snake.speed_boost_timer = FPS * 10
                    elif pu["type"] == "slow":
                        snake.slow_timer = FPS * 10
                    elif pu["type"] == "shield":
                        snake.shield_timer = FPS * 10
                    elif pu["type"] == "invisible":
                        snake.invisible_timer = FPS * 10
                    elif pu["type"] == "growth":
                        snake.score += 3
                        for _ in range(3):
                            snake.body.append(snake.body[-1])
                    elif pu["type"] == "freeze":
                        opponent = [s for s in snakes if s is not snake][0]
                        opponent.freeze_timer = FPS * 5
                        opp_head = opponent.get_grid_position()
                        opp_center = (opp_head[0]*CELL_SIZE+CELL_SIZE/2, opp_head[1]*CELL_SIZE+CELL_SIZE/2)
                        for _ in range(10):
                            freeze_particles.append(FreezeParticle(opp_center))
                    elif pu["type"] == "fire":
                        snake.fire_timer = FPS * 10
                        snake.fire_bonus_active = True
                        snake.score += 10   # Bonus score
                        for _ in range(10):
                            snake.body.append(snake.body[-1])
                        head = snake.get_grid_position()
                        center = (head[0]*CELL_SIZE+CELL_SIZE/2, head[1]*CELL_SIZE+CELL_SIZE/2)
                        for _ in range(10):
                            fire_particles.append(FireParticle(center))
                    powerups.remove(pu)
                    break

        # Update partikel
        for p in particles[:]:
            p.update()
            if p.lifetime <= 0:
                particles.remove(p)
        for fp in freeze_particles[:]:
            fp.update()
            if fp.lifetime <= 0:
                freeze_particles.remove(fp)
        for fp in fire_particles[:]:
            fp.update()
            if fp.lifetime <= 0:
                fire_particles.remove(fp)
        for ip in invis_particles[:]:
            ip.update()
            if ip.lifetime <= 0:
                invis_particles.remove(ip)
        # Tambahkan partikel untuk snake yang sedang invisibility
        for snake in snakes:
            if snake.invisible_timer > 0:
                head = snake.get_grid_position()
                center = (head[0]*CELL_SIZE+CELL_SIZE//2, head[1]*CELL_SIZE+CELL_SIZE//2)
                if random.random() < 0.3:
                    invis_particles.append(InvisibilityParticle(center))

        # Gambar ulang layar
        draw_background(screen)
        # Gambar grid opsional
        for x in range(GRID_WIDTH):
            pygame.draw.line(screen, (20,20,20), (x*CELL_SIZE, 0), (x*CELL_SIZE, WINDOW_HEIGHT))
        for y in range(GRID_HEIGHT):
            pygame.draw.line(screen, (20,20,20), (0, y*CELL_SIZE), (WINDOW_WIDTH, y*CELL_SIZE))
        draw_food(screen, food)
        draw_obstacles(screen, obstacles)
        draw_powerups(screen, powerups)
        for snake in snakes:
            snake.draw(screen)
        for p in particles:
            p.draw(screen)
        for fp in freeze_particles:
            fp.draw(screen)
        for fp in fire_particles:
            fp.draw(screen)
        for ip in invis_particles:
            ip.draw(screen)
        draw_scores(screen, snakes, elapsed_time)
        if DEBUG_MODE:
            dbg_lines = []
            for s in snakes:
                dbg_lines.append(f"{s.name}: {s.mode}")
            for i, line in enumerate(dbg_lines):
                txt = font.render(line, True, YELLOW)
                screen.blit(txt, (10, 30+i*20))
        pygame.display.update()
        clock.tick(FPS)
    return snakes, elapsed_time, outcome

def main():
    while True:
        main_menu()
        snakes, elapsed_time, outcome = game_loop()
        choice = game_over_screen(snakes, elapsed_time, outcome)
        if choice == "menu":
            continue
        elif choice == "restart":
            continue

if __name__ == "__main__":
    main()

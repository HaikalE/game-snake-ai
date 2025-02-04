# game-snake-ai

![image](https://github.com/user-attachments/assets/cf1c233f-5921-4bad-adbd-cd3b40dc4324)

---

### 1. Particle Effects

**Alpha (Opacity) Calculation for Particles:**

```
alpha = min( max(lifetime * 6, 0), 255 )
```

- `lifetime`: Remaining life of the particle.
- The formula scales the lifetime by 6, ensuring it never falls below 0 and never exceeds 255 (the maximum opacity).

### 2. Snake Physics and Movement

The snake’s movement is based on simple physics calculations involving vectors for position, velocity, and acceleration.

**a. Desired Velocity:**

```
desired_velocity = desired_direction * effective_max_speed
```

- `desired_direction`: The unit vector indicating the snake's intended movement.
- `effective_max_speed`: Calculated as follows.

**b. Effective Maximum Speed:**

```
effective_max_speed = base_max_speed * boost_multiplier * (0.5 + 0.5 * danger_factor)
```

- `base_max_speed`: The initial maximum speed set for the snake.
- `boost_multiplier`: Modifier based on power-ups (e.g., speed boost gives 1.5, slow trap gives 0.5).
- `danger_factor`: A value between 0 and 1 indicating how safe the path is (closer danger reduces speed).

**c. Force and Acceleration:**

```
force = desired_velocity - current_velocity
```

- The force is capped by a maximum value:
  
  ```
  max_force = max_acceleration * mass
  ```

- If the computed `force` is larger than `max_force`, it is scaled down.
- Then, acceleration is calculated as:

  ```
  acceleration = force / mass
  ```

**d. Friction Application:**

```
friction = - friction_coeff * current_velocity
```

- `friction_coeff`: A small constant (e.g., 0.05) that simulates resistance.

**e. Net Acceleration and Update:**

```
net_acceleration = acceleration + friction
current_velocity += net_acceleration
```

- If `current_velocity` exceeds `effective_max_speed`, it is scaled back.
- Finally, update the position:

```
position += current_velocity
```

### 3. AI Decision Making

The AI evaluates possible moves (up, down, left, right) by scoring each move based on several factors:

**a. Distance to Food:**

```
food_priority = Manhattan_distance(new_cell, food) * 2.5
```

- The Manhattan distance is simply the sum of the absolute differences of the x and y coordinates.
- Multiplying by 2.5 gives a weight to the importance of moving toward food.

**b. Distance to Opponent:**

```
opp_factor = 5 / (Manhattan_distance(new_cell, opponent_head) + 1)
```

- A lower Manhattan distance to the opponent increases the factor.
- This factor is adjusted based on whether the snake is in an aggressive or defensive mode.

**c. Combining the Scores:**

For each possible move, the AI computes a score that may look like:

```
score = food_priority + opp_factor + (additional mode-specific adjustments)
```

- Additional adjustments can include penalties for moves that could lead to collisions, bonuses for power-up proximity, and considerations for predicted opponent positions.

**d. Selecting the Best Move:**

- The AI evaluates all safe moves (moves that do not lead to collisions) and selects the move with the lowest score.
- In cases where the snake's "intelligence" threshold is not met, it might choose a random safe move.

### 4. Collision and Game Mechanics

**Collision Checks:**

- **Wall Collision:** If the snake's head moves outside the grid boundaries.
- **Self-Collision:** If the snake's head intersects with any part of its own body.
- **Obstacle Collision:** If the snake's head coincides with any obstacle cell.
- **Snake-to-Snake Collision:** Both head-to-head and head-to-body collisions are checked.

For example, a simple wall collision check can be expressed as:

```
if head_x < 0 or head_x >= grid_width or head_y < 0 or head_y >= grid_height:
    collision_detected = True
```

**Power-Up Effects:**

When a snake collects a power-up, the effect is applied immediately:
- **Speed Boost / Slow:** Adjust the `boost_multiplier` used in the speed calculation.
- **Shield:** Provides temporary immunity.
- **Invisibility:** Alters collision logic.
- **Growth:** Increases the snake's length and score.
- **Freeze/Fire:** Applies specific effects (e.g., freezing the opponent or triggering aggressive mode).

---

# game-snake-ai

---

## Overview

This project implements a competitive snake game where two AI-controlled snakes use physics-based motion and decision-making algorithms to navigate a grid, collect food, and utilize various power-ups. The code is structured into several key components:

- **Physics and Particle Effects:** Governing the movement of snakes and visual effects (like particles for food, fire, or freeze).
- **Snake Dynamics:** Calculating acceleration, velocity, and position using physics formulas.
- **AI Decision Making:** Choosing safe and optimal directions based on Manhattan distance calculations and heuristics.
- **Collision and Power-Up Handling:** Detecting collisions with walls, obstacles, and other snakes and applying effects from power-ups.

Each of these components works together in the main game loop to simulate a dynamic environment.

---

## 1. Particle System

### Particle Classes

There are several particle classes defined to create various visual effects:
- **Particle:** A general particle used for effects such as when food is eaten.
- **FreezeParticle, FireParticle, InvisibilityParticle:** Each of these provides a specialized effect (e.g., a blueish color for freeze or orange for fire).

### Particle Update and Draw Mechanics

For each particle:
- **Update Step:**  
  - The particle’s position is updated by adding a random velocity vector.
  - Its lifetime is decremented.
  - The particle’s size gradually decreases (e.g., `self.size -= 0.1`).
- **Drawing:**  
  - A temporary surface is created with an alpha channel.
  - A circle is drawn on this surface using a color that blends with transparency based on the remaining lifetime.
  - This surface is then blitted onto the main screen.

*Example Formula (for blending transparency):*

\[
\text{alpha} = \min(\max(\text{lifetime} \times 6, 0), 255)
\]

This formula adjusts the opacity of a particle based on its remaining lifetime.

---

## 2. Snake Physics

Each snake’s movement is calculated with basic physics principles, using vectors for position and velocity.

### Position and Velocity Update

1. **Desired Velocity Calculation:**  
   The snake calculates its desired velocity as:
   \[
   \text{desired\_velocity} = \text{desired\_direction} \times \text{effective\_max\_speed}
   \]
   Here, the **effective maximum speed** is determined by several factors:
   - **Base speed** (set during snake initialization)
   - **Boost or Slow Multipliers:** For example, if a speed boost is active, the snake’s maximum speed is multiplied by 1.5; if slowed, it is reduced by half.
   - **Danger Factor:** This factor is computed based on the distance to obstacles or walls. The further away the danger, the closer the factor is to 1.0, but if danger is near, the speed is effectively reduced.

   The code calculates effective maximum speed as:
   \[
   \text{effective\_max\_speed} = \text{base\_max\_speed} \times \text{boost\_multiplier} \times \left(0.5 + 0.5 \times \text{danger\_factor}\right)
   \]

2. **Force and Acceleration:**  
   The force acting on the snake is the difference between the desired velocity and the current velocity:
   \[
   \text{force} = \text{desired\_velocity} - \text{velocity}
   \]
   This force is capped by a maximum value calculated as:
   \[
   \text{max\_force} = \text{max\_acceleration} \times \text{mass}
   \]
   If the computed force exceeds this cap, it is scaled down. Then, the acceleration is given by:
   \[
   \text{acceleration} = \frac{\text{force}}{\text{mass}}
   \]

3. **Friction Application:**  
   A friction term is applied to simulate resistance:
   \[
   \text{friction} = -\text{friction\_coeff} \times \text{velocity}
   \]
   Where `friction_coeff` is a small constant (e.g., 0.05). The net acceleration is then:
   \[
   \text{net\_acceleration} = \text{acceleration} + \text{friction}
   \]

4. **Updating Velocity and Position:**  
   The snake’s velocity is updated by adding the net acceleration:
   \[
   \text{velocity} \mathrel{+}= \text{net\_acceleration}
   \]
   If the velocity exceeds the effective maximum speed, it is scaled back. Finally, the position is updated:
   \[
   \text{position} \mathrel{+}= \text{velocity}
   \]

This step-by-step update provides a smooth, physics-based movement for each snake.

---

## 3. AI Decision Making

The AI for each snake is responsible for selecting the next movement direction. The decision-making process includes:

### Safe Direction Calculation

- **Grid and Collision Checks:**  
  The function `get_safe_directions` determines which of the four possible directions (up, down, left, right) are safe. Safety is defined by:
  - Not colliding with the snake’s own body.
  - Not colliding with obstacles or the other snake (unless the snake is in invisibility mode).

### Scoring Function for Direction Choice

The AI evaluates each possible move using a scoring function that considers:
- **Distance to Food:**  
  The Manhattan distance from the potential new head position to the food. A lower distance (multiplied by a factor) is preferred.
  
  \[
  \text{food\_priority} = \text{Manhattan distance to food} \times 2.5
  \]

- **Distance to Opponent:**  
  The distance from the new cell to the opponent’s head, with adjustments based on the current mode (aggressive, defensive, etc.).  
  For example:
  \[
  \text{opp\_factor} = \frac{5}{(\text{Manhattan distance to opponent head} + 1)}
  \]

- **Collision Predictions:**  
  The algorithm also predicts the opponent’s future positions (using a simple step-by-step addition of the current direction) to adjust the score. Moves that may lead into a trap or collision are penalized.

- **Power-Up Influence:**  
  Depending on the type of power-up and the snake’s mode, moves are scored higher or lower based on their proximity to these power-ups.

- **Mode-Specific Adjustments:**  
  The snake can switch between modes (aggressive, defensive, explorative, etc.) based on the environment:
  - **Aggressive Mode:** Prioritizes moves that minimize distance to the opponent (to attack or trap).
  - **Defensive Mode:** Favors avoiding collisions and dangerous zones.
  - **Explorative Mode:** Looks for moves that lead into unexplored (free) spaces when food is far away.

After evaluating all safe moves, the AI chooses the move with the lowest score (the best move) if the snake’s “intelligence” threshold is met. Otherwise, it may pick a random safe move.

---

## 4. Collision and Game Mechanics

### Collision Detection

Collision checks occur in several places:
- **Wall Collision:**  
  If the snake’s head moves outside the grid, it is considered a collision.
- **Self-Collision:**  
  The snake checks if its head has run into any other part of its body.
- **Obstacle Collision:**  
  The snake’s head position is compared against a list of obstacles.
- **Snake-to-Snake Collision:**  
  Head-to-head collisions or a snake’s head colliding with the body of the opponent are detected and resolved. When shields are active, collisions might instead disable the shield and trigger particle effects rather than ending the game immediately.

### Power-Up Effects

When a snake’s head coincides with a power-up’s grid cell, the effect is applied immediately:
- **Speed Boost/Slow:** Modifies the boost multiplier used in physics.
- **Shield:** Provides temporary immunity against collisions.
- **Invisibility:** Alters collision logic so that obstacles and the opponent are mostly ignored.
- **Growth:** Instantly increases the snake’s score and body length.
- **Freeze/Fire:** Applies specific effects such as freezing the opponent or initiating an aggressive mode, along with visual particle effects.

---

## 5. Main Game Loop

The main game loop is responsible for:
- **Handling Input:**  
  While the snakes are controlled by AI, the user can interact with menus.
- **Updating AI Decisions:**  
  Each frame, the AI determines a new direction for each snake.
- **Updating Physics:**  
  The snakes’ positions, velocities, and power-up timers are updated.
- **Collision Checks:**  
  The game continuously checks for collisions between snakes, walls, obstacles, and power-ups.
- **Rendering:**  
  The background, grid, food, obstacles, power-ups, snakes, and particles are redrawn every frame.

The loop runs at a fixed FPS (e.g., 30 FPS) to ensure smooth animation and consistent physics updates.

---

## Summary

In essence, the project is a blend of:
- **Physics Simulation:** Using vector arithmetic, force, acceleration, and friction to simulate snake motion.
- **AI Heuristics:** Combining Manhattan distances, mode-specific adjustments, and predictive behavior to choose safe and effective moves.
- **Dynamic Visuals:** Implementing particle systems and gradient-based rendering to create an engaging visual experience.

Each component (physics, AI, and collision detection) interlocks with the others to form a robust simulation of a snake game where two AI opponents continuously learn and adapt their strategies during the match.

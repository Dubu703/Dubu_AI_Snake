from collections import deque
from enum import Enum
import random

# --- From Phase 1 Example Code ---
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# --- From Phase 2 Example Code (and extended) ---
class SnakeEnv:
    def __init__(self, size=10):
        self.size = size
        self.snake = deque([(5, 5), (5, 6)])  # Initial snake
        self.direction = Direction.UP
        self.food = self._generate_food()
        self.score = 0
        self.done = False

    def _generate_food(self):
        while True:
            food_x = random.randint(0, self.size - 1)
            food_y = random.randint(0, self.size - 1)
            new_food = (food_x, food_y)
            if new_food not in self.snake:
                return new_food

    def step(self, action_dir: Direction):
        if self.done:
            raise ValueError("Game is over, cannot take further steps.")

        # Update direction
        self.direction = action_dir

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Collision detection (wall)
        if not (0 <= new_head[0] < self.size and 0 <= new_head[1] < self.size):
            self.done = True
            return self.get_state(), -10, True, {"message": "Wall collision"}

        # Collision detection (self)
        if new_head in list(self.snake)[:-1]: # Check against body, excluding current tail
            self.done = True
            return self.get_state(), -10, True, {"message": "Self collision"}

        # Food eating logic
        if new_head == self.food:
            self.snake.appendleft(new_head) # Snake grows
            self.score += 1
            self.food = self._generate_food()
            reward = 10
        else:
            self.snake.appendleft(new_head)
            self.snake.pop() # Snake moves normally
            reward = -1 # Encourage reaching food faster

        # Check for game over (e.g., no more space for food, though unlikely in simple snake)
        if len(self.snake) == self.size * self.size:
            self.done = True
            return self.get_state(), 100, True, {"message": "Game completed successfully"}

        return self.get_state(), reward, self.done, {}

    def get_state(self):
        """
        Returns the current state of the environment for the AI.
        This could be improved later in Phase 3.
        """
        return {
            "snake_body": list(self.snake),
            "food_position": self.food,
            "direction": self.direction,
            "score": self.score,
            "board_size": self.size,
            "done": self.done
        }
    
    def reset(self):
        """
        Resets the environment to an initial state.
        """
        self.snake = deque([(5, 5), (5, 6)])
        self.direction = Direction.UP
        self.food = self._generate_food()
        self.score = 0
        self.done = False
        return self.get_state()


if __name__ == "__main__":
    print("--- Snake Environment Simulation Test ---")
    env = SnakeEnv(size=10)
    initial_state = env.get_state()
    print(f"Initial State: {initial_state}")

    # Test moving right
    print("\n--- Moving RIGHT ---")
    state, reward, done, info = env.step(Direction.RIGHT)
    print(f"State after RIGHT: {state}, Reward: {reward}, Done: {done}, Info: {info}")
    
    # Test moving down
    print("\n--- Moving DOWN ---")
    state, reward, done, info = env.step(Direction.DOWN)
    print(f"State after DOWN: {state}, Reward: {reward}, Done: {done}, Info: {info}")

    # Test eating food (manual setup for testing)
    print("\n--- Testing Food Eating ---")
    env_food_test = SnakeEnv(size=5)
    env_food_test.snake = deque([(2, 2), (2, 3)])
    env_food_test.direction = Direction.UP
    env_food_test.food = (2, 1) # Place food right in front of snake head
    print(f"State before eating: {env_food_test.get_state()}")
    state, reward, done, info = env_food_test.step(Direction.UP)
    print(f"State after eating: {state}, Reward: {reward}, Done: {done}, Info: {info}")
    assert len(state["snake_body"]) == 3, "Snake should have grown"
    assert env_food_test.score == 1, "Score should have increased"
    assert env_food_test.food != (2, 1), "Food should have regenerated"

    # Test wall collision
    print("\n--- Testing Wall Collision (LEFT) ---")
    env_wall_test = SnakeEnv(size=3)
    env_wall_test.snake = deque([(0, 1), (1, 1)])
    env_wall_test.direction = Direction.LEFT
    state, reward, done, info = env_wall_test.step(Direction.LEFT)
    print(f"State after LEFT into wall: {state}, Reward: {reward}, Done: {done}, Info: {info}")
    assert done == True, "Game should be over due to wall collision"

    # Test self collision
    print("\n--- Testing Self Collision ---")
    env_self_test = SnakeEnv(size=5)
    env_self_test.snake = deque([(2, 2), (2, 3), (3, 3), (3, 2), (2, 2)]) # Make a loop
    env_self_test.snake = deque([(2, 2), (3, 2), (3, 3), (2, 3)]) # Snake moving UP, head at (2,2)
    env_self_test.direction = Direction.UP
    # Move to (2,1)
    env_self_test.step(Direction.UP) # (2,1), (2,2), (3,2), (3,3)
    # Move LEFT to (1,1)
    env_self_test.step(Direction.LEFT) # (1,1), (2,1), (2,2), (3,2)
    # Move DOWN to (1,2)
    env_self_test.step(Direction.DOWN) # (1,2), (1,1), (2,1), (2,2)
    # Move RIGHT to (2,2) - this will collide with (2,2) which is part of the body
    env_self_test.food = (0,0) # ensure no food in the way
    print(f"State before self-collision: {env_self_test.get_state()}")
    state, reward, done, info = env_self_test.step(Direction.RIGHT) # head will be (2,2)
    print(f"State after RIGHT to self-collide: {state}, Reward: {reward}, Done: {done}, Info: {info}")
    assert done == True, "Game should be over due to self collision"
    assert info["message"] == "Self collision", "Collision message incorrect"

    print("\n--- Reset Test ---")
    env_reset_test = SnakeEnv(size=10)
    env_reset_test.step(Direction.RIGHT)
    env_reset_test.step(Direction.RIGHT)
    print(f"State before reset: {env_reset_test.get_state()}")
    reset_state = env_reset_test.reset()
    print(f"State after reset: {reset_state}")
    assert env_reset_test.score == 0
    assert len(env_reset_test.snake) == 2 # Initial snake length
    assert env_reset_test.direction == Direction.UP
    assert env_reset_test.done == False
    print("All tests passed!")

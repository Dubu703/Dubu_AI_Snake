from typing import List, Tuple, Dict
from enum import Enum

# Import necessary components from other modules
from snake_env import Direction, SnakeEnv # Assuming SnakeEnv and Direction are defined here
from state_perception import find_reachable_areas_bfs, has_path_to_target_bfs
from safety_logic import is_collision, is_future_isolated, simulate_n_steps
from path_planning import a_star_search
from cost_function import calculate_action_cost

class PolicyAgent:
    def __init__(self, board_size: int):
        self.board_size = board_size

    def get_safe_actions(self, current_head: Tuple[int, int], snake_body: List[Tuple[int, int]]) -> List[Direction]:
        """
        Generates a set of safe actions by filtering out moves that lead to immediate collision.
        """
        safe_actions = []
        for action in Direction:
            dx, dy = action.value
            next_head = (current_head[0] + dx, current_head[1] + dy)
            if not is_collision(next_head, self.board_size, snake_body):
                safe_actions.append(action)
        return safe_actions

    def choose_best_action(
        self,
        current_head: Tuple[int, int],
        current_direction: Direction,
        snake_body: List[Tuple[int, int]],
        food_position: Tuple[int, int]
    ) -> Direction:
        """
        Evaluates all safe actions and selects the one with the minimum calculated cost.
        """
        possible_actions = self.get_safe_actions(current_head, snake_body)
        
        if not possible_actions:
            # If no safe actions, the game is likely over or in a very bad state.
            # In a real AI, this might trigger a 'last resort' move or just return the current direction
            # to signify no good option. For now, we'll try to find any move that won't immediately kill.
            # If still no valid move, return current direction (which likely leads to death).
            
            # This scenario should ideally be caught by is_collision, but as a fallback
            print("WARNING: No safe actions found. Game likely over or trapped.")
            # Try to make a move that doesn't immediately result in collision *if possible*.
            # This is a fallback and usually means the game will end.
            for action in Direction:
                dx, dy = action.value
                next_head = (current_head[0] + dx, current_head[1] + dy)
                if not is_collision(next_head, self.board_size, snake_body):
                    return action # Return first non-colliding action as a last resort
            return current_direction # If all moves lead to collision, return current (will result in death)


        # Evaluate costs for all safe actions
        action_costs = []
        for action in possible_actions:
            cost = calculate_action_cost(
                current_head=current_head,
                current_direction=current_direction,
                proposed_action=action,
                snake_body=snake_body,
                food_position=food_position,
                board_size=self.board_size,
                is_collision_func=is_collision,
                a_star_search_func=a_star_search,
                is_future_isolated_func=is_future_isolated,
                find_reachable_areas_bfs_func=find_reachable_areas_bfs
            )
            action_costs.append({"action": action, "cost": cost})

        # Sort by cost and return the action with the minimum cost
        action_costs.sort(key=lambda x: x['cost'])
        best_action = action_costs[0]['action']
        
        return best_action

# --- Test Cases ---
if __name__ == "__main__":
    print("--- PolicyAgent Test ---")
    board_size_test = 10
    agent = PolicyAgent(board_size_test)
    env = SnakeEnv(board_size_test)

    # Test 1: Simple move towards food without obstacles
    print("\nTest 1: Simple move towards food")
    env.snake = deque([(5, 5), (5, 6)])
    env.direction = Direction.UP
    env.food = (5, 3) # Food is UP
    current_state = env.get_state()
    
    best_action = agent.choose_best_action(
        current_head=current_state["snake_body"][0],
        current_direction=current_state["direction"],
        snake_body=current_state["snake_body"],
        food_position=current_state["food_position"]
    )
    print(f"Current State: {current_state}")
    print(f"Chosen Action: {best_action}")
    assert best_action == Direction.UP, "Test 1 Failed: Should move UP towards food"

    # Test 2: Avoid immediate collision
    print("\nTest 2: Avoid immediate collision")
    env.snake = deque([(0, 0), (0, 1)]) # Head at (0,0)
    env.direction = Direction.LEFT # Trying to move LEFT into wall
    env.food = (5, 5) # Food far away
    current_state = env.get_state()
    
    # In this scenario, LEFT and UP would be collisions. DOWN and RIGHT are safe.
    # The cost function should prefer moving towards food (even if far) or avoiding turns.
    best_action = agent.choose_best_action(
        current_head=current_state["snake_body"][0],
        current_direction=current_state["direction"],
        snake_body=current_state["snake_body"],
        food_position=current_state["food_position"]
    )
    print(f"Current State: {current_state}")
    print(f"Chosen Action: {best_action}")
    # Expecting RIGHT or DOWN, should not be LEFT or UP (collisions)
    assert best_action in [Direction.RIGHT, Direction.DOWN], "Test 2 Failed: Should avoid immediate collision"


    # Test 3: Prioritize food, but turn if necessary
    print("\nTest 3: Prioritize food, turn if necessary")
    env.snake = deque([(5, 5), (5, 6)])
    env.direction = Direction.RIGHT # Snake moving right
    env.food = (4, 5) # Food is to the LEFT, needs a turn
    current_state = env.get_state()
    
    best_action = agent.choose_best_action(
        current_head=current_state["snake_body"][0],
        current_direction=current_state["direction"],
        snake_body=current_state["snake_body"],
        food_position=current_state["food_position"]
    )
    print(f"Current State: {current_state}")
    print(f"Chosen Action: {best_action}")
    assert best_action == Direction.LEFT, "Test 3 Failed: Should turn LEFT for food"


    # Test 4: No safe actions (trapped)
    print("\nTest 4: No safe actions (trapped)")
    # Create a scenario where the snake is completely surrounded
    env.snake = deque([(1,1), (1,2), (2,2), (2,1)]) # Head at (1,1), surrounded
    env.direction = Direction.UP # Doesn't matter
    env.food = (0,0) # Far
    current_state = env.get_state()
    
    safe_actions_trapped = agent.get_safe_actions(current_state["snake_body"][0], current_state["snake_body"])
    print(f"Safe actions in trapped state: {safe_actions_trapped}")
    assert not safe_actions_trapped, "Test 4 Failed: Should have no safe actions"

    best_action_trapped = agent.choose_best_action(
        current_head=current_state["snake_body"][0],
        current_direction=current_state["direction"],
        snake_body=current_state["snake_body"],
        food_position=current_state["food_position"]
    )
    print(f"Chosen Action in trapped state: {best_action_trapped}")
    # In this case, the fallback returns current_direction, which will lead to death.
    assert best_action_trapped == Direction.UP, "Test 4 Failed: Fallback action incorrect"


    print("\nAll policy_agent.py tests completed.")

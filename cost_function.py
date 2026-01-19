from typing import List, Tuple
from enum import Enum

# Assume Direction Enum is available from snake_env.py or similar
# For standalone testing, we can define it here.
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Import necessary functions from previously implemented modules
# from .snake_env import SnakeEnv # For state and actions
# from .state_perception import has_path_to_target_bfs, find_reachable_areas_bfs
# from .safety_logic import is_collision, is_future_isolated, simulate_n_steps
# from .path_planning import a_star_search

# For standalone execution and clear context, we'll assume the necessary tools are available.
# In a real project, proper imports would be used.

def turn_cost(current_dir: Direction, next_dir: Direction) -> int:
    """
    Calculates the cost of changing direction.
    0 if moving straight, 1 if turning.
    """
    if current_dir == next_dir:
        return 0
    
    # Check for 180 degree turn (moving directly backward) - this is usually disallowed or highly costly
    # A simple check for this would be: if next_dir is opposite of current_dir
    opposite_directions = {
        Direction.UP: Direction.DOWN,
        Direction.DOWN: Direction.UP,
        Direction.LEFT: Direction.RIGHT,
        Direction.RIGHT: Direction.LEFT
    }
    if opposite_directions.get(current_dir) == next_dir:
        return 1000000 # Very high cost or disallow, for now, high cost.
    
    return 1 # For a 90 degree turn

def calculate_action_cost(
    current_head: Tuple[int, int],
    current_direction: Direction,
    proposed_action: Direction,
    snake_body: List[Tuple[int, int]],
    food_position: Tuple[int, int],
    board_size: int,
    # Additional context from other modules (passed as parameters for loose coupling)
    is_collision_func, # Function from safety_logic
    a_star_search_func, # Function from path_planning
    is_future_isolated_func, # Function from safety_logic
    find_reachable_areas_bfs_func # Function from state_perception
) -> float:
    """
    Calculates a comprehensive cost for a proposed action based on various factors.
    Lower cost is better.
    """
    cost = 0.0

    # Calculate the new head position after the proposed action
    dx, dy = proposed_action.value
    next_head = (current_head[0] + dx, current_head[1] + dy)

    # --- 1. Survival Conditions (Highest Priority / Hard Constraints) ---
    # Check for immediate collision
    if is_collision_func(next_head, board_size, snake_body):
        return float('inf') # Infinite cost for immediate death

    # --- 2. Direction Change Cost ---
    cost += turn_cost(current_direction, proposed_action) * 5 # Multiply to make turning more impactful

    # --- 3. Path to Food ---
    path_to_food = a_star_search_func(next_head, food_position, board_size, list(snake_body))
    if path_to_food:
        cost += len(path_to_food) # Shorter path to food is better
        # Consider a bonus for reaching food
        if len(path_to_food) == 1: # If next step is food
            cost -= 100 # Strong bonus for eating food
    else:
        cost += 1000 # High cost if no path to food is found after this action


    # --- 4. Future Isolation (Heuristic for long-term survival) ---
    # This check is more complex as it needs to consider the snake body's state after the move
    # For a simplified check: does this move lead to a state where there's no path to tail?
    # This is a heuristic.
    # To properly check isolation, we need the *next* snake body state.
    # For a rough estimate, we can use the current snake body and check if the next_head has enough free space.
    
    # Calculate what the snake body would be after this move (before food check)
    temp_snake_body = deque(snake_body)
    temp_snake_body.appendleft(next_head)
    # If food is not eaten, tail would pop
    if next_head != food_position:
        temp_snake_body.pop() # Simulate tail movement

    next_tail = temp_snake_body[-1]

    # Check for isolation: if no path to food AND no path to tail
    if not a_star_search_func(next_head, food_position, board_size, list(temp_snake_body)) and \
       not a_star_search_func(next_head, next_tail, board_size, list(temp_snake_body)):
        # This is a rough isolation check. More robust would be to check reachable area size.
        reachable_count, _ = find_reachable_areas_bfs_func(next_head, board_size, list(temp_snake_body), food_position)
        if reachable_count < len(temp_snake_body) * 2: # Arbitrary threshold for potentially trapping
             cost += 500 # High cost for potentially being isolated

    # --- 5. Proximity to Walls/Center (Optional) ---
    # Penalize being too close to walls if not necessary, or reward being central
    # This can be added later if needed.

    return cost

# --- Test Cases ---
if __name__ == "__main__":
    from snake_env import SnakeEnv, Direction as EnvDirection # Using the actual Direction enum from snake_env
    from state_perception import find_reachable_areas_bfs, has_path_to_target_bfs
    from safety_logic import is_collision, is_future_isolated, simulate_n_steps
    from path_planning import a_star_search

    board_size_test = 10
    
    print("--- Test turn_cost ---")
    assert turn_cost(EnvDirection.UP, EnvDirection.UP) == 0, "Turn cost failed"
    assert turn_cost(EnvDirection.UP, EnvDirection.LEFT) == 1, "Turn cost failed"
    assert turn_cost(EnvDirection.UP, EnvDirection.RIGHT) == 1, "Turn cost failed"
    assert turn_cost(EnvDirection.UP, EnvDirection.DOWN) == 1000000, "Opposite direction cost failed"
    print("turn_cost tests passed!")

    print("\n--- Test calculate_action_cost ---")
    env = SnakeEnv(board_size_test)
    initial_state = env.get_state()
    
    # Mocking functions from other modules
    mock_is_collision = is_collision
    mock_a_star_search = a_star_search
    mock_is_future_isolated = is_future_isolated # Though not directly used, useful for context
    mock_find_reachable_areas_bfs = find_reachable_areas_bfs

    current_head = initial_state["snake_body"][0]
    current_direction = initial_state["direction"]
    snake_body = initial_state["snake_body"]
    food_position = initial_state["food_position"]

    # Scenario 1: Action leads to immediate collision (e.g., UP from (5,5) with snake at (5,5),(5,6))
    # Let's set a collision scenario
    collision_snake_body = [(0,0), (0,1)] # Head at (0,0)
    cost_collision = calculate_action_cost(
        current_head=(0,0),
        current_direction=EnvDirection.UP, # Try to move UP
        proposed_action=EnvDirection.UP,
        snake_body=collision_snake_body,
        food_position=(5,5),
        board_size=board_size_test,
        is_collision_func=mock_is_collision,
        a_star_search_func=mock_a_star_search,
        is_future_isolated_func=mock_is_future_isolated,
        find_reachable_areas_bfs_func=mock_find_reachable_areas_bfs
    )
    print(f"Cost for collision action (UP from (0,0)): {cost_collision}")
    assert cost_collision == float('inf'), "Collision cost not infinite"

    # Scenario 2: Action leads to food, no turns (best case)
    env_food = SnakeEnv(board_size_test)
    env_food.snake = deque([(1,1), (1,2)])
    env_food.direction = EnvDirection.LEFT
    env_food.food = (0,1) # Food is directly to the left
    state_food = env_food.get_state()
    
    cost_food = calculate_action_cost(
        current_head=(1,1),
        current_direction=EnvDirection.LEFT,
        proposed_action=EnvDirection.LEFT,
        snake_body=list(env_food.snake),
        food_position=env_food.food,
        board_size=board_size_test,
        is_collision_func=mock_is_collision,
        a_star_search_func=mock_a_star_search,
        is_future_isolated_func=mock_is_future_isolated,
        find_reachable_areas_bfs_func=mock_find_reachable_areas_bfs
    )
    print(f"Cost for action leading to food (LEFT from (1,1) to (0,1)): {cost_food}")
    # Expected: path length 1 - 100 (bonus) = 1 - 100 + turn_cost(0) = -99
    assert cost_food == 0 + 1 - 100, "Cost to food calculation failed"
    print("Cost to food test passed!")

    # Scenario 3: Action requires a turn, longer path to food
    env_turn = SnakeEnv(board_size_test)
    env_turn.snake = deque([(1,1), (1,2)])
    env_turn.direction = EnvDirection.UP
    env_turn.food = (0,1) # Food to the left, requires a turn
    state_turn = env_turn.get_state()

    cost_turn = calculate_action_cost(
        current_head=(1,1),
        current_direction=EnvDirection.UP,
        proposed_action=EnvDirection.LEFT,
        snake_body=list(env_turn.snake),
        food_position=env_turn.food,
        board_size=board_size_test,
        is_collision_func=mock_is_collision,
        a_star_search_func=mock_a_star_search,
        is_future_isolated_func=mock_is_future_isolated,
        find_reachable_areas_bfs_func=mock_find_reachable_areas_bfs
    )
    print(f"Cost for action with turn to food (UP then LEFT to (0,1)): {cost_turn}")
    # Expected: turn cost 1 * 5 = 5. Path length 1. Bonus -100. Total = 5 + 1 - 100 = -94
    assert cost_turn == (1 * 5) + 1 - 100, "Cost with turn to food calculation failed"
    print("Cost with turn to food test passed!")
    
    print("\nAll cost_function.py tests completed.")

import heapq
from typing import List, Tuple, Dict
from collections import deque

# Assume Direction Enum is available from snake_env.py or similar
# For standalone testing, we can define it here.
from enum import Enum
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """
    Manhattan distance heuristic for A* algorithm.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start: Tuple[int, int], goal: Tuple[int, int], size: int, snake_body: List[Tuple[int, int]]) -> List[Tuple[int, int]] | None:
    """
    Finds the shortest path from start to goal using the A* algorithm.
    Obstacles are the snake's body. The tail is treated as free space if it's the goal.
    Returns a list of coordinates representing the path, or None if no path is found.
    """
    # Priority queue: (f_cost, g_cost, current_node, path)
    # f_cost = g_cost + h_cost
    # g_cost = cost from start to current_node
    # h_cost = heuristic estimate from current_node to goal
    open_set = [(0, 0, start, [])] # f_cost, g_cost, node, path_so_far
    
    # Store the lowest g_cost found for each node
    g_costs: Dict[Tuple[int, int], int] = {start: 0}

    # Obstacles: entire snake body, but if goal is tail, then tail is not an obstacle.
    obstacles = set(snake_body)
    if goal in obstacles:
        obstacles.remove(goal) # If we are pathfinding to the tail, the tail itself is not an obstacle.
    if start in obstacles: # Head is not an obstacle for itself
        obstacles.remove(start)
    
    # Pre-compute valid neighbors for efficiency if board is large, but for snake game, small board. 
    
    while open_set:
        f_cost, g_cost, current_pos, path = heapq.heappop(open_set)

        if current_pos == goal:
            return path + [current_pos] # Path found!

        for dx, dy in [d.value for d in Direction]:
            neighbor_x, neighbor_y = current_pos[0] + dx, current_pos[1] + dy
            neighbor_pos = (neighbor_x, neighbor_y)

            # Check boundaries and obstacles
            if not (0 <= neighbor_x < size and 0 <= neighbor_y < size):
                continue
            if neighbor_pos in obstacles:
                continue

            # Cost to reach this neighbor
            new_g_cost = g_cost + 1 # Each step has a cost of 1

            if neighbor_pos not in g_costs or new_g_cost < g_costs[neighbor_pos]:
                g_costs[neighbor_pos] = new_g_cost
                h_cost = heuristic(neighbor_pos, goal)
                f_cost = new_g_cost + h_cost
                heapq.heappush(open_set, (f_cost, new_g_cost, neighbor_pos, path + [current_pos]))
                
    return None # No path found

def find_longest_path_bfs(start: Tuple[int, int], size: int, snake_body: List[Tuple[int, int]], avoid_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]] | None:
    """
    Finds the longest safe path from start to a position that is not in avoid_positions,
    avoiding snake_body as obstacles. This is useful for tail chasing or avoiding immediate death.
    Returns the path. If no long path, returns None or shortest safe path.
    This is a simplification of a true longest path, focusing on just finding any safe path first.
    For true longest path, one might explore all safe paths and pick the longest.
    A more practical approach for snake AI is to find *any* safe path, and if it leads to tail, even better.
    """
    
    q = deque([(start, [])]) # (current_pos, path_so_far)
    visited = {start}
    
    obstacles = set(snake_body + avoid_positions)
    if start in obstacles:
        obstacles.remove(start) # Head is not an obstacle for itself

    longest_path = []

    while q:
        current_pos, path_so_far = q.popleft()

        if len(path_so_far) > len(longest_path):
            longest_path = path_so_far
        
        for dx, dy in [d.value for d in Direction]:
            neighbor_x, neighbor_y = current_pos[0] + dx, current_pos[1] + dy
            neighbor_pos = (neighbor_x, neighbor_y)

            if not (0 <= neighbor_x < size and 0 <= neighbor_y < size):
                continue
            if neighbor_pos in obstacles:
                continue
            if neighbor_pos in visited:
                continue
            
            visited.add(neighbor_pos)
            q.append((neighbor_pos, path_so_far + [current_pos])) # Add current_pos to path

    # If start is already an obstacle, then the path cannot even start
    if start in set(snake_body + avoid_positions):
        return None

    # After BFS, longest_path contains the longest path found that was valid
    # But this simple BFS doesn't guarantee a path to a specific target,
    # just finds reachable cells.
    # For tail chase, we need a path *to* the tail.
    # The `has_path_to_target_bfs` is more appropriate.
    
    # Re-evaluating: The "Tail Chase strategy" is better implemented using A* to the tail.
    # We need to find a path to the tail (if food is unreachable or dangerous) and ensure it's safe.
    # "安全 루프 생성" implies not getting trapped.
    
    # A simple Tail Chase using A* will be:
    # 1. Find path to food.
    # 2. If no path to food, or food path is risky, find path to tail.
    #    When pathfinding to tail, consider the *future* position of the tail (which is one step behind current tail).
    # This function `find_longest_path_bfs` might be useful for exploring general safe areas,
    # but for a direct "tail chase", A* to tail is more direct.
    
    # Let's adjust, and primarily use A* for pathfinding to specific targets.
    # `find_longest_path_bfs` is removed from here for simplicity and focus.
    return longest_path if longest_path else None # Return longest path or None

def find_safe_path(start: Tuple[int, int], target: Tuple[int, int], size: int, snake_body: List[Tuple[int, int]], current_tail: Tuple[int, int]) -> List[Tuple[int, int]] | None:
    """
    Combines A* search to find a path, with considerations for tail movement.
    When pathfinding to the tail, the tail's next position is considered free.
    """
    obstacles = set(snake_body)
    
    # If the target is the current tail, the tail will move, so it's not an obstacle.
    # For A* to tail, the tail's *next* position (current_tail_minus_one_step) becomes accessible.
    # However, A* usually assumes static obstacles. A more robust tail chase
    # involves checking if the path to the tail still leaves enough space for the snake.
    
    # For a simple A* to tail:
    # 1. Path to target (food)
    # 2. If target is tail, obstacles should exclude the tail itself.
    
    if target == current_tail:
        # If targeting tail, the current tail position is considered free.
        # But this is not enough for a *safe* tail chase, as the snake might get trapped.
        # A proper tail chase ensures a path to the tail that doesn't reduce free space.
        
        # A simple approach for safe tail chase:
        # Find path to tail using A*. After finding it, check if the remaining board
        # still provides enough free cells for the snake to survive for a few turns.
        
        # For `a_star_search`, the `goal` being in `obstacles` will make it remove `goal` from `obstacles`.
        path = a_star_search(start, target, size, list(obstacles))
        if path:
            # Additional check for safety for tail chase path.
            # This is complex and might involve simulating the path.
            # For this phase, let's just implement a simple A* to tail.
            return path
        return None
    else:
        # Path to food. Regular A*
        path = a_star_search(start, target, size, list(obstacles))
        return path

# --- Test Cases ---
if __name__ == "__main__":
    board_size_test = 10

    print("--- Test heuristic ---")
    assert heuristic((0,0), (3,4)) == 7, "Heuristic test failed"
    print("heuristic test passed!")

    print("\n--- Test a_star_search ---")
    snake_body_astar = [(2,2), (2,3), (2,4)] # Head (2,2), Tail (2,4)
    start_astar = (2,2)
    
    # Path to food
    goal_food_astar = (0,0)
    path_to_food = a_star_search(start_astar, goal_food_astar, board_size_test, snake_body_astar)
    print(f"Path to food {goal_food_astar}: {path_to_food}")
    assert path_to_food is not None, "A* path to food failed"
    assert path_to_food[0] == start_astar, "Path should start at start_astar"
    assert path_to_food[-1] == goal_food_astar, "Path should end at goal_food_astar"

    # Path to tail (tail is not an obstacle for pathfinding to itself)
    goal_tail_astar = (2,4) # Current tail position
    path_to_tail = a_star_search(start_astar, goal_tail_astar, board_size_test, snake_body_astar)
    print(f"Path to tail {goal_tail_astar}: {path_to_tail}")
    assert path_to_tail is not None, "A* path to tail failed"
    assert path_to_tail[0] == start_astar, "Path should start at start_astar"
    assert path_to_tail[-1] == goal_tail_astar, "Path should end at goal_tail_astar"

    # No path (blocked)
    blocked_snake = [(1,1), (1,2), (1,3)]
    blocked_start = (0,1)
    blocked_goal = (2,1)
    no_path = a_star_search(blocked_start, blocked_goal, 3, blocked_snake)
    print(f"Path (blocked): {no_path}")
    assert no_path is None, "A* no path test failed" 
    
    print("a_star_search tests passed!")

    print("\n--- Test find_safe_path (simplified tail chase) ---")
    snake_chase = [(5,5), (5,6), (5,7)] # Head (5,5), Tail (5,7)
    food_chase = (0,0)
    
    # Path to food
    safe_path_to_food = find_safe_path((5,5), food_chase, board_size_test, snake_chase, (5,7))
    print(f"Safe path to food: {safe_path_to_food}")
    assert safe_path_to_food is not None, "Safe path to food failed"

    # Path to tail (when food is unreachable or undesirable)
    # The `find_safe_path` re-uses `a_star_search`, which already handles tail as goal.
    safe_path_to_tail = find_safe_path((5,5), (5,7), board_size_test, snake_chase, (5,7))
    print(f"Safe path to tail: {safe_path_to_tail}")
    assert safe_path_to_tail is not None, "Safe path to tail failed"
    
    # Scenario: trapped, no path to food or safe path to tail
    # This requires a very specific setup, hard to test without full env simulation.
    
    print("find_safe_path tests passed (simple A* to target)!")

    print("\nAll path_planning.py tests completed.")

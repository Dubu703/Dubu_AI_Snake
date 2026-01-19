# Dubu_AI_Snake/game_rules.py

class SnakeGameRules:
    """
    Defines the fundamental rules and structure of the Google Snake Game
    for AI development.
    """
    def __init__(self, board_width: int = 10, board_height: int = 10):
        """
        Initializes the game board dimensions.

        Args:
            board_width (int): The width of the game board.
            board_height (int): The height of the game board.
        """
        if not (isinstance(board_width, int) and board_width > 0):
            raise ValueError("Board width must be a positive integer.")
        if not (isinstance(board_height, int) and board_height > 0):
            raise ValueError("Board height must be a positive integer.")

        self.board_width = board_width
        self.board_height = board_height
        self.coordinate_system = "Top-left is (0,0), x increases right, y increases down."

    def get_board_dimensions(self) -> tuple[int, int]:
        """
        Returns the dimensions of the game board.
        """
        return self.board_width, self.board_height

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        """
        Checks if a given coordinate is within the board boundaries.
        """
        return 0 <= x < self.board_width and 0 <= y < self.board_height

    def get_movement_rules(self) -> dict:
        """
        Defines the possible movements and their corresponding coordinate changes.
        """
        return {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0),
        }

    def get_collision_conditions(self) -> list[str]:
        """
        Lists conditions that lead to game over (collision).
        """
        return [
            "Collision with wall",
            "Collision with self (snake's body)",
        ]

    def get_scoring_condition(self) -> str:
        """
        Defines the condition for increasing the score.
        """
        return "Eating food"

class GameState:
    """
    Defines the information that constitutes a game state for the AI.
    """
    def __init__(self, snake_body: list, food_position: tuple, current_direction: str,
                 board_width: int, board_height: int):
        """
        Initializes the game state.

        Args:
            snake_body (list): A list of (x, y) coordinates representing the snake's body,
                                with the head at the first element.
            food_position (tuple): (x, y) coordinate of the food.
            current_direction (str): The current direction of the snake (e.g., "UP", "DOWN").
            board_width (int): The width of the game board.
            board_height (int): The height of the game board.
        """
        if not isinstance(snake_body, list) or not all(isinstance(p, tuple) and len(p) == 2 for p in snake_body):
            raise ValueError("snake_body must be a list of (x,y) tuples.")
        if not isinstance(food_position, tuple) or len(food_position) != 2:
            raise ValueError("food_position must be an (x,y) tuple.")
        if current_direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
            raise ValueError("Invalid current_direction.")

        self.snake_body = snake_body
        self.food_position = food_position
        self.current_direction = current_direction
        self.board_width = board_width
        self.board_height = board_height
        self.score = len(snake_body) - 3 # Assuming initial snake length is 3

    def __repr__(self):
        return (
            f"GameState(snake_body={self.snake_body}, food_position={self.food_position}, "
            f"current_direction='{self.current_direction}', score={self.score})"
        )


class ActionSpace:
    """
    Defines the possible actions the AI can take.
    """
    def __init__(self):
        self.actions = ["UP", "DOWN", "LEFT", "RIGHT"] # Absolute directions
        self.relative_actions = ["STRAIGHT", "LEFT_TURN", "RIGHT_TURN"] # Relative to current direction

    def get_all_actions(self) -> list[str]:
        """
        Returns all absolute possible actions.
        """
        return self.actions

    def get_relative_actions(self) -> list[str]:
        """
        Returns all relative possible actions.
        """
        return self.relative_actions

    def get_absolute_direction(self, current_direction: str, relative_action: str) -> str:
        """
        Converts a relative action to an absolute direction based on current direction.

        Args:
            current_direction (str): The current absolute direction of the snake.
            relative_action (str): The relative action ("STRAIGHT", "LEFT_TURN", "RIGHT_TURN").

        Returns:
            str: The new absolute direction.
        """
        direction_map = {
            "UP": {"STRAIGHT": "UP", "LEFT_TURN": "LEFT", "RIGHT_TURN": "RIGHT"},
            "DOWN": {"STRAIGHT": "DOWN", "LEFT_TURN": "RIGHT", "RIGHT_TURN": "LEFT"},
            "LEFT": {"STRAIGHT": "LEFT", "LEFT_TURN": "DOWN", "RIGHT_TURN": "UP"},
            "RIGHT": {"STRAIGHT": "RIGHT", "LEFT_TURN": "UP", "RIGHT_TURN": "DOWN"},
        }
        if current_direction not in direction_map:
            raise ValueError(f"Invalid current_direction: {current_direction}")
        if relative_action not in direction_map[current_direction]:
            raise ValueError(f"Invalid relative_action: {relative_action}")

        return direction_map[current_direction][relative_action]


if __name__ == "__main__":
    print("--- Snake Game Rules ---")
    rules = SnakeGameRules(15, 15)
    print(f"Board Dimensions: {rules.get_board_dimensions()}")
    print(f"Coordinate System: {rules.coordinate_system}")
    print(f"Valid coordinate (5,5): {rules.is_valid_coordinate(5, 5)}")
    print(f"Valid coordinate (15,0): {rules.is_valid_coordinate(15, 0)}")
    print(f"Movement Rules: {rules.get_movement_rules()}")
    print(f"Collision Conditions: {rules.get_collision_conditions()}")
    print(f"Scoring Condition: {rules.get_scoring_condition()}")

    print("\n--- Game State Example ---")
    initial_snake = [(2, 0), (1, 0), (0, 0)] # Head at (2,0)
    food_pos = (5, 5)
    current_dir = "RIGHT"
    state = GameState(initial_snake, food_pos, current_dir, 15, 15)
    print(state)

    print("\n--- Action Space Example ---")
    actions = ActionSpace()
    print(f"Absolute Actions: {actions.get_all_actions()}")
    print(f"Relative Actions: {actions.get_relative_actions()}")

    # Example: Snake moving RIGHT, takes a LEFT_TURN
    new_direction = actions.get_absolute_direction("RIGHT", "LEFT_TURN")
    print(f"If current direction is RIGHT and action is LEFT_TURN, new direction is: {new_direction}") # Expected: UP
    
    # Example: Snake moving UP, goes STRAIGHT
    new_direction = actions.get_absolute_direction("UP", "STRAIGHT")
    print(f"If current direction is UP and action is STRAIGHT, new direction is: {new_direction}") # Expected: UP

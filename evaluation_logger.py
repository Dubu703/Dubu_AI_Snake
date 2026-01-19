import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Assume Direction Enum from snake_env.py
from enum import Enum
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameLogger:
    def __init__(self, log_dir: str = "."):
        self.log_dir = log_dir
        self.logs: Dict[str, Any] = {
            "game_id": None,
            "start_time": None,
            "end_time": None,
            "board_size": None,
            "final_score": None,
            "survival_time": None, # Number of steps
            "cause_of_death": None,
            "steps": [] # List of {'state', 'action', 'reward', 'new_state', 'info'}
        }
        self._current_game_id = None

    def start_new_game(self, board_size: int):
        self._current_game_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.logs = {
            "game_id": self._current_game_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "board_size": board_size,
            "final_score": 0,
            "survival_time": 0,
            "cause_of_death": None,
            "steps": []
        }

    def log_step(self,
                 state_before: Dict[str, Any],
                 action_taken: Direction,
                 reward: float,
                 state_after: Dict[str, Any],
                 done: bool,
                 info: Dict[str, Any]):
        
        if self._current_game_id is None:
            raise RuntimeError("Call start_new_game() before logging steps.")

        self.logs["steps"].append({
            "step_number": len(self.logs["steps"]),
            "state_before": self._serialize_state(state_before),
            "action_taken": action_taken.name,
            "reward": reward,
            "state_after": self._serialize_state(state_after),
            "done": done,
            "info": info
        })
        self.logs["survival_time"] = len(self.logs["steps"]) # Update survival time

    def end_game(self, final_score: int, cause_of_death: str = "Unknown"):
        if self._current_game_id is None:
            raise RuntimeError("Call start_new_game() before ending the game.")
            
        self.logs["end_time"] = datetime.now().isoformat()
        self.logs["final_score"] = final_score
        self.logs["cause_of_death"] = cause_of_death

    def save_logs(self, filename: str = None):
        if self._current_game_id is None:
            raise RuntimeError("No game has been started or logged yet.")
            
        if filename is None:
            filename = f"game_log_{self._current_game_id}.json"
        
        filepath = f"{self.log_dir}/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=4)
        print(f"Game logs saved to {filepath}")
        return filepath

    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to convert Enum to string for JSON serialization."""
        serialized = state.copy()
        if "direction" in serialized and isinstance(serialized["direction"], Direction):
            serialized["direction"] = serialized["direction"].name
        if "snake_body" in serialized:
            serialized["snake_body"] = [list(pos) for pos in serialized["snake_body"]] # Convert tuples to lists for JSON
        if "food_position" in serialized and isinstance(serialized["food_position"], tuple):
            serialized["food_position"] = list(serialized["food_position"]) # Convert tuple to list for JSON
        return serialized


# --- Test Cases ---
if __name__ == "__main__":
    print("--- GameLogger Test ---")
    logger = GameLogger()

    # Simulate a game
    board_size_test = 5
    logger.start_new_game(board_size_test)
    
    # Mock states and actions
    state1 = {"snake_body": [(2,2), (2,3)], "food_position": (0,0), "direction": Direction.UP, "score": 0, "board_size": 5, "done": False}
    state2 = {"snake_body": [(2,1), (2,2)], "food_position": (0,0), "direction": Direction.UP, "score": 0, "board_size": 5, "done": False}
    state3 = {"snake_body": [(2,0), (2,1)], "food_position": (0,0), "direction": Direction.UP, "score": 0, "board_size": 5, "done": True} # Game over

    logger.log_step(state1, Direction.UP, -1, state2, False, {{}})
    logger.log_step(state2, Direction.UP, -1, state3, True, {"message": "Wall collision"})
    
    logger.end_game(final_score=0, cause_of_death="Wall collision")

    # Save and verify logs
    try:
        log_filepath = logger.save_logs("test_game_log.json")
        with open(log_filepath, 'r', encoding='utf-8') as f:
            loaded_logs = json.load(f)
            
            assert loaded_logs["board_size"] == board_size_test
            assert loaded_logs["final_score"] == 0
            assert loaded_logs["survival_time"] == 2
            assert loaded_logs["cause_of_death"] == "Wall collision"
            assert len(loaded_logs["steps"]) == 2
            assert loaded_logs["steps"][0]["action_taken"] == "UP"
            assert loaded_logs["steps"][1]["info"]["message"] == "Wall collision"
            
            print("Log saving and loading test passed!")
            
    except Exception as e:
        print(f"Log test failed: {e}")
    
    # Test error handling
    print("\nTesting error handling for logger:")
    error_logger = GameLogger()
    try:
        error_logger.log_step({{}}, Direction.UP, 0, {{}}, False, {{}})
    except RuntimeError as e:
        print(f"Caught expected error: {e}")

    print("\nAll evaluation_logger.py tests completed.")

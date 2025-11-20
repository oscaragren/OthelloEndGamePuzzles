"""Puzzle generation logic for Othello endgame puzzles."""

import random
from typing import Optional, List
from models import Board, Puzzle, Move
from engine import get_legal_moves, apply_move, evaluate_all_moves, is_game_over


def play_random_moves(board: Board, min_empty: int, max_empty: int, min_moves_per_side: int = 3) -> Board:
    """
    Play random legal moves until the board has the desired number of empty squares.
    
    Args:
        board: Starting board position
        min_empty: Minimum number of empty squares desired
        max_empty: Maximum number of empty squares desired
        min_moves_per_side: Minimum moves each side should have made
    
    Returns:
        Board with desired number of empty squares
    """
    current_board = board.copy()
    side = 'B'  # Black moves first in Othello
    move_counts = {'B': 0, 'W': 0}
    max_iterations = 1000  # Safety limit
    
    iteration = 0
    while iteration < max_iterations:
        empty_count = current_board.count_empty()
        
        # Check if we're in the desired range
        if min_empty <= empty_count <= max_empty:
            # Ensure both sides have made at least min_moves_per_side moves
            if move_counts['B'] >= min_moves_per_side and move_counts['W'] >= min_moves_per_side:
                break
        
        # If we have too many empty squares, keep playing
        if empty_count > max_empty:
            legal_moves = get_legal_moves(current_board, side)
            
            if legal_moves:
                # Make a random move
                move = random.choice(legal_moves)
                current_board = apply_move(current_board, move, side)
                move_counts[side] += 1
                side = 'W' if side == 'B' else 'B'
            else:
                # No legal moves, switch sides
                side = 'W' if side == 'B' else 'B'
                # If both sides have no moves, game is over
                if is_game_over(current_board):
                    break
        else:
            # We have fewer empty squares than desired, break
            break
        
        iteration += 1
    
    return current_board


def determine_side_to_move(board: Board, preferred_side: Optional[str] = None) -> Optional[str]:
    """
    Determine which side should move next.
    
    Args:
        board: Current board state
        preferred_side: Preferred side ('B' or 'W'), or None to auto-detect
    
    Returns:
        Side to move ('B' or 'W'), or None if game is over
    """
    if preferred_side:
        # Check if preferred side has legal moves
        if get_legal_moves(board, preferred_side):
            return preferred_side
        # If not, check opponent
        opponent = 'W' if preferred_side == 'B' else 'B'
        if get_legal_moves(board, opponent):
            return opponent
        return None  # Game over
    
    # Auto-detect: try black first (standard Othello)
    if get_legal_moves(board, 'B'):
        return 'B'
    if get_legal_moves(board, 'W'):
        return 'W'
    return None  # Game over


def has_unique_best_move(evaluated_moves: List[Move]) -> bool:
    """
    Check if there is a unique best move (no ties for first place).
    
    Args:
        evaluated_moves: List of Move objects with evaluations, sorted by evaluation (best first)
    
    Returns:
        True if there is exactly one best move
    """
    if not evaluated_moves:
        return False
    
    if len(evaluated_moves) == 1:
        return True
    
    # Check if the best move has a unique evaluation
    best_eval = evaluated_moves[0].evaluation
    if best_eval is None:
        return False
    
    # Check if second-best move has the same evaluation
    if len(evaluated_moves) > 1:
        second_eval = evaluated_moves[1].evaluation
        if second_eval is not None and second_eval == best_eval:
            return False
    
    return True


def generate_puzzle(
    min_empty: int = 4,
    max_empty: int = 10,
    side_to_move: Optional[str] = None,
    max_attempts: int = 50
) -> Optional[Puzzle]:
    """
    Generate a single Othello endgame puzzle with a unique best move.
    
    Args:
        min_empty: Minimum number of empty squares
        max_empty: Maximum number of empty squares
        side_to_move: Preferred side to move ('B' or 'W'), or None for auto-detect
        max_attempts: Maximum number of attempts before giving up
    
    Returns:
        Puzzle object if successful, None if failed after max_attempts
    """
    for attempt in range(max_attempts):
        # Start from initial position
        board = Board()
        
        # Play random moves to reach desired endgame state
        board = play_random_moves(board, min_empty, max_empty)
        
        # Determine side to move
        side = determine_side_to_move(board, side_to_move)
        if side is None:
            continue  # Game over, try again
        
        # Optionally add a few more random moves for variety
        # (This helps create more interesting positions)
        for _ in range(random.randint(0, 3)):
            legal_moves = get_legal_moves(board, side)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            board = apply_move(board, move, side)
            side = 'W' if side == 'B' else 'B'
        
        # Re-determine side to move after additional moves
        side = determine_side_to_move(board, side_to_move)
        if side is None:
            continue
        
        # Check empty count is still in range
        empty_count = board.count_empty()
        if not (min_empty <= empty_count <= max_empty):
            continue
        
        # Evaluate all legal moves
        evaluated_moves = evaluate_all_moves(board, side)
        
        if not evaluated_moves:
            continue  # No legal moves, try again
        
        # Check for unique best move
        if has_unique_best_move(evaluated_moves):
            best_move = evaluated_moves[0]
            return Puzzle(board, side, evaluated_moves, best_move)
    
    return None  # Failed to generate puzzle after max_attempts


def generate_puzzles(
    count: int,
    min_empty: int = 4,
    max_empty: int = 10,
    side_to_move: Optional[str] = None,
    max_attempts_per_puzzle: int = 50
) -> List[Puzzle]:
    """
    Generate multiple Othello endgame puzzles.
    
    Args:
        count: Number of puzzles to generate
        min_empty: Minimum number of empty squares
        max_empty: Maximum number of empty squares
        side_to_move: Preferred side to move ('B' or 'W'), or None for auto-detect
        max_attempts_per_puzzle: Maximum attempts per puzzle before giving up
    
    Returns:
        List of Puzzle objects
    """
    puzzles = []
    failed_count = 0
    max_total_failures = count * 10  # Safety limit
    
    while len(puzzles) < count and failed_count < max_total_failures:
        puzzle = generate_puzzle(min_empty, max_empty, side_to_move, max_attempts_per_puzzle)
        if puzzle:
            puzzles.append(puzzle)
        else:
            failed_count += 1
    
    return puzzles


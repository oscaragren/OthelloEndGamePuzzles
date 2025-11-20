"""Othello game engine with board logic and search algorithms."""

from typing import List, Tuple, Optional, Set
from models import Board, Move


# Directions: (row_delta, col_delta) for 8 directions
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]


def is_valid_position(row: int, col: int) -> bool:
    """Check if (row, col) is within board bounds."""
    return 0 <= row < 8 and 0 <= col < 8


def get_opponent(side: str) -> str:
    """Get opponent's piece color."""
    return 'W' if side == 'B' else 'B'


def find_flipped_pieces(board: Board, row: int, col: int, side: str) -> List[Tuple[int, int]]:
    """
    Find all pieces that would be flipped by placing a piece at (row, col).
    Returns list of (row, col) positions that would be flipped.
    """
    if board[row, col] != '.':
        return []  # Square must be empty
    
    opponent = get_opponent(side)
    flipped = []
    
    # Check each direction
    for dr, dc in DIRECTIONS:
        direction_flipped = []
        r, c = row + dr, col + dc
        
        # Move in direction, collecting opponent pieces
        while is_valid_position(r, c) and board[r, c] == opponent:
            direction_flipped.append((r, c))
            r, c = r + dr, c + dc
        
        # If we hit our own piece, all collected pieces are flipped
        if is_valid_position(r, c) and board[r, c] == side and direction_flipped:
            flipped.extend(direction_flipped)
    
    return flipped


def is_legal_move(board: Board, row: int, col: int, side: str) -> bool:
    """Check if placing a piece at (row, col) is legal for the given side."""
    return len(find_flipped_pieces(board, row, col, side)) > 0


def get_legal_moves(board: Board, side: str) -> List[Move]:
    """
    Get all legal moves for the given side.
    Returns list of Move objects (without evaluations).
    """
    moves = []
    for row in range(8):
        for col in range(8):
            if is_legal_move(board, row, col, side):
                moves.append(Move(row, col))
    return moves


def apply_move(board: Board, move: Move, side: str) -> Board:
    """
    Apply a move to the board and return a new board.
    Does not modify the original board.
    """
    new_board = board.copy()
    row, col = move.row, move.col
    
    # Place the piece
    new_board[row, col] = side
    
    # Flip all pieces in the flipped list
    flipped = find_flipped_pieces(board, row, col, side)
    for fr, fc in flipped:
        new_board[fr, fc] = side
    
    return new_board


def is_game_over(board: Board) -> bool:
    """Check if the game is over (no legal moves for either side)."""
    return len(get_legal_moves(board, 'B')) == 0 and len(get_legal_moves(board, 'W')) == 0


def get_score(board: Board, side: str) -> int:
    """
    Calculate final score difference from side's perspective.
    Returns: count(side) - count(opponent)
    """
    my_count = board.count_pieces(side)
    opponent_count = board.count_pieces(get_opponent(side))
    return my_count - opponent_count


def minimax(board: Board, side: str, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    """
    Minimax with alpha-beta pruning to evaluate a position.
    
    Args:
        board: Current board state
        side: The side to evaluate for (maximizing player)
        depth: Remaining search depth (0 = leaf node)
        alpha: Alpha value for pruning
        beta: Beta value for pruning
        maximizing: True if current player is maximizing
    
    Returns:
        Evaluation score from side's perspective (positive = good for side)
    """
    # Check if game is over
    if is_game_over(board):
        return get_score(board, side)
    
    # If we've reached max depth, evaluate current position
    if depth == 0:
        return get_score(board, side)
    
    current_side = side if maximizing else get_opponent(side)
    legal_moves = get_legal_moves(board, current_side)
    
    # If no legal moves, pass turn to opponent
    if not legal_moves:
        opponent_side = get_opponent(current_side)
        opponent_moves = get_legal_moves(board, opponent_side)
        
        # If opponent also has no moves, game over
        if not opponent_moves:
            return get_score(board, side)
        
        # Pass turn: opponent moves, but we're still evaluating from original side's perspective
        return minimax(board, side, depth - 1, alpha, beta, not maximizing)
    
    if maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            new_board = apply_move(board, move, current_side)
            eval_score = minimax(new_board, side, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            new_board = apply_move(board, move, current_side)
            eval_score = minimax(new_board, side, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        return min_eval


def evaluate_move(board: Board, move: Move, side: str, max_depth: int = 100) -> float:
    """
    Evaluate a move by searching to the end of the game.
    
    Args:
        board: Current board state
        move: Move to evaluate
        side: Side making the move
        max_depth: Maximum search depth (should be >= number of empty squares)
    
    Returns:
        Evaluation score from side's perspective after perfect play
    """
    new_board = apply_move(board, move, side)
    empty_count = new_board.count_empty()
    
    # Search to end of game (depth = number of remaining moves)
    # Add some buffer for passes
    search_depth = empty_count + 10
    
    return minimax(new_board, side, search_depth, float('-inf'), float('inf'), False)


def evaluate_all_moves(board: Board, side: str) -> List[Move]:
    """
    Evaluate all legal moves for the given side.
    
    Returns:
        List of Move objects with evaluations filled in, sorted by evaluation (best first)
    """
    legal_moves = get_legal_moves(board, side)
    
    # Calculate number of empty squares to determine search depth
    empty_count = board.count_empty()
    search_depth = empty_count + 10  # Buffer for passes
    
    evaluated_moves = []
    for move in legal_moves:
        evaluation = evaluate_move(board, move, side, search_depth)
        move.evaluation = evaluation
        evaluated_moves.append(move)
    
    # Sort by evaluation (descending)
    evaluated_moves.sort(key=lambda m: m.evaluation or float('-inf'), reverse=True)
    
    return evaluated_moves


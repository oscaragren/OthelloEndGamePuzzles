"""Data models for Othello puzzle generator."""

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Board:
    """Represents an 8x8 Othello board state."""
    grid: List[List[str]]  # 8x8 grid: '.' (empty), 'B' (black), 'W' (white)
    
    def __init__(self, grid: Optional[List[List[str]]] = None):
        """Initialize board. If no grid provided, creates standard starting position."""
        if grid is None:
            # Standard Othello starting position
            self.grid = [['.' for _ in range(8)] for _ in range(8)]
            self.grid[3][3] = 'W'
            self.grid[3][4] = 'B'
            self.grid[4][3] = 'B'
            self.grid[4][4] = 'W'
        else:
            self.grid = [row[:] for row in grid]  # Deep copy
    
    def __getitem__(self, pos: Tuple[int, int]) -> str:
        """Get piece at (row, col)."""
        row, col = pos
        return self.grid[row][col]
    
    def __setitem__(self, pos: Tuple[int, int], value: str):
        """Set piece at (row, col)."""
        row, col = pos
        self.grid[row][col] = value
    
    def count_empty(self) -> int:
        """Count number of empty squares."""
        return sum(row.count('.') for row in self.grid)
    
    def count_pieces(self, piece: str) -> int:
        """Count number of pieces of given color."""
        return sum(row.count(piece) for row in self.grid)
    
    def to_string(self) -> str:
        """Convert board to string representation."""
        return '\n'.join(''.join(row) for row in self.grid)
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        return Board(self.grid)


@dataclass
class Move:
    """Represents a move (row, col) with optional evaluation."""
    row: int
    col: int
    evaluation: Optional[float] = None
    
    def __str__(self) -> str:
        """Convert move to algebraic notation (e.g., 'd3')."""
        col_letter = chr(ord('a') + self.col)
        row_number = str(self.row + 1)
        return f"{col_letter}{row_number}"
    
    @classmethod
    def from_string(cls, move_str: str) -> 'Move':
        """Create move from algebraic notation (e.g., 'd3')."""
        col_letter = move_str[0].lower()
        row_number = int(move_str[1])
        col = ord(col_letter) - ord('a')
        row = row_number - 1
        return cls(row, col)


@dataclass
class Puzzle:
    """Represents an Othello endgame puzzle."""
    board: Board
    side_to_move: str  # 'B' or 'W'
    legal_moves: List[Move]  # All legal moves with evaluations
    best_move: Move  # The unique best move
    
    def to_dict(self) -> dict:
        """Convert puzzle to dictionary for JSON serialization."""
        return {
            'board': self.board.to_string(),
            'side_to_move': self.side_to_move,
            'legal_moves': [
                {
                    'move': str(move),
                    'row': move.row,
                    'col': move.col,
                    'evaluation': move.evaluation
                }
                for move in self.legal_moves
            ],
            'best_move': {
                'move': str(self.best_move),
                'row': self.best_move.row,
                'col': self.best_move.col,
                'evaluation': self.best_move.evaluation
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Puzzle':
        """Create puzzle from dictionary."""
        board_lines = data['board'].split('\n')
        board_grid = [list(line) for line in board_lines]
        board = Board(board_grid)
        
        legal_moves = [
            Move(m['row'], m['col'], m['evaluation'])
            for m in data['legal_moves']
        ]
        
        best_move_data = data['best_move']
        best_move = Move(
            best_move_data['row'],
            best_move_data['col'],
            best_move_data['evaluation']
        )
        
        return cls(board, data['side_to_move'], legal_moves, best_move)
    
    def pretty_print(self) -> str:
        """Return human-readable string representation."""
        lines = []
        lines.append("Board:")
        # Add column labels
        lines.append("  " + " ".join(chr(ord('a') + i) for i in range(8)))
        # Add board with row labels
        for i, row in enumerate(self.board.grid):
            lines.append(f"{i+1} {' '.join(row)}")
        lines.append(f"\nSide to move: {self.side_to_move}")
        lines.append(f"\nBest move for {self.side_to_move}: {self.best_move} (score {self.best_move.evaluation:+d})")
        lines.append("\nAll moves:")
        for move in sorted(self.legal_moves, key=lambda m: m.evaluation or -999, reverse=True):
            marker = "  <-- best" if move.row == self.best_move.row and move.col == self.best_move.col else ""
            lines.append(f"  {move}: {move.evaluation:+d}{marker}")
        return "\n".join(lines)


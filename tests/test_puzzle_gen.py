"""Tests for puzzle generation."""

import unittest
from models import Board, Puzzle
from puzzle_gen import (
    play_random_moves,
    determine_side_to_move,
    has_unique_best_move,
    generate_puzzle
)
from engine import get_legal_moves


class TestPuzzleGen(unittest.TestCase):
    """Test cases for puzzle generation."""
    
    def test_play_random_moves(self):
        """Test that random moves reduce empty squares."""
        board = Board()
        initial_empty = board.count_empty()
        
        # Play moves to get to 4-10 empty squares
        result_board = play_random_moves(board, min_empty=4, max_empty=10)
        final_empty = result_board.count_empty()
        
        # Should have fewer empty squares than initial
        self.assertLess(final_empty, initial_empty)
        # Should be in desired range (or close, if game ended early)
        self.assertLessEqual(final_empty, 10)
    
    def test_determine_side_to_move(self):
        """Test side-to-move detection."""
        board = Board()
        
        # From initial position, black should move
        side = determine_side_to_move(board)
        self.assertEqual(side, 'B')
        
        # After a move, should detect next side
        black_moves = get_legal_moves(board, 'B')
        if black_moves:
            new_board = board.copy()
            from engine import apply_move
            new_board = apply_move(new_board, black_moves[0], 'B')
            side = determine_side_to_move(new_board)
            # Should be white's turn (or black if white has no moves)
            self.assertIn(side, ['B', 'W'])
    
    def test_has_unique_best_move(self):
        """Test unique best move detection."""
        from models import Move
        
        # Case 1: Single move (unique)
        moves1 = [Move(0, 0, 5)]
        self.assertTrue(has_unique_best_move(moves1))
        
        # Case 2: Two moves with different evaluations (unique)
        moves2 = [Move(0, 0, 5), Move(1, 1, 3)]
        self.assertTrue(has_unique_best_move(moves2))
        
        # Case 3: Two moves with same evaluation (not unique)
        moves3 = [Move(0, 0, 5), Move(1, 1, 5)]
        self.assertFalse(has_unique_best_move(moves3))
        
        # Case 4: Empty list (not unique)
        moves4 = []
        self.assertFalse(has_unique_best_move(moves4))
    
    def test_generate_puzzle_basic(self):
        """Test basic puzzle generation."""
        puzzle = generate_puzzle(min_empty=4, max_empty=8, max_attempts=10)
        
        if puzzle:  # May fail if no unique best move found
            # Check puzzle structure
            self.assertIsInstance(puzzle, Puzzle)
            self.assertIn(puzzle.side_to_move, ['B', 'W'])
            self.assertGreater(len(puzzle.legal_moves), 0)
            self.assertIsNotNone(puzzle.best_move)
            
            # Check empty squares in range
            empty_count = puzzle.board.count_empty()
            self.assertGreaterEqual(empty_count, 4)
            self.assertLessEqual(empty_count, 8)
            
            # Check that best move is in legal moves
            best_in_legal = any(
                m.row == puzzle.best_move.row and m.col == puzzle.best_move.col
                for m in puzzle.legal_moves
            )
            self.assertTrue(best_in_legal)
            
            # Check that best move has highest evaluation
            if len(puzzle.legal_moves) > 1:
                best_eval = puzzle.best_move.evaluation
                for move in puzzle.legal_moves[1:]:
                    if move.evaluation is not None:
                        self.assertLessEqual(move.evaluation, best_eval)
    
    def test_puzzle_unique_best_move(self):
        """Test that generated puzzles have unique best moves."""
        puzzle = generate_puzzle(min_empty=4, max_empty=8, max_attempts=10)
        
        if puzzle:
            # Verify uniqueness
            evaluated_moves = puzzle.legal_moves
            if len(evaluated_moves) > 1:
                best_eval = evaluated_moves[0].evaluation
                second_eval = evaluated_moves[1].evaluation
                
                # Best move should have strictly better evaluation
                if best_eval is not None and second_eval is not None:
                    self.assertGreater(best_eval, second_eval)


if __name__ == '__main__':
    unittest.main()


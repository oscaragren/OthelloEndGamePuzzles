"""Command-line interface for Othello endgame puzzle generator."""

import argparse
import json
import sys
from puzzle_gen import generate_puzzles
from models import Puzzle


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Othello endgame puzzles with unique best moves.'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of puzzles to generate (default: 1)'
    )
    parser.add_argument(
        '--min-empty',
        type=int,
        default=4,
        help='Minimum number of empty squares (default: 4)'
    )
    parser.add_argument(
        '--max-empty',
        type=int,
        default=10,
        help='Maximum number of empty squares (default: 10)'
    )
    parser.add_argument(
        '--side',
        type=str,
        choices=['B', 'W'],
        default=None,
        help='Side to move (B or W). If not specified, auto-detect.'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path for JSON export (optional)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Print puzzles in human-readable format'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Open Pygame visualizer to display puzzles'
    )
    parser.add_argument(
        '--load',
        type=str,
        default=None,
        help='Load puzzles from JSON file instead of generating new ones'
    )
    
    args = parser.parse_args()
    
    # Load puzzles from file if requested
    if args.load:
        try:
            with open(args.load, 'r') as f:
                puzzles_data = json.load(f)
                puzzles = [Puzzle.from_dict(data) for data in puzzles_data]
            print(f"Loaded {len(puzzles)} puzzle(s) from {args.load}", file=sys.stderr)
        except FileNotFoundError:
            print(f"Error: File not found: {args.load}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.load}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Validate arguments
        if args.min_empty < 0 or args.max_empty < 0:
            print("Error: min-empty and max-empty must be non-negative", file=sys.stderr)
            sys.exit(1)
        
        if args.min_empty > args.max_empty:
            print("Error: min-empty must be <= max-empty", file=sys.stderr)
            sys.exit(1)
        
        if args.count < 1:
            print("Error: count must be at least 1", file=sys.stderr)
            sys.exit(1)
        
        # Generate puzzles
        print(f"Generating {args.count} puzzle(s)...", file=sys.stderr)
        puzzles = generate_puzzles(
            count=args.count,
            min_empty=args.min_empty,
            max_empty=args.max_empty,
            side_to_move=args.side
        )
        
        if not puzzles:
            print("Error: Failed to generate any puzzles. Try adjusting parameters.", file=sys.stderr)
            sys.exit(1)
        
        if len(puzzles) < args.count:
            print(
                f"Warning: Generated {len(puzzles)} puzzle(s) instead of {args.count}",
                file=sys.stderr
            )
    
    # Output puzzles
    if args.pretty:
        for i, puzzle in enumerate(puzzles, 1):
            print(f"\nPuzzle {i}")
            print("=" * 50)
            print(puzzle.pretty_print())
            print()
    else:
        # Simple text output
        for i, puzzle in enumerate(puzzles, 1):
            print(f"Puzzle {i}")
            print(f"Side to move: {puzzle.side_to_move}")
            print("Board:")
            print(puzzle.board.to_string())
            print(f"\nBest move: {puzzle.best_move} (score {puzzle.best_move.evaluation:+d})")
            print("All moves:")
            for move in puzzle.legal_moves:
                marker = " <-- best" if move.row == puzzle.best_move.row and move.col == puzzle.best_move.col else ""
                print(f"  {move}: {move.evaluation:+d}{marker}")
            print()
    
    # Export to JSON if requested
    if args.output:
        puzzles_data = [puzzle.to_dict() for puzzle in puzzles]
        with open(args.output, 'w') as f:
            json.dump(puzzles_data, f, indent=2)
        print(f"Exported {len(puzzles)} puzzle(s) to {args.output}", file=sys.stderr)
    
    # Visualize if requested
    if args.visualize:
        try:
            from visualizer import visualize_puzzles
            visualize_puzzles(puzzles)
        except ImportError:
            print("Error: Pygame not installed. Install it with: pip install pygame", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()


# Othello Endgame Puzzle Generator

A Python project that generates Othello (Reversi) endgame puzzles with unique best moves.

## Features

- Generates valid late-game Othello positions (4-10 empty squares)
- Ensures each puzzle has a unique best move
- Uses minimax with alpha-beta pruning for perfect play evaluation
- Exports puzzles to JSON format
- Human-readable puzzle output
- **Interactive Pygame visualizer** with move highlighting and evaluation display
- Comprehensive test suite

## Project Structure

```
.
├── models.py          # Data models (Board, Puzzle, Move)
├── engine.py          # Game engine (board logic, move generation, search)
├── puzzle_gen.py      # Puzzle generation algorithms
├── main.py            # Command-line interface
├── visualizer.py      # Pygame-based puzzle visualizer
├── tests/             # Test suite
│   ├── test_engine.py
│   └── test_puzzle_gen.py
└── requirements.txt   # Dependencies (pygame for visualization)
```

## Installation

Python 3.8+ is required. For visualization features, Pygame is needed.

```bash
# Clone or download the project
cd OthelloEndGamePuzzles

# Install dependencies (optional, for visualization)
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a single puzzle:

```bash
python main.py
```

### Generate Multiple Puzzles

```bash
python main.py --count 5
```

### Control Endgame Depth

```bash
python main.py --count 5 --min-empty 4 --max-empty 8
```

### Pretty Print Output

```bash
python main.py --count 3 --pretty
```

### Export to JSON

```bash
python main.py --count 10 --output puzzles.json
```

### Specify Side to Move

```bash
python main.py --side B --count 5
```

### Visualize Puzzles

Open an interactive Pygame visualizer:

```bash
# Generate and visualize puzzles
python main.py --count 5 --visualize

# Load and visualize puzzles from JSON file
python main.py --load puzzles.json --visualize
```

### Complete Example

```bash
python main.py --count 5 --min-empty 4 --max-empty 8 --output puzzles.json --pretty --visualize
```

## Output Format

### Human-Readable Format (--pretty)

```
Puzzle 1
==================================================
Board:
  a b c d e f g h
1 . . . . . . . .
2 . . . . . . . .
3 . . . W B . . .
4 . . . W W B . .
5 . . . B W . . .
6 . . . . . . . .
7 . . . . . . . .
8 . . . . . . . .

Side to move: B

Best move for B: d3 (score +4)

All moves:
  d3: +4  <-- best
  c3: +1
  f4:  0
```

### JSON Format

The JSON export includes:
- Board state (string representation)
- Side to move
- All legal moves with evaluations
- Best move identification

## Running Tests

```bash
python -m unittest discover tests
```

Or run individual test files:

```bash
python -m unittest tests.test_engine
python -m unittest tests.test_puzzle_gen
```

## Visualization Features

The Pygame visualizer provides an interactive way to explore puzzles:

- **Visual Board**: Green Othello board with black and white pieces
- **Move Highlighting**: 
  - Yellow highlights for all legal moves
  - Green highlight for the best move
  - Orange highlight on hover
- **Information Panel**: Shows puzzle details, all moves with evaluations, and best move
- **Navigation**: Use arrow keys to navigate between multiple puzzles
- **Interactive**: Click on moves or hover to see details

## How It Works

1. **Puzzle Generation**: Starts from the initial Othello position and plays random legal moves until reaching the desired number of empty squares (4-10).

2. **Move Evaluation**: Uses minimax with alpha-beta pruning to search to the end of the game, evaluating each position based on final disc count.

3. **Uniqueness Check**: Verifies that exactly one move has the highest evaluation (no ties).

4. **Validation**: Each generated puzzle is validated to ensure:
   - Valid board position
   - Unique best move exists
   - All moves are legal
   - Evaluations are correct

## Code Quality

- Type hints throughout
- Comprehensive docstrings
- Clean separation of concerns
- Well-commented algorithms
- Test coverage for core functionality

## License

This project is provided as-is for educational and puzzle generation purposes.

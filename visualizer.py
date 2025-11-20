"""Pygame-based visualizer for Othello puzzles."""

import pygame
from typing import List, Optional, Tuple
from models import Puzzle, Move


# Colors
BOARD_COLOR = (34, 139, 34)  # Forest green
GRID_COLOR = (0, 100, 0)  # Dark green
BLACK_PIECE = (0, 0, 0)
WHITE_PIECE = (255, 255, 255)
LEGAL_MOVE_HIGHLIGHT = (255, 255, 0, 128)  # Yellow with transparency
BEST_MOVE_HIGHLIGHT = (0, 255, 0, 180)  # Green with transparency
HOVER_HIGHLIGHT = (255, 200, 0, 150)  # Orange with transparency
TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (20, 20, 20)

# Board dimensions
BOARD_SIZE = 600
CELL_SIZE = BOARD_SIZE // 8
MARGIN = 50
INFO_PANEL_WIDTH = 300
WINDOW_WIDTH = BOARD_SIZE + MARGIN * 2 + INFO_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE + MARGIN * 2


class PuzzleVisualizer:
    """Visualizer for displaying Othello puzzles with Pygame."""
    
    def __init__(self, puzzles: List[Puzzle]):
        """Initialize visualizer with a list of puzzles."""
        self.puzzles = puzzles
        self.current_puzzle_index = 0
        self.hovered_cell: Optional[Tuple[int, int]] = None
        self.selected_move: Optional[Move] = None
        
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Othello Puzzle Visualizer")
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.clock = pygame.time.Clock()
    
    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to board cell (row, col)."""
        x, y = pos
        x -= MARGIN
        y -= MARGIN
        
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            return (row, col)
        return None
    
    def get_cell_rect(self, row: int, col: int) -> pygame.Rect:
        """Get pygame Rect for a board cell."""
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    def draw_board(self):
        """Draw the Othello board."""
        # Draw board background
        board_rect = pygame.Rect(MARGIN, MARGIN, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect)
        
        # Draw grid lines
        for i in range(9):
            # Vertical lines
            x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (x, MARGIN), (x, MARGIN + BOARD_SIZE), 2)
            # Horizontal lines
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (MARGIN, y), (MARGIN + BOARD_SIZE, y), 2)
        
        # Draw column labels (a-h)
        for i in range(8):
            label = chr(ord('a') + i)
            x = MARGIN + i * CELL_SIZE + CELL_SIZE // 2
            text = self.small_font.render(label, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(x, MARGIN - 15))
            self.screen.blit(text, text_rect)
        
        # Draw row labels (1-8)
        for i in range(8):
            label = str(i + 1)
            y = MARGIN + i * CELL_SIZE + CELL_SIZE // 2
            text = self.small_font.render(label, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(MARGIN - 15, y))
            self.screen.blit(text, text_rect)
    
    def draw_pieces(self, puzzle: Puzzle):
        """Draw pieces on the board."""
        for row in range(8):
            for col in range(8):
                piece = puzzle.board[row, col]
                if piece != '.':
                    rect = self.get_cell_rect(row, col)
                    center = rect.center
                    radius = CELL_SIZE // 2 - 5
                    
                    # Draw piece
                    color = BLACK_PIECE if piece == 'B' else WHITE_PIECE
                    pygame.draw.circle(self.screen, color, center, radius)
                    # Draw border
                    pygame.draw.circle(self.screen, GRID_COLOR, center, radius, 2)
    
    def draw_highlights(self, puzzle: Puzzle):
        """Draw highlights for legal moves and best move."""
        # Draw legal move highlights
        for move in puzzle.legal_moves:
            rect = self.get_cell_rect(move.row, move.col)
            is_best = (move.row == puzzle.best_move.row and 
                      move.col == puzzle.best_move.col)
            
            # Use different color for best move
            if is_best:
                highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, BEST_MOVE_HIGHLIGHT, 
                                (0, 0, CELL_SIZE, CELL_SIZE))
                self.screen.blit(highlight_surface, rect.topleft)
            else:
                highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, LEGAL_MOVE_HIGHLIGHT, 
                                (0, 0, CELL_SIZE, CELL_SIZE))
                self.screen.blit(highlight_surface, rect.topleft)
        
        # Draw hover highlight
        if self.hovered_cell:
            row, col = self.hovered_cell
            # Check if it's a legal move
            is_legal = any(m.row == row and m.col == col for m in puzzle.legal_moves)
            if is_legal:
                rect = self.get_cell_rect(row, col)
                highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, HOVER_HIGHLIGHT, 
                                (0, 0, CELL_SIZE, CELL_SIZE))
                self.screen.blit(highlight_surface, rect.topleft)
    
    def draw_info_panel(self, puzzle: Puzzle):
        """Draw information panel on the right side."""
        panel_x = BOARD_SIZE + MARGIN * 2
        panel_y = MARGIN
        panel_width = INFO_PANEL_WIDTH - MARGIN
        
        # Background for info panel
        info_rect = pygame.Rect(panel_x, panel_y, panel_width, WINDOW_HEIGHT - MARGIN * 2)
        pygame.draw.rect(self.screen, (40, 40, 40), info_rect)
        pygame.draw.rect(self.screen, (80, 80, 80), info_rect, 2)
        
        y_offset = 20
        
        # Title
        title = self.font.render("Othello Puzzle", True, TEXT_COLOR)
        self.screen.blit(title, (panel_x + 10, y_offset))
        y_offset += 40
        
        # Puzzle number
        puzzle_text = f"Puzzle {self.current_puzzle_index + 1}/{len(self.puzzles)}"
        text = self.small_font.render(puzzle_text, True, TEXT_COLOR)
        self.screen.blit(text, (panel_x + 10, y_offset))
        y_offset += 30
        
        # Side to move
        side_text = f"Side to move: {'Black' if puzzle.side_to_move == 'B' else 'White'}"
        text = self.font.render(side_text, True, TEXT_COLOR)
        self.screen.blit(text, (panel_x + 10, y_offset))
        y_offset += 40
        
        # Best move
        best_text = f"Best move: {puzzle.best_move}"
        text = self.font.render(best_text, True, (0, 255, 0))
        self.screen.blit(text, (panel_x + 10, y_offset))
        y_offset += 30
        
        best_eval_text = f"Score: {puzzle.best_move.evaluation:+d}"
        text = self.small_font.render(best_eval_text, True, TEXT_COLOR)
        self.screen.blit(text, (panel_x + 10, y_offset))
        y_offset += 40
        
        # All moves
        moves_title = self.font.render("All Moves:", True, TEXT_COLOR)
        self.screen.blit(moves_title, (panel_x + 10, y_offset))
        y_offset += 30
        
        # Sort moves by evaluation
        sorted_moves = sorted(puzzle.legal_moves, 
                            key=lambda m: m.evaluation or -999, 
                            reverse=True)
        
        for move in sorted_moves[:10]:  # Show top 10 moves
            is_best = (move.row == puzzle.best_move.row and 
                      move.col == puzzle.best_move.col)
            color = (0, 255, 0) if is_best else TEXT_COLOR
            move_text = f"  {move}: {move.evaluation:+d}"
            if is_best:
                move_text += " (BEST)"
            text = self.small_font.render(move_text, True, color)
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 25
        
        if len(sorted_moves) > 10:
            more_text = f"  ... and {len(sorted_moves) - 10} more"
            text = self.small_font.render(more_text, True, TEXT_COLOR)
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 25
        
        y_offset += 20
        
        # Hovered move info
        if self.hovered_cell:
            row, col = self.hovered_cell
            hovered_move = next(
                (m for m in puzzle.legal_moves if m.row == row and m.col == col),
                None
            )
            if hovered_move:
                hover_text = f"Hovered: {hovered_move}"
                text = self.small_font.render(hover_text, True, (255, 200, 0))
                self.screen.blit(text, (panel_x + 10, y_offset))
                y_offset += 25
                hover_eval_text = f"Score: {hovered_move.evaluation:+d}"
                text = self.small_font.render(hover_eval_text, True, (255, 200, 0))
                self.screen.blit(text, (panel_x + 10, y_offset))
        
        y_offset += 40
        
        # Instructions
        instructions = [
            "Controls:",
            "← → : Navigate puzzles",
            "ESC : Exit",
            "Click: Select move"
        ]
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (150, 150, 150))
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 20
    
    def run(self):
        """Main visualization loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        self.current_puzzle_index = max(0, self.current_puzzle_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.current_puzzle_index = min(len(self.puzzles) - 1, 
                                                        self.current_puzzle_index + 1)
                elif event.type == pygame.MOUSEMOTION:
                    cell = self.get_cell_from_pos(event.pos)
                    self.hovered_cell = cell
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        cell = self.get_cell_from_pos(event.pos)
                        if cell:
                            puzzle = self.puzzles[self.current_puzzle_index]
                            clicked_move = next(
                                (m for m in puzzle.legal_moves 
                                 if m.row == cell[0] and m.col == cell[1]),
                                None
                            )
                            if clicked_move:
                                self.selected_move = clicked_move
            
            # Clear screen
            self.screen.fill(BACKGROUND_COLOR)
            
            # Draw everything
            puzzle = self.puzzles[self.current_puzzle_index]
            self.draw_board()
            self.draw_highlights(puzzle)
            self.draw_pieces(puzzle)
            self.draw_info_panel(puzzle)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def visualize_puzzles(puzzles: List[Puzzle]):
    """Main entry point for visualizing puzzles."""
    import sys
    if not puzzles:
        print("No puzzles to visualize.", file=sys.stderr)
        return
    
    visualizer = PuzzleVisualizer(puzzles)
    visualizer.run()


if __name__ == '__main__':
    import sys
    import json
    from models import Puzzle
    
    # Example: load from JSON file if provided
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            puzzles_data = json.load(f)
            puzzles = [Puzzle.from_dict(data) for data in puzzles_data]
            visualize_puzzles(puzzles)
    else:
        print("Usage: python visualizer.py <puzzles.json>")
        print("Or use: python main.py --visualize")


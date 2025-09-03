import os

from solver_algorithms import *
from sudoku_elements import Sudoku


class SudokuSolver:
    def __init__(self, filename: str, strategy: Strategy, start: float = None, end: float = None):
        self._unsolved_puzzle = self.read_puzzle_file(filename)
        self._strategy = strategy
        self._puzzle_start = start
        self._puzzle_end = end

        self.sudoku = Sudoku(self._unsolved_puzzle)

    def read_puzzle_file(self, puzzle_file: str) -> list[list[int]]:
        if not os.path.isfile(puzzle_file):
            raise FileNotFoundError(f"File not found. Check file is in the expected location: {puzzle_file}")

        puzzle = []
        with open(puzzle_file) as f:
            for line in f:
                format_line = line.rstrip().split(',')
                puzzle.append([int(format_line[i]) for i in range(len(format_line))])
        
        return puzzle
    
    @property
    def unsolved_puzzle(self) -> list[list[int]]:
        return self._unsolved_puzzle
    
    @property
    def strategy(self) -> Strategy:
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy) -> None:
        self._strategy = strategy
    
    @property
    def puzzle_start(self) -> float:
        return self._puzzle_start
    
    @puzzle_start.setter
    def puzzle_start(self, time: float) -> None:
        if time < 0:
            raise ValueError("Enter a valid puzzle start time")
        self._puzzle_start = time
            
    @property
    def puzzle_end(self) -> float:
        return self._puzzle_end
    
    @puzzle_end.setter
    def puzzle_end(self, time: float) -> None:
        if time < 0:
            raise ValueError("Enter a valid puzzle end time")
        if time < self._puzzle_start:
            raise ValueError("End time is less than start time.")
        self._puzzle_end = time

    def __repr__(self):
        """
        Display puzzle in a readable format.
        """
        output_str = ""
        puzzle = self.sudoku.puzzle
        for r in range(len(puzzle)): # loop over rows
            if r in [3, 6]:
                sep_str = "-" * 9 + "+"
                full_str = sep_str * 3
                output_str += full_str[:-1]
                output_str += "\n"
            for c in range(len(puzzle)): # assumes sudoku is square
                if c in [3, 6]:
                    output_str += "|"

                output = puzzle[r][c]
                if output == 0:
                    output = "-"
                output_str += f" {output} "
            
            output_str += "\n"
            
        return output_str
    
    def reset_sudoku(self) -> None:
        """
        Reset to the original puzzle and zero the timers
        """
        # reset sudoku attribute
        self.sudoku.reset(self._unsolved_puzzle)

        # reset timings
        self._puzzle_start = 0
        self._puzzle_end = 0

    def solve_puzzle(self) -> bool:
        """
        Solve loaded sudoku with the set strategy
        """
        result = self._strategy.solve(self.sudoku)

        # TODO handle result - is it solved?


if __name__ == "__main__":
    sudoku = SudokuSolver("puzzle_hard.txt", RecursiveSolver())
    print(sudoku)
    sudoku.solve_puzzle()
    print(sudoku)
    sudoku.reset_sudoku()

    sudoku.strategy = ImprovedRecursiveSolver()
    sudoku.solve_puzzle()
    print(sudoku)
    sudoku.reset_sudoku()

    sudoku.strategy = PersonalSolver()
    sudoku.solve_puzzle()
    print(sudoku)

import os
import copy

from solver_algorithms import *

# temporary globals
PUZZLE_FILE = "puzzle_hard.txt"
CHUNK_SIZE = 3

class PotentialEntries:
    def __init__(self):
        self.valid_nums = [i for i in range (1, 10)]

    def remove_invalid(self, num) -> None:
        if num not in self.valid_nums:
            return

        self.valid_nums.remove(num)

    def reset_valid_nums(self) -> None:
        self.valid_nums = [i for i in range (1, 10)]

class SudokuPuzzle:
    def __init__(self, filename: str, strategy: Strategy, start: float = None, end: float = None):
        self._unsolved_puzzle = self.read_puzzle_file(filename)
        self._strategy = strategy
        self._puzzle_start = start
        self._puzzle_end = end

        self.puzzle = copy.deepcopy(self._unsolved_puzzle)
        self.size = len(self.puzzle) # assuming puzzle is square 
        self.cell_options = [[PotentialEntries() for _ in range(self.size)] for _ in range(self.size)]

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
    def stategy(self, strategy) -> None:
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
        for r in range(len(self.puzzle)): # loop over rows
            if r in [3, 6]:
                sep_str = "-" * 9 + "+"
                full_str = sep_str * 3
                output_str += full_str[:-1]
            for c in range(len(self.puzzle)): # assumes sudoku is square
                if c in [3, 6]:
                    # print("|", end="")
                    output_str += "|"

                output = self.puzzle[r][c]
                if output == 0:
                    output = "-"
                # print(f" {output} ", end="")
                output_str += f" {output} "
            
            output_str += "\n"
            
        return output_str
    
    def reset_sudoku(self) -> None:
        """
        Reset to the original puzzle and zero the timers
        """
        original = self._unsolved_puzzle
        self.puzzle = copy.deepcopy(original)

        for r in range(self.size):
            for c in range(self.size):
                self.cell_options[r][c].reset_valid_nums()

        # reset timings as well
        self.set_start_time(0)
        self.set_end_time(0)

    def remove_element_valid_nums(self, row_index: int, col_index: int, value: int) -> None:
        """ 
        When a new value is added to a cell, the related row, column and chunk cells valid entries lists have to be updated 
        """
        for r in range(self.size):
            self.cell_options[r][col_index].remove_invalid(value)

        for c in range(self.size):
            self.cell_options[row_index][c].remove_invalid(value)

        row = (row_index // CHUNK_SIZE) * 3
        col = (col_index // CHUNK_SIZE) * 3
        for r in range(row, row+3):
            for c in range(col, col+3):
                self.cell_options[r][c].remove_invalid(value)

    def update_valid_entries(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                # only update valid_nums if the cell is empty
                if self.puzzle[r][c] != 0:
                    continue

                options = self.cell_options[r][c]
                options.valid_nums = [value for value in options.valid_nums if self.check_valid_entry(value, r, c)]
                # only one valid option so add into puzzle
                if len(options.valid_nums) == 1: 
                    cell_value = options.valid_nums[0]
                    self.puzzle[r][c] = cell_value
                    self.remove_element_valid_nums(r, c, cell_value)

    def solve_puzzle(self) -> bool:
        """
        Solve loaded sudoku with the set strategy
        """
        result = self._strategy.solve(self.puzzle)
        print(result)


if __name__ == "__main__":
    sudoku = SudokuPuzzle("puzzle_hard.txt", RecursiveSolver())
    print(sudoku)

    sudoku.solve_puzzle()
    sudoku.strategy = ImprovedRecursiveSolver()

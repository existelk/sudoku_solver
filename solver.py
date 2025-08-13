import os
import copy
import time
import sys
from collections import Counter

"""
[
[[1,2,3],    [4,5,6],    [7,8,9]],
[[11,12,13], [14,15,16], [17,18,19]],
[[21,22,23], [24,25,26], [27,28,29]]
]
"""

# temporary globals
PUZZLE_FILE = "puzzle.txt"
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

class Sudoku:
    def __init__(self, puzzle_matrix: list, start: float = None, end: float = None):
        self._unsolved_puzzle = puzzle_matrix
        self.puzzle = copy.deepcopy(puzzle_matrix)
        self._puzzle_start = start
        self._puzzle_end = end

        self.size = len(puzzle_matrix)
        self.cell_options = [[PotentialEntries() for _ in range(self.size)] for _ in range(self.size)]

    def pretty_print(self, puzzle: list) -> None:
        """
        Display puzzle in a readable format.
        """
        for r in range(len(puzzle)): # loop over rows
            if r in [3, 6]:
                sep_str = "-" * 9 + "+"
                full_str = sep_str * 3
                print(full_str[:-1])
            for c in range(len(puzzle)): # assumes sudoku is square
                if c in [3, 6]:
                    print("|", end="")

                output = puzzle[r][c]
                if output == 0:
                    output = "-"
                print(f" {output} ", end="")
            print("\n")

    def get_unsolved_puzzle(self):
        return self._unsolved_puzzle

    def set_start_time(self, start: float) -> None:
        self._puzzle_start = start

    def set_end_time(self, end: float) -> None:
        self._puzzle_end = end
    
    def determine_calculation_time(self) -> float:
        return (self._puzzle_end - self._puzzle_start)
    
    def find_empty(self) -> tuple[int, int]:
        for r in range(self.size):
            for c in range(self.size):
                if (self.puzzle[r][c] == 0):
                    return r,c
                
        return -1,-1
    
    def check_valid_entry(self, value: str, row: int, col: int) -> int:
        """
        Check value is a valid option for cell.
        """
        puzzle = self.puzzle
        puzzle_size = len(puzzle)

        # check value is valid for row
        row_valid = all([value != puzzle[row][c] for c in range(puzzle_size)])
        if not row_valid:
            return 0

        # check value is valid for column
        col_valid = all([value != puzzle[r][col] for r in range(puzzle_size)])
        if not col_valid:
            return 0

        # check value is valid for square
        r_corner = (row // CHUNK_SIZE) * 3
        c_corner = (col // CHUNK_SIZE) * 3
        for x in range(r_corner, r_corner+3):
            for y in range(c_corner, c_corner+3):
                if puzzle[x][y] == str(value):
                    return 0
        
        return 1
    
    def reset_puzzle(self) -> None:
        original = self.get_unsolved_puzzle()
        self.puzzle = copy.deepcopy(original)

        for r in range(self.size):
            for c in range(self.size):
                self.cell_options[r][c].reset_valid_nums()

        # reset timings as well
        self.set_start_time(0)
        self.set_end_time(0)

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
    
    def remove_element_valid_nums(self, row_index: int, col_index: int, value: int) -> None:
        """ 
        When a new value is added to a cell, the related row and column cells valid entries has to be updated 
        """
        for r in range(self.size):
            self.cell_options[r][col_index].remove_invalid(value)

        for c in range(self.size):
            self.cell_options[row_index][c].remove_invalid(value)

    def row_solve_entries(self, row_index: int) -> None:
        combined_possible_entries = []
        history = {}

        # iterate along the row
        for c in range(self.size):
            if self.puzzle[row_index][c] == 0:
                options = self.cell_options[row_index][c]
                combined_possible_entries += options.valid_nums
                history[c] = options.valid_nums # keep a history of valid_nums and associated column index to avoid another loop later
        
        combined_possible_entries.sort()
        counter = Counter(combined_possible_entries)
        # if a possible value only appears for one cell in a row, it can be assigned to that cell
        single_entries = [key for key, value in counter.items() if value == 1]

        if len(single_entries) == 0:
            return
        
        for key, value in history.items():
            for elem in single_entries:
                if elem not in value:
                    continue

                self.puzzle[row_index][key] = elem
                single_entries.remove(elem)
                if len(single_entries) == 0:
                    break

    def col_solve_entries(self, col_index: int) -> None:
        combined_possible_entries = []
        history = {}
        
        # iterate along the row
        for r in range(self.size):
            if self.puzzle[r][col_index] == 0:
                options = self.cell_options[r][col_index]
                combined_possible_entries += options.valid_nums
                history[r] = options.valid_nums # keep a history of valid_nums and associated column index to avoid another loop later
        
        combined_possible_entries.sort()
        counter = Counter(combined_possible_entries)
        # if a possible value only appears for one cell in a row, it can be assigned to that cell
        single_entries = [key for key, value in counter.items() if value == 1]

        if len(single_entries) == 0:
            return
        
        for key, value in history.items():
            for elem in single_entries:
                if elem not in value:
                    continue

                self.puzzle[key][col_index] = elem
                single_entries.remove(elem)
                if len(single_entries) == 0:
                    break


def solve_sudoku_original(puzzle: Sudoku, r: int = 0, c: int = 0) -> bool:
    r, c = puzzle.find_empty()
    if r == -1:
        return True
    
    for value in range(1, 10):
        if puzzle.check_valid_entry(value, r, c):
            puzzle.puzzle[r][c] = value
            if solve_sudoku_original(puzzle, r, c):
                return True
            
            puzzle.puzzle[r][c] = 0

    return False

def improved_solve_sudoku(puzzle: Sudoku, r: int = 0, c: int = 0) -> bool:
    r, c = puzzle.find_empty()
    if r == -1:
        return True
    
    values = puzzle.cell_options[r][c].valid_nums
    for value in values:
        if puzzle.check_valid_entry(value, r, c):
            puzzle.puzzle[r][c] = value
            if improved_solve_sudoku(puzzle, r, c):
                return True
            
            puzzle.puzzle[r][c] = 0
    
    return False

def personal_way_to_solve(sudoku : Sudoku) -> None:
    # run valid_entries twice as some cells will be solved on the first pass
    for _ in range(2):
        sudoku.update_valid_entries()
    sudoku.pretty_print(sudoku.puzzle)

    # check if any rows can be solved
    for r in range(sudoku.size):
        sudoku.row_solve_entries(r)

    # check if any columns can be solved
    for c in range(sudoku.size):
        sudoku.col_solve_entries(c)


def read_sudoku_puzzle(puzzle_file: str) -> Sudoku:
    """
    Read sudoku from input text file. 0 represents an empty space.
    """
    if not os.path.isfile(puzzle_file):
        print(f"File not found. Check file is in the expected location: {puzzle_file}")
        sys.exit(1)

    puzzle = []
    with open("puzzle.txt") as f:
        for line in f:
            format_line = line.rstrip().split(',')
            puzzle.append([int(format_line[i]) for i in range(len(format_line))])
    
    return Sudoku(puzzle)

def main() -> None:
    sudoku_puzzle = read_sudoku_puzzle(PUZZLE_FILE)
    sudoku_puzzle.pretty_print(sudoku_puzzle.puzzle)
    print("\n\n")

    # solve sudoku with standard recursion and backtracking
    # start = time.perf_counter()
    # sudoku_puzzle.set_start_time(start) # using perf_countter as it provides a higher resolution time
    # solve_sudoku_original(sudoku_puzzle)

    # end = time.perf_counter() 
    # sudoku_puzzle.set_end_time(end)
    # sol_length = sudoku_puzzle.determine_calculation_time()

    # print(f'The sudoku puzzle took {sol_length} seconds to find the solution: \n')
    # sudoku_puzzle.pretty_print(sudoku_puzzle.puzzle)

    # # solve the sudoku with same method but only testing valid values in cells
    # sudoku_puzzle.reset_puzzle()
    # start = time.perf_counter()
    # sudoku_puzzle.set_start_time(start)

    # sudoku_puzzle.update_valid_entries()
    # improved_solve_sudoku(sudoku_puzzle)

    # end = time.perf_counter() 
    # sudoku_puzzle.set_end_time(end)
    # sol_length = sudoku_puzzle.determine_calculation_time()
    
    # print(f'The sudoku puzzle took {sol_length} seconds to find the solution: \n')
    # sudoku_puzzle.pretty_print(sudoku_puzzle.puzzle)

    # solve the sudoku my way
    # sudoku_puzzle.reset_puzzle()
    start = time.perf_counter()
    sudoku_puzzle.set_start_time(start)

    personal_way_to_solve(sudoku_puzzle)

    end = time.perf_counter() 
    sudoku_puzzle.set_end_time(end)
    sol_length = sudoku_puzzle.determine_calculation_time()
    
    print(f'The sudoku puzzle took {sol_length} seconds to find the solution: \n')
    sudoku_puzzle.pretty_print(sudoku_puzzle.puzzle)

if __name__ == "__main__":
    main()
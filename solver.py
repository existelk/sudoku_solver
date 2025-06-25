import os
import copy
import time

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

class PotentialList:
    def __init__(self):
        self.valid_nums = [i for i in range (1, 10)]

    def remove_invalid(self, num) -> None:
        self.valid_nums.remove(num)


class Sudoku:
    def __init__(self, puzzle_matrix : list, start : float = None, end : float = None):
        self._unsolved_puzzle = puzzle_matrix
        self.puzzle = copy.deepcopy(puzzle_matrix)
        self._puzzle_start = start
        self._puzzle_end = end

        self.size = len(puzzle_matrix)
        self.cell_options = [[PotentialList() for _ in range(self.size)] for _ in range(self.size)]

    def pretty_print(self, puzzle : list) -> None:
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

    def set_start_time(self, start : float) -> None:
        self._start = start

    def set_end_time(self, end : float) -> None:
        self._end = end
    
    def determine_calculation_time(self) -> float:
        return (self._end - self._start)
    
    def find_empty(self):
        for r in range(self.size):
            for c in range(self.size):
                if (self.puzzle[r][c] == 0):
                    return r,c
                
        return -1,-1
    
    def check_valid_entry(self, value : str, row : int, col : int) -> int:
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

        # reset timings as well
        self.set_start_time(0)
        self.set_end_time(0)

    def update_valid_entries(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                # only update valid_nums if the cell is empty
                if self.puzzle[r][c] == 0:
                    options = self.cell_options[r][c]
                    options.valid_nums = [value for value in options.valid_nums if self.check_valid_entry(value, r, c)]

                    # only one valid option so add into puzzle
                    if len(options.valid_nums) == 1: 
                        self.puzzle[r][c] = options.valid_nums[0]


def solve_sudoku_original(puzzle : Sudoku, r : int = 0, c : int = 0) -> bool:
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

def improved_solve_sudoku(puzzle : Sudoku, r : int = 0, c : int = 0) -> bool:
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


def read_sudoku_puzzle(puzzle_file : str) -> Sudoku:
    """
    Read sudoku from input text file. 0 represents an empty space.
    """
    if not os.path.isfile(puzzle_file):
        print(f"File not found. Check file is in the expected location: {puzzle_file}")
        exit(1)

    puzzle = []
    with open("puzzle.txt") as f:
        for line in f:
            format_line = line.rstrip().split(',')
            puzzle.append([int(format_line[i]) for i in range(len(format_line))])
    
    return Sudoku(puzzle)

def main() -> None:
    sudoku_puzzle = read_sudoku_puzzle(PUZZLE_FILE)

    # solve sudoku with standard recursion and backtracking
    start = time.perf_counter()
    sudoku_puzzle.set_start_time(start) # using perf_countter as it provides a higher resolution time
    solve_sudoku_original(sudoku_puzzle)

    end = time.perf_counter() 
    sudoku_puzzle.set_end_time(end)
    sol_length = sudoku_puzzle.determine_calculation_time()

    print(f'The sudoku puzzle took {sol_length} seconds to find the solution: \n')
    sudoku_puzzle.pretty_print(sudoku_puzzle.puzzle)

    # solve the sudoku with same method but only testing valid values in cells
    sudoku_puzzle.reset_puzzle()
    start = time.perf_counter()
    sudoku_puzzle.set_start_time(start)

    sudoku_puzzle.update_valid_entries()
    improved_solve_sudoku(sudoku_puzzle)

    end = time.perf_counter() 
    sudoku_puzzle.set_end_time(end)
    sol_length = sudoku_puzzle.determine_calculation_time()
    
    print(f'The sudoku puzzle took {sol_length} seconds to find the solution: \n')
    sudoku_puzzle.pretty_print(sudoku_puzzle.puzzle)


if __name__ == "__main__":
    main()
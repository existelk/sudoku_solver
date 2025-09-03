from abc import ABC, abstractmethod
from collections import Counter

from sudoku_elements import Sudoku

CHUNK_SIZE = 3

class Strategy(ABC):
    def find_empty(self, puzzle: list[list[int]]) -> tuple[int, int]:
        for r in range(len(puzzle)):
            for c in range(len(puzzle)):
                if (puzzle[r][c] == 0):
                    return r,c
                
        return -1,-1
    
    def check_valid_entry(self, puzzle: list[list[int]], size: int, value: str, row: int, col: int) -> int:
        """
        Check value is a valid option for cell.
        """

        # check value is valid for row
        row_valid = all([value != puzzle[row][c] for c in range(size)])
        if not row_valid:
            return 0

        # check value is valid for column
        col_valid = all([value != puzzle[r][col] for r in range(size)])
        if not col_valid:
            return 0

        # check value is valid for square
        r_corner = (row // CHUNK_SIZE) * 3
        c_corner = (col // CHUNK_SIZE) * 3
        for x in range(r_corner, r_corner+3):
            for y in range(c_corner, c_corner+3):
                if puzzle[x][y] == value:
                    return 0
        
        return 1
    
    @abstractmethod
    def solve(self, sudoku: Sudoku, r: int = 0, c: int = 0) -> bool:
        """
        Solve the sudoku puzzle. Optionally, r and c can specify a starting cell.
        """
        pass

class RecursiveSolver(Strategy):
    def solve(self, sudoku: Sudoku, r: int = 0, c: int = 0) -> bool:
        r, c = self.find_empty(sudoku.puzzle)
        if r == -1:
            return True
        
        for value in range(1, 10):
            if self.check_valid_entry(sudoku.puzzle, sudoku.size, value, r, c):
                sudoku.puzzle[r][c] = value
                if self.solve(sudoku, r, c):
                    return True
                
                sudoku.puzzle[r][c] = 0

        return False

class ImprovedRecursiveSolver(Strategy):
    def solve(self, sudoku: Sudoku, r: int = 0, c: int = 0) -> bool:
        r, c = self.find_empty(sudoku.puzzle)
        if r == -1:
            return True
        
        values = sudoku.cell_options[r][c].valid_nums
        for value in values:
            if self.check_valid_entry(sudoku.puzzle, sudoku.size, value, r, c):
                sudoku.puzzle[r][c] = value
                if self.solve(sudoku, r, c):
                    return True
                
                sudoku.puzzle[r][c] = 0
        
        return False

# TODO: add early exit if puzzle is solved
# TODO: add false condition if puzzle not solved at the end 
class PersonalSolver(Strategy):
    def __init__(self):
        self.recurive_solver = ImprovedRecursiveSolver()

    def update_valid_entries(self, sudoku: Sudoku) -> None:
        for r in range(sudoku.size):
            for c in range(sudoku.size):
                # only update valid_nums if the cell is empty
                if sudoku.puzzle[r][c] != 0:
                    continue

                options = sudoku.cell_options[r][c]
                options.valid_nums = [value for value in options.valid_nums if self.check_valid_entry(sudoku.puzzle, sudoku.size, value, r, c)]
                # only one valid option so add into puzzle
                if len(options.valid_nums) == 1: 
                    cell_value = options.valid_nums[0]
                    sudoku.puzzle[r][c] = cell_value
                    sudoku.remove_element_valid_nums(r, c, cell_value)
    
    def row_solve_entries(self, sudoku: Sudoku, row_index: int) -> None:
        combined_possible_entries = []
        history = {}

        # iterate along the row
        for c in range(sudoku.size):
            if sudoku.puzzle[row_index][c] == 0:
                options = sudoku.cell_options[row_index][c]
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

                sudoku.puzzle[row_index][key] = elem
                sudoku.remove_element_valid_nums(row_index, key, elem)
                single_entries.remove(elem)

                if len(single_entries) == 0:
                    break

    def col_solve_entries(self, sudoku: Sudoku, col_index: int) -> None:
        combined_possible_entries = []
        history = {}
        
        # iterate along the row
        for r in range(sudoku.size):
            if sudoku.puzzle[r][col_index] == 0:
                options = sudoku.cell_options[r][col_index]
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

                sudoku.puzzle[key][col_index] = elem
                sudoku.remove_element_valid_nums(key, col_index, elem)
                single_entries.remove(elem)
                if len(single_entries) == 0:
                    break

    def solve_cell(self, sudoku: Sudoku, r_corner: int, c_corner: int) -> None:
        combined_possible_entries = []
        history = {}

        # find any empty cells in a chunk and add their cell options to combined list
        for r in range(3):
            for c in range(3):
                row = r_corner + r
                col = c_corner + c
                if sudoku.puzzle[row][col] != 0:
                    continue
                
                options = sudoku.cell_options[row][col]
                combined_possible_entries += options.valid_nums
                history[(row, col)] = options.valid_nums
        
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

                sudoku.puzzle[key[0]][key[1]] = elem
                sudoku.remove_element_valid_nums(key[0], key[1], elem)
                single_entries.remove(elem)
                if len(single_entries) == 0:
                    break 

    def solve(self, sudoku : Sudoku, r: int = 0, c: int = 0) -> None:
        # run valid_entries twice as some cells will be solved on the first pass
        for _ in range(2):
            self.update_valid_entries(sudoku)

        # check if any rows can be solved
        for r in range(sudoku.size):
            self.row_solve_entries(sudoku, r)

        # check if any columns can be solved
        for c in range(sudoku.size):
            self.col_solve_entries(sudoku, c)

        # iterate over chunk corners
        for r_corner in range(0, 8, 3):
            for c_corner in range(0, 8, 3):
                self.solve_cell(sudoku, r_corner, c_corner)

        self.recurive_solver.solve(sudoku)

        return True
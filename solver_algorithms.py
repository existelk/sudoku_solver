from abc import ABC, abstractmethod
from collections import Counter, defaultdict

from sudoku_elements import Sudoku, Cell

class Strategy(ABC):
    def find_empty(self, puzzle: list[list[Cell]]) -> tuple[int, int]:
        """
        Find an empty cell in the puzzle. Return row, column index or -1, -1 if no empty cells.
        """ 
        for r in range(len(puzzle)):
            for c in range(len(puzzle[r])):
                if (puzzle[r][c].value == 0):
                    return r,c
                
        return -1,-1
    
    def check_valid_entry(self, puzzle: list[list[Cell]], size: int, value: int, row: int, col: int) -> int:
        """
        Check value is a valid option for cell.
        """

        # check row
        if any(puzzle[row][c].value == value for c in range(size)):
            return False

        # check column
        if any(puzzle[r][col].value == value for r in range(size)):
            return False

        # check box
        box_size = int(len(puzzle) ** 0.5)
        r_corner = (row // box_size) * box_size
        c_corner = (col // box_size) * box_size
        for x in range(r_corner, r_corner + box_size):
            for y in range(c_corner, c_corner + box_size):
                if puzzle[x][y].value == value:
                    return False
        
        return True
    
    @abstractmethod
    def solve(self, sudoku: Sudoku, r: int, c: int) -> bool:
        pass

class RecursiveSolver(Strategy):
    def solve(self, sudoku: Sudoku, r: int = 0, c: int = 0) -> bool:
        """
        Basic backtracking recursive solver algorithm.
        """
        r, c = self.find_empty(sudoku.puzzle)
        if r == -1:
            return True
        
        for value in range(1, 10):
            if self.check_valid_entry(sudoku.puzzle, sudoku.size, value, r, c):
                sudoku.puzzle[r][c].value = value
                if self.solve(sudoku, r, c):
                    return True
                
                sudoku.puzzle[r][c].value = 0

        return False

class ImprovedRecursiveSolver(Strategy):
    def solve(self, sudoku: Sudoku, r: int = 0, c: int = 0) -> bool:
        """
        Improved recursive solver. Uses cell valid entries to reduce the number of options to try at each empty cell.
        """
        r, c = self.find_empty(sudoku.puzzle)
        if r == -1:
            return True
        
        values = sudoku.puzzle[r][c].valid_nums
        for value in values:
            if self.check_valid_entry(sudoku.puzzle, sudoku.size, value, r, c):
                sudoku.puzzle[r][c].value = value
                if self.solve(sudoku, r, c):
                    return True
                
                sudoku.puzzle[r][c].value = 0
        
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
                if sudoku.puzzle[r][c].value != 0:
                    continue

                valid_nums = sudoku.puzzle[r][c].valid_nums
                valid = [num for num in valid_nums if self.check_valid_entry(sudoku.puzzle, sudoku.size, num, r, c)]
                
                # only one valid option so add into puzzle
                if len(valid) == 1: 
                    sudoku.puzzle[r][c].value = valid[0]
                    sudoku.remove_element_valid_nums(r, c, valid[0])

                sudoku.puzzle[r][c].valid_nums = valid
    
    def row_solve_entries(self, sudoku: Sudoku, row_index: int) -> None:
        counter = Counter()
        history = defaultdict(list)

        # collect all possible entries for empty cells in the row
        for c in range(sudoku.size):
            if sudoku.puzzle[row_index][c].value == 0:
                valid_nums = sudoku.puzzle[row_index][c].valid_nums
                counter.update(valid_nums)
                history[c] = valid_nums # keep a history of valid_nums and associated column index to avoid another loop later
        
        single_entries = {num for num, count in counter.items() if count == 1}

        if len(single_entries) == 0:
            return
        
        # if a possible value only appears for one cell in a row, it can be assigned to that cell
        for col, valid_nums in history.items():
            unique_nums = single_entries & set(valid_nums)
            if unique_nums:
                num = unique_nums.pop()
                sudoku.puzzle[row_index][col].value = num
                sudoku.remove_element_valid_nums(row_index, col, num)
                single_entries.remove(num)

                if not single_entries:
                    break

    def col_solve_entries(self, sudoku: Sudoku, col_index: int) -> None:
        counter = Counter()
        history = defaultdict(list)
        
        # iterate along the row
        for r in range(sudoku.size):
            if sudoku.puzzle[r][col_index].value == 0:
                valid_nums = sudoku.puzzle[r][col_index].valid_nums
                counter.update(valid_nums)
                history[r] = valid_nums # keep a history of valid_nums and associated column index to avoid another loop later
        
        single_entries = {num for num, count in counter.items() if count == 1}

        if len(single_entries) == 0:
            return

        # if a possible value only appears for one cell in a row, it can be assigned to that cell
        for row, valid_nums in history.items():
            unique_nums = single_entries & set(valid_nums)
            if unique_nums:
                num = unique_nums.pop()
                sudoku.puzzle[row][col_index].value = num
                sudoku.remove_element_valid_nums(row, col_index, num)
                single_entries.remove(num)

                if not single_entries:
                    break

    def chunk_solve_entries(self, sudoku: Sudoku, r_corner: int, c_corner: int) -> None:
        counter = Counter()
        history = defaultdict(list)

        # find any empty cells in a chunk and add their cell options to combined list
        for r in range(3):
            for c in range(3):
                row = r_corner + r
                col = c_corner + c
                if sudoku.puzzle[row][col].value != 0:
                    continue
                valid_nums = sudoku.puzzle[row][col].valid_nums
                counter.update(valid_nums)
                history[(row, col)] = valid_nums
        
        # if a value only appears for one cell in a chunk, it can be assigned to that cell
        single_entries = {num for num, count in counter.items() if count == 1}

        if len(single_entries) == 0:
            return
        
        for cell_coords, valid_nums in history.items():
            unique_nums = single_entries & set(valid_nums)
            if unique_nums:
                num = unique_nums.pop()
                sudoku.puzzle[cell_coords[0]][cell_coords[1]].value = num
                sudoku.remove_element_valid_nums(cell_coords[0], cell_coords[1], num)
                self.update_valid_entries(sudoku)
                single_entries.remove(num)

                if not single_entries:
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
                self.chunk_solve_entries(sudoku, r_corner, c_corner)

        self.recurive_solver.solve(sudoku)

        return True
import copy

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
    def __init__(self, new_sudoku: list[list[int]]):
        self.puzzle = copy.deepcopy(new_sudoku)
        self.size = len(self.puzzle) # assuming puzzle is square 
        self.cell_options = [[PotentialEntries() for _ in range(self.size)] for _ in range(self.size)]

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

    def reset(self, puzzle: list[list[int]]) -> None:
        self.puzzle = copy.deepcopy(puzzle)

        for r in range(self.size):
            for c in range(self.size):
                self.cell_options[r][c].reset_valid_nums()
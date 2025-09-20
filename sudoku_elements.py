import copy

class Cell:
    def __init__(self, value=0):
        self.value = value
        self.valid_nums = set(range(1, 10)) if value == 0 else set()

    def remove_invalid_num(self, num) -> None:
        if num not in self.valid_nums:
            return

        self.valid_nums.remove(num)

class Sudoku:
    def __init__(self, new_sudoku: list[list[int]]):
        self.size = len(new_sudoku) # assuming puzzle is square 
        self.puzzle = [[Cell(val) for val in row] for row in new_sudoku]

    def remove_element_valid_nums(self, row_index: int, col_index: int, value: int) -> None:
        """ 
        When a new value is added to a cell, the related row, column and chunk cells valid entries lists have to be updated 
        """
        for r in range(self.size):
            self.puzzle[r][col_index].remove_invalid_num(value)

        for c in range(self.size):
            self.puzzle[row_index][c].remove_invalid_num(value)

        box_size = int(self.size ** 0.5)
        row = (row_index // box_size) * box_size
        col = (col_index // box_size) * box_size
        for r in range(row, row+3):
            for c in range(col, col+3):
                self.puzzle[r][c].remove_invalid_num(value)

    def reset(self, puzzle: list[list[int]]) -> None:
        self.size = len(puzzle)
        self.puzzle = [[Cell(val) for val in row] for row in puzzle]
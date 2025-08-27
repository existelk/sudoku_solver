from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def solve(self, puzzle: list[list[int]], r: int, c: int) -> bool:
        pass

class RecursiveSolver(Strategy):
    # TODO change type hint?
    def solve(self, puzzle: list[list[int]], r: int = 0, c: int = 0) -> bool:
        r, c = puzzle.find_empty()
        if r == -1:
            return True
        
        for value in range(1, 10):
            if puzzle.check_valid_entry(value, r, c):
                puzzle.puzzle[r][c] = value
                if self.solve(puzzle, r, c):
                    return True
                
                puzzle.puzzle[r][c] = 0

        return False

class ImprovedRecursiveSolver(Strategy):
    # TODO change type hint?
    def solve(self, puzzle: list[list[int]], r: int = 0, c: int = 0) -> bool:
        r, c = puzzle.find_empty()
        if r == -1:
            return True
        
        values = puzzle.cell_options[r][c].valid_nums
        for value in values:
            if puzzle.check_valid_entry(value, r, c):
                puzzle.puzzle[r][c] = value
                if self.solve(puzzle, r, c):
                    return True
                
                puzzle.puzzle[r][c] = 0
        
        return False

# TODO: add early exit if puzzle is solved
# TODO: add false condition if puzzle not solved at the end 
class PersonalSolver(Strategy):
    def __init__(self):
        self.recurive_solver = ImprovedRecursiveSolver()

    def solve(self, sudoku : list[list[int]]) -> None:
        # run valid_entries twice as some cells will be solved on the first pass
        for _ in range(2):
            sudoku.update_valid_entries()

        # check if any rows can be solved
        for r in range(sudoku.size):
            sudoku.row_solve_entries(r)

        # check if any columns can be solved
        for c in range(sudoku.size):
            sudoku.col_solve_entries(c)

        # iterate over chunk corners
        for r_corner in range(0, 8, 3):
            for c_corner in range(0, 8, 3):
                sudoku.solve_cell(r_corner, c_corner)

        self.recurive_solver.solve(sudoku)

        return True
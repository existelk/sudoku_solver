import os

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

class Sudoku:
    def __init__(self, puzzle_matrix : list):
        self.unsolved_puzzle = puzzle_matrix
        self.puzzle = puzzle_matrix

    def pretty_print(self):
        """
        Display puzzle in a readable format.
        """
        for r in range(len(self.puzzle)): # loop over rows
            if r in [3, 6]:
                sep_str = "-" * 9 + "+"
                full_str = sep_str * 3
                print(full_str[:-1])
            for c in range(len(self.puzzle)): # assumes sudoku is square
                if c in [3, 6]:
                    print("|", end="")

                output = self.puzzle[r][c]
                if output == 0:
                    output = "-"
                print(f" {output} ", end="")
            print("\n")
    
    def find_empty(self):
        for r in range(len(self.puzzle)):
            for c in range(len(self.puzzle)):
                if (self.puzzle[r][c] == 0):
                    return r,c
                
        return -1,-1
    
    def check_valid_entry(self, value : str, row : int, col : int):
        """
        Check value is a valid option for cell.
        """
        puzzle = self.unsolved_puzzle
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


def solve_sudoku(puzzle, r=0, c=0):
    r, c = puzzle.find_empty()
    if r == -1:
        return True
    
    for value in range(1, 10):
        if puzzle.check_valid_entry(value, r, c):
            puzzle.puzzle[r][c] = value
            if solve_sudoku(puzzle, r, c):
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
    sudoku_puzzle.pretty_print()

    solve_sudoku(sudoku_puzzle)
    sudoku_puzzle.pretty_print()

if __name__ == "__main__":
    main()
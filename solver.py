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
    def __init__(self, puzzle_matrix):
        self.unsolved_puzzle = puzzle_matrix

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
                print(f" {self.puzzle[r][c]} ", end="")
            print("\n")

def read_sudoku_puzzle(puzzle_file : str) -> Sudoku:
    """
    Read sudoku from input text file. * represents an empty space.
    """
    if not os.path.isfile(puzzle_file):
        print(f"File not found. Check file is in the expected location: {puzzle_file}")
        exit(1)

    puzzle = []
    with open("puzzle.txt") as f:
        for line in f:
            format_line = line.rstrip().split(',')
            puzzle.append([format_line[i:(i + CHUNK_SIZE)] for i in range(0, len(format_line), CHUNK_SIZE)])
    
    return Sudoku(puzzle)

def main() -> None:
    print("main")
    sudoku_puzzle = read_sudoku_puzzle(PUZZLE_FILE)
    sudoku_puzzle.pretty_print()

if __name__ == "__main__":
    main()
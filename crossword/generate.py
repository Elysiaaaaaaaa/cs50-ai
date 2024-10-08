import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            print(variable,'---', self.domains[variable])
            domain = copy.deepcopy(self.domains[variable])
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    domain.remove(word)
            self.domains[variable] = domain

        # variables= self.domains.keys()
        # for variable in variables:
        #     print(variable,'---', self.domains[variable])
        #     l=variable.length
        #     words=copy.deepcopy(self.domains[variable])
        #     for world in words:
        #         if not(len(world)==l):
        #             self.domains[variable].remove(world)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        cng = False
        pnt = self.crossword.overlaps[x, y]
        if pnt:
            i, j = pnt
            domain_cp = self.domains[x].copy()
            for word1 in self.domains[x]:
                flag = False
                for word2 in self.domains[y]:
                    if word1[i] == word2[j]:
                        flag = True
                        break
                if not flag:
                    domain_cp.remove(word1)
                    cng = True
            self.domains[x] = domain_cp
        return cng

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [(x, y) for x in self.crossword.variables for y in self.crossword.variables if x != y]
        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                arcs += [(z, x) for z in self.crossword.variables if z != x and z != y]
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if assignment.get(variable, None) is None:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable1, word1 in assignment.items():
            if len(word1) != variable1.length:
                return False
        for variable1, word1 in assignment.items():
            for variable2, word2 in assignment.items():
                if variable1 == variable2:
                    continue
                pnt = self.crossword.overlaps[variable1, variable2]
                if pnt:
                    i, j = pnt
                    if word1[i] != word2[j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ans = dict()
        for word1 in self.domains[var]:
            n = 0
            for var2 in self.crossword.neighbors(var):
                if var2 in assignment:
                    continue
                (i, j) = self.crossword.overlaps[var, var2]
                for word2 in self.domains[var2]:
                    if word1[i] == word2[j]:
                        n += 1
            ans[word1] = n
        lis = list(ans.keys())
        lis.sort(key=lambda x: -ans[x])
        return lis

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        pos_ans = []
        for var in self.crossword.variables:
            if var not in assignment:
                pos_ans.append([var, len(self.domains[var])])
        pos_ans.sort(key=lambda x: x[1])
        ans = []
        for i in range(len(pos_ans)):
            if pos_ans[i][1] == pos_ans[0][1]:
                ans.append(pos_ans[i][0])
            else:
                break
        ans.sort(key=lambda x: len(self.crossword.neighbors(x)), reverse=True)
        return ans[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        values = self.order_domain_values(var, assignment)
        for v in values:
            assignment[var] = v
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if not (result == None):
                    return result
            assignment.pop(var)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

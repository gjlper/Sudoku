from itertools import product, groupby


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return sorted(list(map(lambda t: t[0] + t[1], product(A, B))))


rows = 'ABCDEFGHI'
cols = '123456789'

# GENERAL
boxes = cross(rows, cols)  # 81
# adding diagonal contraint units
diagonal_units = [list(map(lambda t: t[0] + t[1], zip(rows, cols))),
                  list(map(lambda t: t[0] + t[1], zip(rows, reversed(cols))))]

row_units = [cross(r, cols) for r in rows]  # list of 9 rows

column_units = [cross(rows, c) for c in cols]  # list of 9 columns

square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]  # list of 9 sub-boxes

unitlist = row_units + column_units + square_units + \
    diagonal_units  # 29 units = 29 lists

# BOX SPECIFIC
units = dict((box, [unit for unit in unitlist if box in unit])
             for box in boxes)
peers = dict((box, list(set(sum(units[box], [])) - {box})) for box in boxes)

# To see progress
assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any
    # values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins an eliminate from peers in same unit
    for unit in unitlist:
        # Filter boxes with possibilities of length 2
        boxes = [(values[box], box) for box in unit if len(values[box]) == 2]

        for value, group in groupby(boxes, key=lambda t: t[0]):
            group = list(group)
            # only naked twin groups
            if len(group) == 2:
                # transform to (value, [box1, box2])
                twin = (value, [t[1] for t in group])
                twin_peers = set(unit) - set(twin[1])
                # elimination
                for peer in twin_peers:
                    for digit in value:
                        values = assign_value(values, peer, values[
                            peer].replace(digit, ''))  # eliminate the digit

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    digits = '123456789'
    values = dict(
        [(box, value) if value in digits else (box, digits) for box, value in zip(boxes, grid)])
    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[box]) for box in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_boxes = [box for box, value in values.items() if len(value) == 1]
    for box in solved_boxes:
        digit = values[box]
        for peer in peers[box]:
            # IF ALL REPLACED = NO POSSIBILTY LEFT = AGENT MADE A MISTAKE
            values = assign_value(values, peer, values[
                peer].replace(digit, ''))

    return values


def only_choice(values):
    """
   Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
   Input: A sudoku in dictionary form.
   Output: The resulting sudoku in dictionary form.
   """

    for unit in unitlist:
        for digit in '123456789':
            places = [box for box in unit if digit in values[box]]
            if len(places) == 1:
                values = assign_value(values, places[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_boxes_before = [box for box,
                               value in values.items() if len(value) == 1]
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_boxes_after = [box for box,
                              value in values.items() if len(value) == 1]
        stalled = len(solved_boxes_before) == len(solved_boxes_after)
        # ERROR CHECK/USEFUL IN DFS
        if len([box for box, value in values.items() if len(value) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku."""
    values = reduce_puzzle(values)

    if not values:  # ERROR CHECK
        return False

    box = min(values, key=lambda b: len(
        values[b]) if len(values[b]) != 1 else 10)  # Box with minimum possibilities

    possibilities = values[box]

    if len(possibilities) == 1:  # FULLY SOLVED
        return values

    for p in possibilities:
        child_sudoku = values.copy()
        child_sudoku[box] = p
        attempt = search(child_sudoku)  # recursively find solution
        if attempt:  # solution found
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    try:
        values = search(grid_values(grid))
        return values
    except TypeError:
        return False
    except Exception as e:
        print(e)


if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

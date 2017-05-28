"""
Desc: AIND Sudoku project submission code. Program intelligently solves any
sudoku puzzle, includes naked_twins() heuristic code and support for diagonal
sudoku puzzles. Portions of this code are adapted from the Udacity - Artificial
Intelligence Nanodegree (May 2017 session) online MOOC.
Input: initial puzzle configuration
Output: 2-D puzzle solution
Author: Daniel R Rines
Github: drines
Created: Friday, May 23, 2017
Version: 2017.05.25.003
"""
import logging

logging.basicConfig(filename='error.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.ERROR)


def update_log(level, message):
    """
    Function makes it easier to output logging messages instead of adding
    format instructions each time a message is sent to the logging module
    code base. Warning is the default level.
    """
    log_message = ' :: ' + message
    if level == 'debug':
        logging.debug(log_message)
    elif level == 'error':
        logging.error(log_message)
    else:
        logging.warning(log_message)

update_log('debug', 'starting execution: solution.py')
assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
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
    Overall logic:
        function obtains a list of all boxes that currently contain only two
        digits. It then loops through these boxes on a peer-by-peer manner to
        identify any set of idential two digit boxes. of course, these must
        be within the same peer group. assuming a set of naked twins are found
        in a peer group, then function will search for each of the digits in
        other peer associated boxes and remove them, leaving just the non-
        twin digits.
    """
    # find all instances of naked twins
    values = find_twins(values,
                        [box for box in values.keys()
                         if len(values[box]) == 2])
    return values


def find_twins(values, two_digit_boxes):
    """
    Modularized code to handle the search aspects of the naked_twins algorithm.
    Args:
        two_digit_boxes(list): a list of all the boxes with the two digit
        values.
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for box in two_digit_boxes:
        for peer_group in units[box]:
            for twin_box in peer_group:    # loop through peer groups
                if values[box] == values[twin_box] and box != twin_box:
                    update_log('debug', 'Found a twin: ' + box +
                               ' -> (' + values[twin_box] + ')')
                    # now isolate and eliminate the digits if possible
                    values = eliminate_twins(values, box, twin_box,
                                             peer_group, values[box])
    return values


def eliminate_twins(values, box, twin_box, group, digits):
    """
    Modularized code to handle the search aspects of the naked_twins algorithm.
    Args:
        values(dict) - a dictionary with key: box and value: digits
        box(string) - the first two digit box in the peer
        twin_box(string) - the second two digit box in the peer
        group(list) - the list of all keys in current peer
        digits(string) - a successfully ident. set of naked twin digits
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for digit in digits:
        # eliminate the naked twins as possibilities in
        # their peers.
        for fix_box in group:
            # make sure you don't remove digits from either
            # of the naked twins and don't remove any digits
            # from a single digit (assigned) box.
            if box != fix_box and fix_box != twin_box and \
                    len(values[fix_box]) > 1:
                update_log('debug',
                           'eliminating digit from non-twins box: ' +
                           fix_box + '-> ' +
                           values[fix_box] + '(' +
                           digit + ')')
                values = assign_value(values, fix_box,
                                      values[fix_box].replace(digit, ''))
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    update_log('debug', 'convert input sudoku grid')
    chars = []
    digits = '123456789'
    for cpos in grid:
        if cpos in digits:
            chars.append(cpos)
        if cpos == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value,
    eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    update_log('debug', 'executing eliminate()')
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values = \
                assign_value(values, peer, values[peer].replace(digit, ''))
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that
    only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    update_log('debug', 'executing only_choice()')
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                # values[dplaces[0]] = digit
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box
    with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same,
    return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    update_log('debug', 'executing reduce_puzzle()')
    stalled = False
    while not stalled:
        solved_values_before = \
            len([box for box in values.keys() if len(values[box]) == 1])
        # extended the constraint propogation to include the diagonal
        # peer constraint via the eliminate() function execution. the peer
        # groups are initially defined with global 'unit' constants.
        values = eliminate(values)
        values = only_choice(values)
        # also extended the constraint propogation loop to include the
        # test for naked twins (two boxes with idential set of paired
        # digits). this heuristic removes digits from other peer
        # associated boxes that are already included in any twins.
        values = naked_twins(values)
        solved_values_after = \
            len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if stalled:
            update_log('debug', 'reduce_puzzle() stalled')
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree
    and solve the sudoku."""
    update_log('debug', 'executing search()')
    # First, reduce the puzzle using the previous function
    # Choose one of the unfilled squares with the fewest possibilities
    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  # Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    _, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example:
            '2.............62....1....7...6..8...3...9...7...6..4...4.
            ...8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no
        solution exists.
    """
    update_log('debug', 'executing solve()')
    return search(grid_values(grid))


# Initialize global constants
update_log('debug', 'global constant initialization')
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
# added two additional peer groups for any units located along
# either of the matrix diagnols. these are then included with the
# unitlist definition and, thus, 'baked in' into the constraint
# propogation process.
diag_units = [[r+c for r, c in zip(rows, cols)],
              [r+c for r, c in zip(rows, cols[::-1])]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)

if __name__ == '__main__':
    """
    Entry point for Sudoku solution.py code base.
    """
    update_log('debug', 'called: __main__')

    diag_sudoku_grid = \
        '2.............62....1....7...6..8...3...9...7' + \
        '...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        update_log('debug', 'problems with pygame execution')
        print('We could not visualize your board due to a pygame issue.' +
              ' Not a problem! It is not a requirement.')

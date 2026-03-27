# ==========================================
# COMPONENT: 2D Array (Matrix)
# [NOTE]: Uses a nested list comprehension to build rows, then arranges them DOWN.
# To access cell [row][col], you will use squares[row][col] in your animation loop.
# ==========================================
def create_2d_array(grid_data):
    rows = len(grid_data)
    cols = len(grid_data[0])
    
    matrix_squares = VGroup()
    matrix_labels = VGroup()
    
    for r in range(rows):
        row_squares = VGroup(*[Square(side_length=0.6) for _ in range(cols)]).arrange(RIGHT, buff=0.05)
        row_labels = VGroup(*[Text(str(grid_data[r][c]), font_size=18).move_to(row_squares[c]) for c in range(cols)])
        matrix_squares.add(row_squares)
        matrix_labels.add(row_labels)
        
    matrix_squares.arrange(DOWN, buff=0.05)
    matrix_labels.match_y(matrix_squares) # Keep labels aligned with their rows
    
    matrix_group = VGroup(matrix_squares, matrix_labels).move_to(UP * 2)
    return matrix_group, matrix_squares, matrix_labels
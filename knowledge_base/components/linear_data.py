# ==========================================
# COMPONENT: 1D Array
# [NOTE]: Anchored to UP * 2 to stay perfectly centered in the top UI zone.
# ==========================================
def create_1d_array(data):
    squares = VGroup(*[Square(side_length=0.7) for _ in data]).arrange(RIGHT, buff=0.1)
    labels = VGroup(*[Text(str(x), font_size=20).move_to(squares[i]) for i, x in enumerate(data)])
    array_group = VGroup(squares, labels).move_to(UP * 2)
    return array_group, squares, labels

# ==========================================
# COMPONENT: String
# [NOTE]: buff=0 makes the boxes touch. Monospace font for characters.
# ==========================================
def create_string_array(string_data):
    squares = VGroup(*[Square(side_length=0.6) for _ in string_data]).arrange(RIGHT, buff=0)
    labels = VGroup(*[Text(char, font="Monospace", font_size=24).move_to(squares[i]) for i, char in enumerate(string_data)])
    string_group = VGroup(squares, labels).move_to(UP * 2)
    return string_group, squares, labels
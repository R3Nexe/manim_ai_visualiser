# ==========================================
# COMPONENT: Set
# [NOTE]: Visually distinguishes itself from arrays by using a Circle boundary and floating text without index boxes.
# ==========================================
def create_set(set_data):
    set_boundary = Circle(radius=1.5, color=PURPLE)
    set_title = Text("Set", font_size=18, color=PURPLE).next_to(set_boundary, UP)
    
    # Arrange elements in a circular layout inside the boundary
    elements = VGroup(*[Text(str(x), font_size=20) for x in set_data])
    
    # Math to space them out inside the circle
    for i, elem in enumerate(elements):
        angle = i * (TAU / len(set_data))
        elem.move_to(set_boundary.get_center() + [0.8 * np.cos(angle), 0.8 * np.sin(angle), 0])
        
    set_group = VGroup(set_boundary, set_title, elements).move_to(UP * 2)
    return set_group, elements
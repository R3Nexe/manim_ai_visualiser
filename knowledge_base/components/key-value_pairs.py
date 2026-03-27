# ==========================================
# COMPONENT: HashMap (Key-Value Pairs)
# [NOTE]: Builds a vertical list. Keys are distinct colors (e.g., BLUE) to differentiate from Values.
# ==========================================
def create_hashmap(dictionary_data):
    map_group = VGroup()
    keys_list = list(dictionary_data.keys())
    
    for i, key in enumerate(keys_list):
        val = dictionary_data[key]
        
        # Key Box (Left)
        k_box = Rectangle(width=1.2, height=0.6, color=BLUE)
        k_label = Text(str(key), font_size=18).move_to(k_box)
        k_group = VGroup(k_box, k_label)
        
        # Value Box (Right)
        v_box = Rectangle(width=1.2, height=0.6, color=WHITE)
        v_label = Text(str(val), font_size=18).move_to(v_box)
        v_group = VGroup(v_box, v_label)
        
        # Arrow connecting them
        arrow = Arrow(k_box.get_right(), v_box.get_left(), buff=0.1, max_tip_length_to_length_ratio=0.15)
        
        row = VGroup(k_group, arrow, v_group)
        map_group.add(row)
        
    # Stack them vertically and center in the top UI zone
    map_group.arrange(DOWN, buff=0.2).move_to(UP * 2)
    return map_group
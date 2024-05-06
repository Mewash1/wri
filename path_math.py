import math



#  x0  
#   |  
# --+  
#      
#      

#  x1  
#      
#      
# --+  
#   |  

#  x2  
#      
#      
#   +--
#   |  

#  x3  
#      
#   |  
#   +--
#      

#  10  
#      
# -----
#      

#  11  
#      
#   |  
#   |  
#   |  


# 10 -- straight positive y
# 11 -- straight positive x
# 2x -- sharp
# 3x -- round
# 4x -- diagonal
# 5x -- smooth round start
# 6x -- smooth round mid
# 7x -- smooth round end

# +----Y
# |
# |
# X

size = [10, 10]
cell_size = 200
starting_point = [100 + 3 * cell_size, 3 * cell_size]

map = [
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, 32, 10, 41,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, 62, 52, 20,  0, 33, 31,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, 72, 22, 10, 10, 10, 30,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, 11, 11,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0, 23, 20,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
]

def get_dist(x, y, theta):
    x += starting_point[0]
    y += starting_point[1]
    theta += 3 * math.pi / 2
    cell_x, cell_y = int(x // cell_size), int(y // cell_size)
    x -= cell_size * cell_x
    y -= cell_size * cell_y
    x -= cell_size // 2
    y -= cell_size // 2

    cell = map[cell_x][cell_y]
    cell_type = cell // 10
    cell_variant = cell % 10

    if cell_variant == 3:
        theta += 3 * math.pi / 2
        x, y = -y, x
    elif cell_variant == 2:
        theta += math.pi 
        x, y = -x, -y
    elif cell_variant == 1:
        theta += math.pi / 2
        x, y = y, -x

    while theta > 2 * math.pi:
        theta -= 2 * math.pi

    while theta < 0:
        theta += 2 * math.pi

    print(x, y, theta)
    print(cell_x, cell_y)
    print(cell, cell_type, cell_variant)

    if cell_type == 1:
        #if cell_variant == 1:
        #    x = -x
        
        if theta > math.pi / 2 and theta <= 3 * math.pi / 2:
            return -x
        else:
            return x

    elif cell_type == 2:
        if x < 0:
            if y < 0:
                res = max(x, y)
            else:
                res = y
        else:
            if y < 0:
                res = x
            else:
                res = math.sqrt(x * x + y * y)
        
        if theta > math.pi * 0.25 and theta < math.pi * 1.25:
            return -res
        else:
            return res
    elif cell_type == 3:
        x += cell_size // 2
        y += cell_size // 2
        res = math.sqrt(x * x + y * y) - cell_size // 2
        if theta > math.pi * 0.25 and theta < math.pi * 1.25:
            return -res
        else:
            return res
    elif cell_type == 4:
        res = (x + y + cell_size // 2) / math.sqrt(2)

        if theta > math.pi * 0.25 and theta < math.pi * 1.25:
            return -res
        else:
            return res
    elif cell_type == 5:
        x += 3 * cell_size // 2
        y += cell_size // 2
        res = math.sqrt(x * x + y * y) - 3 * cell_size // 2
        if theta > math.pi * 0.25 and theta < math.pi * 1.25:
            return -res
        else:
            return res
    elif cell_type == 6:
        x += 3 * cell_size // 2
        y += 3 * cell_size // 2
        res = math.sqrt(x * x + y * y) - 3 * cell_size // 2
        if theta > math.pi * 0.25 and theta < math.pi * 1.25:
            return -res
        else:
            return res
    elif cell_type == 7:
        x += cell_size // 2
        y += 3 * cell_size // 2
        res = math.sqrt(x * x + y * y) - 3 * cell_size // 2
        if theta > math.pi * 0.25 and theta < math.pi * 1.25:
            return -res
        else:
            return res
    else:
        return 0

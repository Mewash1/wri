import math

size = [10, 10]
starting_point = [10 + 3 * 20, 0 + 3 * 20]
cell_size = 20
heading = 0 # positive Y

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


map = [
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  1, 10,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, 33, 21,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
]

def get_dist(x, y, heading):
    cell_x, cell_y = x // cell_size, y // cell_size
    x -= cell_size * cell_x
    y -= cell_size * cell_y
    x -= 5
    y -= 5

    cell = map[cell_x][cell_y]
    cell_type = cell // 10
    cell_variant = cell % 10

    if cell_variant == 1:
        heading += 3 * math.pi / 2
        x, y = -y, x
    elif cell_variant == 2:
        heading += math.pi 
        x, y = -x, -y
    elif cell_variant == 3:
        heading += math.pi / 2
        x, y = y, -x

    if heading > 2 * math.pi:
        heading -= 2 * math.pi

    if cell_type == 1:
        if heading > math.pi / 2 and heading <= 3 * math.pi / 2:
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
        
        if heading > math.pi * 0.75 and heading < math.pi * 1.75:
            return -res
        else:
            return res
    elif cell_type == 3:
        x += 5
        y += 5
        res = math.sqrt(x * x + y * y)
        if heading > math.pi * 0.75 and heading < math.pi * 1.75:
            return -res
        else:
            return res
    elif cell_type == 4:
        if x + y < -5:
            res = todo
        else
            res = todo

        if heading > math.pi * 0.75 and heading < math.pi * 1.75:
            return -res
        else:
            return res
    else:
        return 1000

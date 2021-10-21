

def check_rectangle_overlap(big_rectangle, small_rectangle):
    points_overlap = 0
    
    # coordinates from opencv are left, bottom, width, heigh; which means: (x0, y0, x0+w, x0+h)
    x_1 = big_rectangle[0]
    y_1 = big_rectangle[1]
    x_2 = big_rectangle[0] + big_rectangle[2]
    y_2 = big_rectangle[1] + big_rectangle[3]
    # coordinates from face_recognition are top, right, bottom, left which means: (y0, x1, y1 ,x0)
    # check if all dots from the small rectangle (face_recognition) are inside the other rectangle (opencv)
    if (x_1 < small_rectangle[3] < x_2) and (y_1 < small_rectangle[0] < y_2):
        points_overlap += 1
    if (x_1 < small_rectangle[1] < x_2) and (y_1 < small_rectangle[2] < y_2):
        points_overlap += 1
    if (x_1 < small_rectangle[3] < x_2) and (y_1 < small_rectangle[2] < y_2):
        points_overlap += 1
    if (x_1 < small_rectangle[1] < x_2) and (y_1 < small_rectangle[0] < y_2):
        points_overlap += 1
    
    if points_overlap >= 1:
        print(points_overlap)
        return True
    
    return False

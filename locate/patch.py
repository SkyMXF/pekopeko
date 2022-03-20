import cv2
import numpy as np

def search_patch(
    template_file,
    screen_file,
    threshold=0.8,
    grayscale=True,
    scale_change=False,
    match_first=False,
    max_width=800,
    standard_scale=0.1,
    min_scale=0.5,
    max_scale=2.0,
    scale_interval=0.1
):
    # template_file & screen_file: path of img file
    # grayscale: search with gray img
    # scale_change: match with multi scale
    # first_match: return first match pos or max coef pos
    # return: [x, y] or None

    read_mode = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR

    template = cv2.imread(template_file, read_mode)
    screen = cv2.imread(screen_file, read_mode)

    # restrict screen.width to max_width
    if screen.shape[1] > max_width:
        scale = max_width / screen.shape[1]
        h, w = int(screen.shape[0] * scale), int(screen.shape[1] * scale)
        screen = cv2.resize(screen, (w, h), interpolation=cv2.INTER_NEAREST)

        if not scale_change:
            h, w = int(template.shape[0] * scale), int(template.shape[1] * scale)
            template = cv2.resize(template, (w, h), interpolation=cv2.INTER_NEAREST)

    return multi_scale_template_match(
        template, screen,
        threshold, match_first,
        standard_scale,
        min_scale, max_scale,
        scale_interval
    ) if scale_change else template_match(
        template, screen,
        threshold, match_first
    )

def template_match(template, screen, threshold, match_first):
    # template & screen: np.array by cv2.imread
    # return: [x, y] or None, x-width, y-height, 0.0-1.0

    # match with edge map
    #template = cv2.Canny(template, 50, 150)
    #screen = cv2.Canny(screen, 50, 150)
    #template = 255 - template
    #screen = 255 - screen

    match_map = cv2.matchTemplate(screen, template, cv2.TM_SQDIFF_NORMED)
    searched_loc = []
    while True:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_map)

        if min_val < (1.0 - threshold):
            # matched template
            x = min_loc[0] + template.shape[1] // 2
            y = min_loc[1] + template.shape[0] // 2
            searched_loc.append([1.0 - min_val, x / screen.shape[1], y / screen.shape[0]])
            match_map[min_loc[1], min_loc[0]] = 1.0
        else:
            break

        if match_first:
            break
    
    if len(searched_loc) == 0:
        return None
    
    if match_first:
        return searched_loc[0][1:]
    
    # sort by coef
    searched_loc = [
        loc[1:]     # remove coef
        for loc in sorted(searched_loc, key=lambda l: l[0])
    ]
    
    return searched_loc[-1]

def multi_scale_template_match(
    template, screen,
    threshold,
    match_first,
    standard_scale,
    min_scale, max_scale,
    scale_interval
):
    # template & screen: np.array by cv2.imread
    # return: [x, y] or None, x-width, y-height, 0.0-1.0

    # resize template to standard_scale * screen
    w = int(screen.shape[1] * standard_scale)
    h = int(w / template.shape[1] * template.shape[0])
    template = cv2.resize(template, (w, h), interpolation=cv2.INTER_NEAREST)
    
    # match from min_scale to max_scale, interval = scale_interval
    searched_loc = []
    curr_scale = min_scale
    while curr_scale <= max_scale:

        # resize template to current scale
        h, w = int(template.shape[0] * curr_scale), int(template.shape[1] * curr_scale)
        scaled_template = cv2.resize(template, (w, h), interpolation=cv2.INTER_NEAREST)
        
        match_map = cv2.matchTemplate(screen, scaled_template, cv2.TM_SQDIFF_NORMED)
        while True:
            # get all pos with coef > threshold
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_map)

            if min_val < (1.0 - threshold):
                # matched template
                x = min_loc[0] + scaled_template.shape[1] // 2
                y = min_loc[1] + scaled_template.shape[0] // 2
                searched_loc.append([1.0 - min_val, x / screen.shape[1], y / screen.shape[0]])
                match_map[min_loc[1], min_loc[0]] = 1.0
            else:
                break

            if match_first:
                break
        
        if match_first and len(searched_loc) > 0:
            break
        
        curr_scale += scale_interval
    
    if len(searched_loc) == 0:
        return None
    
    if not match_first:
        return searched_loc[0][1:]
    
    # sort by coef
    searched_loc = [
        loc[1:]     # remove coef
        for loc in sorted(searched_loc, key=lambda l: l[0])
    ]
    
    return searched_loc

extractor = cv2.ORB_create()
def feature_match(template, screen, threshold, multi_patch):
    # template & screen: np.array by cv2.imread
    # return: [x1, y1, x2, y2] or None, x-width, y-height, 0.0-1.0

    raise NotImplementedError

    # match with edge map
    template = cv2.Canny(template, 50, 150)
    screen = cv2.Canny(screen, 50, 150)
    
    print(template.shape)
    print(screen.shape)
    template_kp, template_dscp = extractor.detectAndCompute(template, None)
    screen_kp, screen_dscp = extractor.detectAndCompute(screen, None)

    print(len(template_kp))
    print(len(screen_kp))

    template_dscp = template_dscp.astype(np.float32)
    screen_dscp = screen_dscp.astype(np.float32)

    FLANN_INDEX_KDTREE = 0
    indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    searchParams = dict(checks=32)
    matcher = cv2.FlannBasedMatcher(indexParams, searchParams)
    matches = matcher.knnMatch(template_dscp, screen_dscp, k=2)

    #matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    #matches = matcher.match(template_dscp, screen_dscp)

    print(len(matches))

    good_match = []
    #for m, n in matches:
    #    if m.distance < 0.5*n.distance:    # 如果第一个邻近距离比第二个邻近距离的0.5倍小，则保留
    #        good_match.append(m)
    
    #舍弃大于0.7的匹配
    MIN_MATCH_COUNT = 10
    for m,n in matches:
        if m.distance < 0.95 * n.distance:
            good_match.append(m)

    if len(good_match) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([template_kp[m.queryIdx].pt for m in good_match ]).reshape(-1,1,2)
        dst_pts = np.float32([screen_kp[m.trainIdx].pt for m in good_match ]).reshape(-1,1,2)
        #计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h,w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        cv2.polylines(screen, [np.int32(dst)],True,0,2, cv2.LINE_AA)
    else:
        print( "Not enough matches are found - %d/%d" % (len(good_match), MIN_MATCH_COUNT))
        matchesMask = None
    draw_params = dict(matchColor=(0,255,0), 
                    singlePointColor=None,
                    matchesMask=matchesMask, 
                    flags=2)
    result = cv2.drawMatches(
        template, template_kp,
        screen, screen_kp,
        good_match, None, **draw_params
    )
    #plt.imshow(result, 'gray')
    #plt.show()

    cv2.imshow("result", result)
    #cv2.imshow("out_img2", out_img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def check_patch(
    template_file,
    screen_file,
    pos,        # norm value, 0.0-1.0
    threshold=0.8,
    grayscale=True,
    scale_change=False,
    max_width=800,
    standard_scale=0.1,
    min_scale=0.5,
    max_scale=2.0,
    scale_interval=0.1
):
    # template_file & screen_file: path of img file
    # grayscale: search with gray img
    # scale_change: match with multi scale
    # pos: [width, height], value=0.0-1.0
    # return: True or False

    read_mode = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR

    template = cv2.imread(template_file, read_mode)
    screen = cv2.imread(screen_file, read_mode)

    # restrict screen.width to max_width
    if screen.shape[1] > max_width:
        scale = max_width / screen.shape[1]
        h, w = int(screen.shape[0] * scale), int(screen.shape[1] * scale)
        screen = cv2.resize(screen, (w, h), interpolation=cv2.INTER_NEAREST)

        if not scale_change:
            h, w = int(template.shape[0] * scale), int(template.shape[1] * scale)
            template = cv2.resize(template, (w, h), interpolation=cv2.INTER_NEAREST)

    return multi_scale_template_check(
        template, screen,
        pos, threshold,
        standard_scale,
        min_scale, max_scale,
        scale_interval
    ) if scale_change else template_check(
        template, screen,
        pos, threshold
    )

def template_check(template, screen, pos, threshold):
    # check if template is in pos of screen
    
    # crop screen with pos and template.shape
    search_scale = 1.3
    h, w = template.shape[:2]
    h = int(search_scale * h)
    w = int(search_scale * w)
    h_min = int(pos[1] * screen.shape[0] - h / 2)
    h_max = h_min + h
    w_min = int(pos[0] * screen.shape[1] - w / 2)
    w_max = w_min + w

    h_min = max(0, h_min)
    h_max = min(screen.shape[0], h_max)
    w_min = max(0, w_min)
    w_max = min(screen.shape[1], w_max)

    crop_screen = screen[h_min: h_max, w_min: w_max, ...]

    # search
    match_map = cv2.matchTemplate(crop_screen, template, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_map)
    if min_val < (1.0 - threshold):
        # matched template
        return True
    
    return False

def multi_scale_template_check(
    template, screen,
    pos, threshold,
    standard_scale,
    min_scale, max_scale,
    scale_interval
):
    # check if template is in pos of screen

    # resize template to standard_scale * screen
    w = int(screen.shape[1] * standard_scale)
    h = int(w / template.shape[1] * template.shape[0])
    template = cv2.resize(template, (w, h), interpolation=cv2.INTER_NEAREST)
    
    # crop screen with pos and template.shape
    search_scale = 1.1
    h, w = template.shape[:2]
    h = int(search_scale * h * max_scale)
    w = int(search_scale * w * max_scale)
    h_min = int(pos[1] * screen.shape[0] - h / 2)
    h_max = h_min + h
    w_min = int(pos[0] * screen.shape[1] - w / 2)
    w_max = w_min + w

    h_min = max(0, h_min)
    h_max = min(screen.shape[0], h_max)
    w_min = max(0, w_min)
    w_max = min(screen.shape[1], w_max)

    crop_screen = screen[h_min: h_max, w_min: w_max, ...]

    # search
    curr_scale = min_scale
    while curr_scale <= max_scale:

        # resize template to current scale
        h, w = int(template.shape[0] * curr_scale), int(template.shape[1] * curr_scale)
        scaled_template = cv2.resize(template, (w, h), interpolation=cv2.INTER_NEAREST)
        
        match_map = cv2.matchTemplate(crop_screen, scaled_template, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_map)
        if min_val < (1.0 - threshold):
            # matched template
            return True
        
        curr_scale += scale_interval
    
    return False
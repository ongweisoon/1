import math
import time
from typing import Tuple, List, Union
from .points import *

import cv2
import numpy as np
import mss

import threading
import queue

img_swm = cv2.imread('img/swm.png')
img_swm_h = cv2.imread('img/swm_h.png')
img_box = cv2.imread('img/box.png')
img_cola_b = cv2.imread('img/cola_b.png')
img_cola_o = cv2.imread('img/cola_o.png')
img_digua = cv2.imread('img/digua.png')
img_shutiao = cv2.imread('img/shutiao.png')
img_shutiao_l = cv2.imread('img/shutiao_l.png')
img_full_screen = cv2.imread('img/full_screen_2.png')

to_show_image = queue.Queue()  # put: (window_name, img)

WINDOW_NAME_GUEST = 'guest'
WINDOW_NAME_TABLE = 'table'
WINDOW_NAME_FRY = 'fry'


def __background_show_window():
    cv2.namedWindow(WINDOW_NAME_TABLE, cv2.WINDOW_NORMAL)
    cv2.namedWindow(WINDOW_NAME_GUEST, cv2.WINDOW_NORMAL)
    cv2.namedWindow(WINDOW_NAME_FRY, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME_TABLE, 200, 100)
    cv2.resizeWindow(WINDOW_NAME_GUEST, 200, 100)
    cv2.resizeWindow(WINDOW_NAME_FRY, 200, 100)
    while True:
        try:
            # get from queue
            name, img = to_show_image.get_nowait()
            cv2.imshow(name, img)
            img_size = img.shape
            cv2.resizeWindow(name, img_size[1], img_size[0])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except queue.Empty:
            time.sleep(0.1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()


def init_show_windows():
    threading.Thread(target=__background_show_window, daemon=True).start()


def calc_center_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def is_center_too_close_to(points_list: List[Tuple[int, int]], center: Tuple[int, int], threshold: int = 10) -> bool:
    for p in points_list:
        if calc_center_distance(p, center) < threshold:
            return True
    return False


def match_many_object_on_image(whole_img: np.ndarray,
                               obj_img: np.ndarray,
                               threshold=0.8,
                               draw_rect=False,
                               save_file=False,
                               output_name='output.png'):
    """
    在整张图片上找到所有的目标物体
    :param whole_img: 整张图片
    :param obj_img: 目标物体
    :param threshold: 阈值
    :param draw_rect:
    :param save_file:
    :param output_name:
    :return: 所有目标物体的坐标
    """
    res = cv2.matchTemplate(whole_img, obj_img, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    match = []
    center_points = []
    final_points = []
    for pt in zip(*loc[::-1]):
        center = (pt[0] + obj_img.shape[1] // 2, pt[1] + obj_img.shape[0] // 2)
        if is_center_too_close_to(center_points, center):
            continue
        center_points.append(center)
        final_points.append(pt)
        match.append(pt)
        if draw_rect:
            cv2.rectangle(whole_img, pt, (pt[0] + obj_img.shape[1], pt[1] + obj_img.shape[0]), (0, 255, 0), 2)
    if save_file:
        # save to img/output.png
        cv2.imwrite('test/' + (output_name or 'output.png'), whole_img)
    return final_points


def fast_screen_shot(left_up: Tuple[int, int], right_down: Tuple[int, int], save=True) -> np.ndarray:
    with mss.mss() as sct:
        monitor = {'top': left_up[1], 'left': left_up[0], 'width': right_down[0] - left_up[0],
                   'height': right_down[1] - left_up[1]}
        img = np.array(sct.grab(monitor))
        if save:
            cv2.imwrite('img/capture.png', img)
        # convert
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


if __name__ == '__main__':
    # for image, name in [
    #     (img_swm, 'swm'),
    #     (img_box, 'box'),
    #     (img_cola_b, 'cola_b'),
    #     (img_cola_o, 'cola_o'),
    #     (img_digua, 'digua'),
    #     (img_shutiao, 'shutiao'),
    # ]:
    #     print(name)
    #     res = match_many_object_on_image(img_full_screen, image, draw_rect=True, output_name=name + '.png')
    #     print(f'there are {len(res)} {name} in the screen')
    fast_screen_shot(POS_GUEST_1_LT, POS_GUEST_1_RB)

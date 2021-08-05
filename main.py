from time import sleep

import PIL.Image
from PIL import ImageGrab, ImageChops, ImageDraw
from xdo import Xdo

waitTime = 1.0
interval = .2
asteroidBBox = [130, 220, 130 + 1680, 220 + 240]

xdo = Xdo()
lg2 = -1


def neighbours(x, y, w, h):
    out = []
    for nx in range(-1, 2):
        for ny in range(-1, 2):
            if nx == ny == 0 or \
                    x + nx < 0 or x + nx >= w or \
                    y + ny < 0 or y + ny >= h:
                continue
            out.append((x + nx, y + ny))
    return out


def setup():
    global lg2
    lg2 = xdo.search_windows("Lazy Galaxy 2".encode("utf-8"))
    if len(lg2) > 1:
        print("More than 1 LG2??")
        exit(1)
    elif len(lg2) < 1:
        print("Launch LG2!!")
        exit(1)
    lg2 = lg2[0]
    xdo.set_window_size(lg2, 1920, 1080)
    xdo.focus_window(lg2)
    xdo.wait_for_window_focus(lg2, 1)
    lg2loc = xdo.get_window_location(lg2)
    return [
        lg2loc[0] + asteroidBBox[0],
        lg2loc[1] + asteroidBBox[1],
        lg2loc[0] + asteroidBBox[2],
        lg2loc[1] + asteroidBBox[3]
    ]


def find_asteroid(pixels, pos, size):
    a = [pos[0], pos[1], pos[0]+1, pos[1]+1]
    for _ in range(2):
        found = [False, False, False]  # left, top, bottom

        while not found[0] and a[2] < size[0]:
            found[0] = True
            for y in range(a[1], a[3]):
                try:
                    if pixels[a[2], y]:
                        a[2] += 1
                        found[0] = False
                        break
                except IndexError:
                    print('0', a[2], y)

        while not found[1] and a[1] > 0:
            found[1] = True
            for x in range(a[0], a[2]):
                if pixels[x, a[1]-1] == 255:
                    a[1] -= 1
                    found[1] = False
                    break

        while not found[2] and a[3] < size[1] - 3:
            found[2] = True
            for x in range(a[0], a[2]):
                try:
                    if pixels[x, a[3]] == 255:
                        a[3] += 1
                        found[2] = False
                        break
                except IndexError:
                    print('2', x, a[3])

    return a


def start():
    lg2asteroid_box = setup()
    counter = 10

    while counter > 0:
        sleep(waitTime)
        pxa = ImageGrab.grab(lg2asteroid_box)
        sleep(interval)
        pxb = ImageGrab.grab(lg2asteroid_box)
        diff = ImageChops.difference(pxa, pxb)\
            .convert("L").resize((pxa.width // 8, pxa.height // 8))\
            .point(lambda x: 0 if x == 0 else 255, '1')
        pixels = diff.load()
        asteroids = []
        for x in range(0, diff.width):
            for y in range(0, diff.height):
                skip = False
                for a in asteroids:
                    if a[0] <= x < a[2] and a[1] <= y < a[3]:
                        skip = True
                        break
                if skip:
                    continue
                if pixels[x, y] == 255:
                    asteroids.append(find_asteroid(pixels, (x, y), (diff.width, diff.height)))

        # print(len(asteroids))
        # overlay = PIL.Image.blend(pxa, diff.resize((pxa.width, pxa.height), PIL.Image.NEAREST).convert("RGB"), .5)
        # overlay_draw = ImageDraw.Draw(overlay)
        for a in asteroids:
            # overlay_draw.rectangle([a[0]*8, a[1]*8, a[2]*8, a[3]*8], outline=(0, 255, 0), width=2)
            aavg = [(a[0] + a[2])*4, (a[1] + a[3])*4]
            # overlay_draw.ellipse([aavg[0] - 4, aavg[1] - 4, aavg[0] + 4, aavg[1] + 4], outline=(255, 0, 0), width=2)
            xdo.move_mouse(lg2asteroid_box[0] + aavg[0], lg2asteroid_box[1] + aavg[1])
            xdo.click_window_multiple(lg2, 1, 4, 20*1000)
        # overlay.show()
        # break
        counter -= 1


if __name__ == '__main__':
    start()

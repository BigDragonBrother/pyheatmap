# -*- coding: utf-8 -*-
#
# author: oldj
# blog: http://oldj.net
# email: oldj.wu@gmail.com
#


import os
import Image
import ImageDraw2
from libs import cf


class HeatMap(object):

    def __init__(self,
            data,
            base=None,
            width=0,
            height=0
        ):
        u""""""

        assert type(data) in (list, tuple)
        assert base is None or os.path.isfile(base)
        assert type(width) in (int, long, float)
        assert type(height) in (int, long, float)
        assert width >= 0 and height >= 0

        self.data = data
        self.base = base
        self.width = width
        self.height = height

        if not self.base and (self.width == 0 or self.height == 0):
            w, h = cf.getMaxSize(data)
            self.width = self.width or w
            self.height = self.height or h

        if self.base:
            self.__im = Image.open(self.base)
            self.width, self.height = self.__im.size()

        else:
            self.__im = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))


    def __paintHit(self, x, y, color):
        u""""""

        im = self.__im
        width, height = self.width, self.height
        im.putpixel((x, y), color)

        for i in (1, 2):
            pos = (
                (x + i, y + i),
                (x + i, y - i),
                (x - i, y + i),
                (x - i, y - i),
            )
            for ix, iy in pos:
                if ix >= 0 and iy >= 0 and ix < width and iy < height:
                    im.putpixel((ix, iy), color)


    def clickmap(self, save_as, color=(255, 0, 0, 255)):
        u""""""

        for hit in self.data:
            x, y = hit[0], hit[1]
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                continue

            self.__paintHit(x, y, color)


        self.save_as = save_as
        self.__save()


    def __heat(self, heat_data, x, y, template):
        u""""""

        l = len(heat_data)
        width = self.width
        p = width * y + x

        for ip, iv in template:
            p2 = p + ip
            if 0 <= p2 < l:
                heat_data[p2] += iv


    def __paintHeat(self, heat_data, colors):
        u""""""

        import re

        im = self.__im
        rr = re.compile(", (\d+)%\)")
        dr = ImageDraw2.ImageDraw.Draw(im)
        width = self.width
        height = self.height

        max_v = max(heat_data)
        if max_v <= 0:
            # 空图片
            return

        r = 240.0 / max_v
        heat_data2 = [int(i * r) - 1 for i in heat_data]

        size = width * height
        for p in xrange(size):
            v = heat_data2[p]
            if v > 0:
                x, y = p % width, p // width
                color = colors[v]
                alpha = int(rr.findall(color)[0])
                if alpha > 50:
                    al = 255 - 255 * (alpha - 50) / 50
                    im.putpixel((x, y), (0, 0, 255, al))
                else:
                    dr.point((x, y), fill=color)


    def heatmap(self, save_as):
        u""""""

        circle = cf.mkCircle(10, self.width)
        heat_data = [0] * self.width * self.height

        for hit in self.data:
            x, y = hit[0], hit[1]
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                continue

            self.__heat(heat_data, x, y, circle)

        self.__paintHeat(heat_data, cf.mkColors())

        self.save_as = save_as
        self.__save()


    def __save(self):

        save_as = os.path.join(os.getcwd(), self.save_as)
        folder, fn = os.path.split(save_as)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        self.__im.save(save_as)



def test():
    u""""""

    import random

    width = 400
    height = 300
    r = 50
    data = []

    for i in range(4):
        data.append([
            random.randint(0, width - 1),
            random.randint(0, height - 1),
        ])

    for i in xrange(12):
        data2 = []
        for x, y in data:
            x2 = x + random.randint(-r, r)
            y2 = y + random.randint(-r, r)
            data2.append([x2, y2])
        data.extend(data2)

    print(len(data))
    hm = HeatMap(data)
#    hm.clickmap(save_as="hit.png")
    hm.heatmap(save_as="heat.png")



if __name__ == "__main__":
    test()

import sim
import shapes
import ui
import copy
import time
import pygame

import glm

# !!! you can allways use matplotlib and I sugest you try it first, I include
# this plots lib here for a way of ploting data directly on the main surface

# !!! this lib is SLOW, use it with that in mind

# the number of characters in `-1e-99`
_RESERVED_CHAR_CNT = 6

_TITLE_DISTANCE = 2
_LABEL_DISTANCE = 1.5

# under this angle we throw away points, see comments in Graph.draw
# put this 1 if you don't want this, but be aware it will be much slower
_MAX_COS = 0.9999

Color = sim.Color

class Defs:
    # You can view the plot as a window in the space of the graphs, as such
    # this window will be moved and stretched for all graphs contained in a plot

    # The following plot modes and mode options can be used:

    # if data leaves the window the data will be removed, but will remember
    # points that cross the window boundry
    # TODO: OPT_CLIP_DATA = 100

    # data points that are outside the window will be removed
    # TODO: OPT_CLIP_DATA_STRICT = 101

    # ebable save, move, rescale, add_marker buttons
    OPT_DRAW_BUTTONS = 102

    DEFAULT_OPTS = [OPT_DRAW_BUTTONS]

    # When in this mode the window will slide when new data is added, depending
    # on the options the window size will depend on initial DA and DB
    MODE_SLIDING = 0

    # Will only slide in the positive direction and will ignore negative values
    OPT_SLIDE_PX = 1

    # analogous to above
    OPT_SLIDE_NX = 2

    # If set the window will be resized in the y direction to fit the data
    OPT_SLIDE_RESIZE_Y = 3

    DEFAULT_SLIDING_OPTS = [OPT_SLIDE_PX, OPT_SLIDE_RESIZE_Y] + DEFAULT_OPTS

    # The internal window will autoresize to fit all data on screen, uses
    # DA and DB for the minimal initial bounds, set to None to auto set them
    MODE_RESIZE = 1

    # If set the window will be resized on the x direction to fit the data on
    # screen
    OPT_RESIZE_X = 0
    
    # analogous to above
    OPT_RESIZE_Y = 1

    # will resize the graph in such a way that the origin will not move from
    # the original location of the graph on the screen
    # * requires DA and DB to be set
    # * if O is None it will be initialized to (DA + DB) / 2
    # * if O is too close to the border (< 1e3) you will get undefined
    # behaviour, check the next options if you want to only resize in a
    # specific direction
    #TODO: OPT_RESIZE_ORIGIN = 2

    # will only resize in the positive x direction, to the right of O if not
    # none
    #TODO: OPT_RESIZE_PX = 3

    # the following are analogous to above:
    #TODO: OPT_RESIZE_NX = 4
    #TODO: OPT_RESIZE_PY = 5
    #TODO: OPT_RESIZE_NY = 6

    DEFAULT_RESIZE_OPTS = [OPT_RESIZE_X, OPT_RESIZE_Y] + DEFAULT_OPTS

class DataPoint():
    def __init__(self, P, inside):
        self.P = glm.vec2(P)
        self.inside = inside

# graphs are used inside plots, you can't have graphs that do not belong to a
# plot
class Graph:
    # data_y    - an array with the y coords of the data
    # data_x    - an array with the x coords of the data on screen
    def __init__(self, data_y=None, data_x=None, color=Color.BLACK, name="",
            parent_plot=None):
        self.parent_plot = parent_plot
        self.data_y = data_y
        self.data_x = data_x
        # _data_y, _data_x are internal views of the actual data
        self._data = []
        self.refresh_plot()
        self.color = color
        self.name = name

    def refresh_plot(self, recursive=False):
        self._data = []
        self.inflection_points = []

        if self.parent_plot.mode == Defs.MODE_SLIDING:
            self.diff_x = self.parent_plot.DB.x - self.parent_plot.DA.x
        if not self.data_y is None:
            if not self.data_x is None:
                if len(self.data_x) != len(self.data_y):
                    raise Exception("Can't plot data with disagreeing lengths")
                for i in range(len(self.data_x)):
                    self._add_point(self.data_x[i], self.data_y[i])
            else:
                for i in range(len(self.data_y)):
                    self._add_point(i, self.data_y[i])
        if not recursive:
            for g in self.parent_plot.graphs:
                if g != self:
                    g.refresh_plot(recursive=True)

    def append_point(self, x, y):
        if self.data_x:
            self.data_x.append(x)
        if self.data_y:
            self.data_y.append(y)
        self._add_point(x, y)

    def _add_point(self, x, y):
        P = glm.vec2(x, y)
        if not self.parent_plot.DA:
            self.parent_plot.DA = glm.vec2(P.x, P.y)
        if not self.parent_plot.DB:
            self.parent_plot.DB = glm.vec2(P.x, P.y)
        if self.parent_plot.mode == Defs.MODE_RESIZE:
            if Defs.OPT_RESIZE_X in self.parent_plot.mode_opts:
                if self.parent_plot.DA.x > P.x:
                    self.parent_plot.DA.x = P.x
                if self.parent_plot.DB.x < P.x:
                    self.parent_plot.DB.x = P.x
            if Defs.OPT_RESIZE_Y in self.parent_plot.mode_opts:
                if self.parent_plot.DA.y > P.y:
                    self.parent_plot.DA.y = P.y
                if self.parent_plot.DB.y < P.y:
                    self.parent_plot.DB.y = P.y
        if self.parent_plot.mode == Defs.MODE_SLIDING:
            if Defs.OPT_SLIDE_RESIZE_Y in self.parent_plot.mode_opts:
                if self.parent_plot.DA.y > P.y:
                    self.parent_plot.DA.y = P.y
                if self.parent_plot.DB.y < P.y:
                    self.parent_plot.DB.y = P.y
            check_px = False
            check_nx = False
            if Defs.OPT_SLIDE_PX in self.parent_plot.mode_opts:
                check_px = True
            elif Defs.OPT_SLIDE_NX in self.parent_plot.mode_opts:
                check_nx = True
            else:
                check_px = True
                check_nx = True
            if check_nx and self.parent_plot.DA.x > P.x:
                self.parent_plot.DA.x = P.x
                self.parent_plot.DB.x = self.parent_plot.DA.x + self.diff_x
            if check_px and self.parent_plot.DB.x < P.x:
                self.parent_plot.DB.x = P.x
                self.parent_plot.DA.x = self.parent_plot.DB.x - self.diff_x
        self.parent_plot.off = glm.vec2(self.parent_plot.DA)
        self.parent_plot.scale = glm.vec2(
                self.parent_plot.DB.x - self.parent_plot.DA.x,
                self.parent_plot.DB.y - self.parent_plot.DA.y)\
            / glm.vec2(
                self.parent_plot.IB.x - self.parent_plot.IA.x,
                self.parent_plot.IB.y - self.parent_plot.IA.y)
        if abs(self.parent_plot.scale.x) < 0.0000001:
            self.parent_plot.scale.x = 0.00001
        if abs(self.parent_plot.scale.y) < 0.0000001:
            self.parent_plot.scale.y = 0.00001
        self.parent_plot.win_off = glm.vec2(self.parent_plot.IA) -\
                self.parent_plot.off / self.parent_plot.scale
        prev_dp = None
        if len(self._data) > 0:
            prev_dp = self._data[-1]
        if self.is_inside(P):
            if prev_dp:
                aabb = shapes.AABB(self.parent_plot.DA, self.parent_plot.DB)
                if not prev_dp.inside:
                    line = shapes.Segment(prev_dp.P, P)
                    intr = aabb.intersect(line)
                    self._data.append(DataPoint(intr[0], inside=False))
                    self._data.append(DataPoint(P, inside=True))
                    # print("pass boundry from outside", self._data[-1].P)
                else:
                    self._data.append(DataPoint(P, inside=True))
                    # print("continue inside")
            else:
                self._data.append(DataPoint(P, inside=True))
                # print("first point is inside")
        else:
            if prev_dp:
                aabb = shapes.AABB(self.parent_plot.DA, self.parent_plot.DB)
                if not prev_dp.inside:
                    self._data[-1] = DataPoint(P, inside=False)
                    # print("continue outside")
                else:
                    line = shapes.Segment(prev_dp.P, P)
                    intr = aabb.intersect(line)
                    self._data.append(DataPoint(intr[0], inside=False))
                    self._data.append(DataPoint(P, inside=False))
                    # print("pass boundry from inside")
            else:
                self._data.append(DataPoint(P, inside=False))
                # print("first point is outside")


    def draw(self):
        if len(self._data) <= 1:
            return
        to_remove = []
        marked_out = {}
        for i in range(1, len(self._data)):
            p1 = self._data[i - 1]
            p2 = self._data[i]
            if not p1.inside and not p2.inside:
                continue
            p1_inside = self.is_inside(p1.P)
            p2_inside = self.is_inside(p2.P)

            # TODO: fix this check removing segments at the boundry
            if not p1_inside and not p2_inside:
                to_remove.append(i - 1)
                to_remove.append(i)
                continue
            # drawing thousands of points is problematic at least, the problem
            # is that we don't have the computation power to do that and most of
            # the points we add are useless in most cases.
            # 
            # a point P is useless if it's neighbours A to the left and B to the
            # right can form a line AB such that drawing the lines AP and PB
            # will make no difference on screen from drawing only the line AB
            # 
            # in the same way if we have the sequence A, P1, P2, ... Pn, B such
            # that the distance from all points P1, P2, ... Pn to the line
            # AB is smaller than one pixel we can draw the line AB ignoring the
            # lines AP1, P1P2, P2P3, ... Pn-1Pn, PnB
            if i > 1:
                p0 = self._data[i - 2]
                p0_inside = self.is_inside(p0.P)
                if p0.inside and p1.inside and p2.inside and \
                        p0_inside and p1_inside and p2_inside and \
                        i-1 not in marked_out:
                    n1 = self._d2win(p1.P) - self._d2win(p0.P)
                    n2 = self._d2win(p2.P) - self._d2win(p1.P)
                    d = glm.dot(n1, n2)
                    if d * d > glm.length2(n1) * glm.length2(n2) * _MAX_COS:
                        marked_out[i - 1] = 0
                        to_remove.append(i - 1)
        to_remove = sorted(set(to_remove))
        for i in reversed(to_remove):
            del self._data[i]
        to_draw = []
        for i in range(1, len(self._data)):
            p1 = self._data[i - 1]
            p2 = self._data[i]
            if not p1.inside and not p2.inside:
                continue
            p1_inside = self.is_inside(p1.P)
            p2_inside = self.is_inside(p2.P)

            if self.is_inside(p1.P) and self.is_inside(p2.P):
                to_draw.append(self._d2win(p1.P))
                to_draw.append(self._d2win(p2.P))
                continue
            aabb = shapes.AABB(self.parent_plot.DA, self.parent_plot.DB)
            line = shapes.Segment(p1.P, p2.P)
            intr = aabb.intersect(line)
            if not intr:
                print("bambuzle")
                # ????
                continue
            if p1_inside and not p2_inside:
                to_draw.append(self._d2win(p1.P))
                to_draw.append(self._d2win(intr[0]))
            else:
                to_draw.append(self._d2win(intr[0]))
                to_draw.append(self._d2win(p2.P))
        for i in range(len(to_draw)):
            to_draw[i] = sim.pos2screen(to_draw[i])
        pygame.draw.lines(sim.state.surface, self.color, False,
                to_draw)

    def is_inside(self, P):
        if self.parent_plot.DA.x <= P.x and self.parent_plot.DA.y <= P.y:
            if self.parent_plot.DB.x >= P.x and self.parent_plot.DB.y >= P.y:
                return True
        return False

    def _d2win(self, pos):
        return pos / self.parent_plot.scale + self.parent_plot.win_off

class Plot:
    # A, B      - the bounding box of the whole plot(dictates it's screen
    #           position, where A is the bottom left corner and B is top right)
    #           in the form (x, y)
    #           * The draw area will be smaller than the rectangle defined by
    #           A and B, because it must include the labels and other
    #           pieces of information
    # name      - the name of the plot
    # xlabel    - the name of the x axis
    # ylabel    - the name of the y axis
    # mode      - dictates the way the plot will rescale itself by adding points
    #           (see above for each mode)
    # mode_opts - options specific to the selected mode
    # data      - a list of lists with the positional parameters for a Graph
    #           * for example:
    #           data=[[[2, 2, 4], [1, 2, 3], Color.RED, "name"], [[1, 2, 1])]
    #           * see Graph class for more info
    #           * those will be added as graphs inside the plot
    # kdata     - a lits of dicts with the rest of the parameters
    #           * if both kdata and data are present their 
    # DA        - optional initial data bound(bottom left) in the form (x, y)
    # DB        - optional initial data bound(top right) in the form (x, y)
    # O         - optional resize origin in the form (x, y)
    # font_obj  - the font object that should be used for the graph, if none the
    #           default is used
    # chars_cnt - the number of chars minus _RESERVED_CHAR_CNT,
    #           used to represent the coords, minimum is 0 to be able to
    #           represent -1e-99
    #           * 2 is necesary to represent -1.1e-09
    def __init__(self,
            A, B,
            name=None, xlabel=None, ylabel=None,
            mode=Defs.MODE_RESIZE, mode_opts=Defs.DEFAULT_RESIZE_OPTS,
            data=None, kdata=None,
            DA=None, DB=None, O=None,
            font_obj=None, chars_cnt=0):
        self.graphs = []
        self.aabb = shapes.AABB(A, B)
        self.name = name
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.mode = mode
        self.mode_opts = mode_opts
        self.off = 0
        self.win_off = 0
        self.scale = 0
        self._DA = glm.vec2(DA) if DA else None
        self._DB = glm.vec2(DB) if DB else None
        self._O  = glm.vec2(O)  if O  else glm.vec2()
        self.reset_window()
        self.chr_cnt = chars_cnt + _RESERVED_CHAR_CNT

        # Uggly repetition, plz fix
        if data and not kdata:
            for d in data:
                self.graphs.append(Graph(*d, parent_plot=self))
        if kdata and not data:
            for kd in kdata:
                self.graphs.append(Graph(**kd, parent_plot=self))
        if data and kdata:
            for d, kd in zip(data, kdata): 
                self.graphs.append(Graph(*d, **kd, parent_plot=self))

        if not font_obj:
            self.font_obj = sim.state.font

        # calculating the internal draw area
        self.IA = glm.vec2(self.aabb.AA)
        self.IB = glm.vec2(self.aabb.BB)

        self.chr_h = sim.px2dist(self.font_obj.char_height_px())
        self.chr_w = sim.px2dist(self.font_obj.char_width_px())

        # name is at the top, and requires 1.5 of it's font size
        self.title_dist = _TITLE_DISTANCE
        self.label_dist = _LABEL_DISTANCE
        if name:
            self.IB.y -= self.chr_h * self.title_dist
        else:
            self.IB.y -= self.chr_h / 2 + self.chr_w

        if xlabel:
            self.IA.y += self.chr_h * self.label_dist

        if ylabel:
            self.IA.x += self.chr_h * self.label_dist


        self.lbl_w = self.chr_w * self.chr_cnt
        self.lbl_h = self.chr_h

        # one character width will be the distance from labels to the draw area
        self.IA.x += self.chr_w + self.lbl_w
        self.IB.x -= self.lbl_w / 2
        self.IA.y += self.chr_w + self.chr_h

        if self.IA.x > self.IB.x or self.IA.y > self.IB.y:
            raise Exception("Not enaugh space for drawing after placing lbls")

        self.lbl_x_cnt = round((self.IB.x - self.IA.x) // self.lbl_w)
        self.lbl_y_cnt = round((self.IB.y - self.IA.y) // self.lbl_h)

        if self.lbl_x_cnt < 2 or self.lbl_y_cnt < 2:
            raise Exception("Not enaugh space for labels")

        if self.lbl_x_cnt > 10:
            self.lbl_x_cnt = 10
        if self.lbl_y_cnt > 10:
            self.lbl_y_cnt = 10

        self.iaabb = shapes.AABB(self.IA, self.IB)

    def refresh_plot(self):
        for g in self.graphs:
            g.refresh_plot(recursive=True)

    def create_graph(self, *args, **kwargs):
        g = Graph(*args, **kwargs, parent_plot=self)
        self.graphs.append(g)
        return g

    def reset_window(self):
        self.DA = glm.vec2(self._DA) if self._DA else None
        self.DB = glm.vec2(self._DB) if self._DB else None
        self.O  = glm.vec2(self._O)  if self._O  else glm.vec2()

    def coord_str(self, number):
        cnt = self.chr_cnt - _RESERVED_CHAR_CNT
        return ("{0:."+f"{cnt}"+"g}").format(number)


    def draw(self):
        # Draw bounds
        self.aabb.draw()
        self.iaabb.draw()

        # Draw name
        if self.name:
            x = (self.aabb.AA.x + self.aabb.BB.x) / 2
            y = self.aabb.BB.y - self.chr_h * self.title_dist / 2
            ui.TextLine(self.name, pos=(x, y), color=Color.BLACK,
                    font_obj=self.font_obj,
                    align=(ui.XCENTER, ui.YCENTER)).draw()

        # Draw y labels
        if self.ylabel:
            x = self.aabb.AA.x + self.chr_h * self.label_dist / 2
            y = (self.aabb.AA.y + self.aabb.BB.y) / 2
            ui.TextLine(self.ylabel, pos=(x, y), color=Color.BLACK,
                    font_obj=self.font_obj, align=(ui.XCENTER, ui.YCENTER),
                    rotated=True).draw()

        lbl_y_dist = (self.IB.y - self.IA.y) / (self.lbl_y_cnt)
        day = self.DA.y if self.DA else 0
        dby = self.DB.y if self.DB else 0
        lbl_yd_dist = (dby - day) / (self.lbl_y_cnt)
        for i in range(self.lbl_y_cnt + 1):
            x = self.IA.x - self.chr_w
            y = self.IA.y + i * lbl_y_dist
            sim.draw_line([x + self.chr_w / 2, y], [x + self.chr_w * 3 / 2, y])
            ui.TextLine(self.coord_str(day + i * lbl_yd_dist), pos=(x, y),
                    color=Color.BLACK, font_obj=self.font_obj,
                    align=(ui.XRIGHT, ui.YCENTER)).draw()

        # draw x labels
        if self.xlabel:
            x = (self.aabb.AA.x + self.aabb.BB.x) / 2
            y = self.aabb.AA.y + self.chr_h * self.label_dist / 2
            ui.TextLine(self.xlabel, pos=(x, y), color=Color.BLACK,
                    font_obj=self.font_obj,
                    align=(ui.XCENTER, ui.YCENTER)).draw()

        lbl_x_dist = (self.IB.x - self.IA.x) / (self.lbl_x_cnt)
        dax = self.DA.x if self.DA else 0
        dbx = self.DB.x if self.DB else 0
        lbl_xd_dist = (dbx - dax) / (self.lbl_x_cnt)
        for i in range(self.lbl_x_cnt + 1):
            x = self.IA.x + i * lbl_x_dist
            y = self.IA.y - self.chr_w
            sim.draw_line([x, y + self.chr_w / 2], [x, y + self.chr_w * 3 / 2])
            ui.TextLine(self.coord_str(dax + i * lbl_xd_dist), pos=(x, y),
                    color=Color.BLACK, font_obj=self.font_obj,
                    align=(ui.XCENTER, ui.YTOP)).draw()

        # draw buttons
        # TODO

        # draw graphs(the actual data)
        for g in self.graphs:
            g.draw()

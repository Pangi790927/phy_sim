import sim
import utils
import ui
import plots
import time
import numpy as np

Color = sim.Color
sim.init(width=1200, height=800, scale=1)
s = sim.state.scale
fps = utils.FpsCounter()
frame_ctrl = utils.FpsCounter(1/30)

p = plots.Plot(
    [-0.8, -0.8], [0.8, 0],
    name="This is a plot",
    ylabel="ylabel",
    xlabel="xlabel",
    DA=(-22222221, -1222222),
    DB=(22222221, 1222222),
    chars_cnt=5,
)


q = plots.Plot(
    [0.0, 0.5], [1, 1],
    name="Force",
    ylabel="y[m]",
    xlabel="x[s]"
)

w = plots.Plot(
    [-1, 0], [1, 0.5],
    mode=plots.Defs.MODE_SLIDING,
    name="Some graph",
    DA=(-1, 0),
    DB=(1, 1),
    chars_cnt=5,
)

# w.mode_opts.remove(plots.Defs.OPT_RESIZE_Y)

g1 = w.create_graph(color=Color.RED)
g2 = q.create_graph(color=Color.BLACK)
g2.data_x = np.linspace(0, 100, 1000)
g2.data_y = np.cos(g2.data_x)
q.refresh_plot()
t0 = time.time()

def draw_fn():
    fps.update()
    if frame_ctrl.update():
        t = time.time() - t0
        g1.append_point(t, np.sin(t))

    p.draw()
    q.draw()
    w.draw()

    # g2.append_point(t, np.cos(t))

    metadata = '\n'.join([
        "fps %d" % fps.get_fps(),
    ])
    ui.TextBlock(metadata, pos=(-s+0.01, s-0.01)).draw()

sim.loop(draw_fn=draw_fn)

import sim

# Those classes are meant to be registered inside `sim` with the function
# `interactive_add`. Check test_movable for an example.
# Once the elements are registered to the sim module they will be drawn inside
# the main loop, before calling the user draw method

# TODO: add a priority argument so that the user can controll when an object
# should be drawn above another one

def _none_fn(*args, **kwargs):
    pass

class Interactive():
	def __init__(self, shape_type, *args,
			on_click=_none_fn,
			on_release=_none_fn,
			on_move=_none_fn,
			on_hover=_none_fn,
			**kwargs):
		self.shape = shape_type(*args, **kwargs)
		self.on_click = on_click
		self.on_release = on_release
		self.on_move = on_move
		self.on_hover = on_hover
		self.is_clicked = False
		self.is_hovered = False

	def on_click_fn(self, pos, old_pos):
		if self.shape.intersect_point(pos):
			self.is_clicked = True
			self.on_click(pos, old_pos)
			# returns true to gain focus
			return True
		return False

	def on_release_fn(self, pos, old_pos):
		if self.is_clicked:
			self.on_release(pos, old_pos)
			self.is_clicked = False

	def on_move_fn(self, pos, old_pos):
		old_int = self.shape.intersect_point(old_pos)
		pos_int = self.shape.intersect_point(pos)

		if old_int and not pos_int:
			self.on_hover_fn(pos, old_pos, False, True)
			self.is_hovered = False
		elif pos_int and not old_int:
			self.on_hover_fn(pos, old_pos, True, False)
			self.is_hovered = True
		elif pos_int and old_int:
			self.on_hover_fn(pos, old_pos, False, False)
			self.is_hovered = True
		else:
			self.is_hovered = False

		if self.is_clicked:
			self.on_move(pos, old_pos)

	def on_hover_fn(self, pos, old_pos, entered, exited):
		self.on_hover(pos, old_pos, entered, exited)

	def draw(self):
		self.shape.draw()


class Movable(Interactive):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def on_click_fn(self, pos, old_pos):
		return super().on_click_fn(pos, old_pos)

	def on_release_fn(self, pos, old_pos):
		super().on_release_fn(pos, old_pos)

	def on_move_fn(self, pos, old_pos):
		super().on_move_fn(pos, old_pos)
		if self.is_clicked:
			self.shape.translate_origin(pos - old_pos)

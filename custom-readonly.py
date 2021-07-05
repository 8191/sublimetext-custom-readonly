import sublime
import sublime_plugin
import os.path


class ToggleReadonlyModeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		set_read_only(self.view, not self.view.is_read_only())


class ToggleReadonlyListener(sublime_plugin.EventListener):

	def debug(self, str):
		pass
		# print("custom-readonly {0}: {1}".format(self.__hash__(), str))

	""" Called on initialization to pass all open views. """
	def on_init(self, views):
		self.debug("on_init()")
		for view in views:
			self.on_load(view)

	"""	Called for each view (file) opened. """
	def on_load(self, view):
		self.debug("called ToggleReadonlyListener: on_load")
		# Check if this project is configured for this read only mode
		if view.settings().get('read_only_mode'):
			if view.window() is not None and view.window().project_data():
				project_paths = [i.get("path", "") for i in view.window().project_data().get("folders", {"path": ''})]

				file_in_project = False
				# Check if file is part of the project
				for path in project_paths:
					path = os.path.normpath(path)
					# Maybe this project path is relative?
					if not os.path.exists(path):
						path = os.path.join(os.path.dirname((view.window().project_file_name())), path)
					if (view.file_name() is not None) and (path in view.file_name()):
						file_in_project	= True

				if file_in_project:
					self.debug("File {0} in project. Setting read-only.".format(view.file_name()))
					set_read_only(view, True)
				else:
					# Disable read-only - might be set when opening file via goto (ctrl+p)
					self.debug("File {0} NOT in project. Disable read-only.".format(view.file_name()))
					set_read_only(view, False)
			else:
				self.debug("No window passed or not part of a project")
				# Set all views not part of a project to read-only - workaround for file selection using goto (ctrl+p)
				set_read_only(view, True)

		else:
			self.debug("read_only_mode not set")


def set_read_only(view, read_only = True):
	if read_only:
		view.set_read_only(True)
		view.set_status('read_only_mode', 'Read-only')
	else:
		view.set_read_only(False)
		view.set_status('read_only_mode', '')
			
	alter_color_scheme(view)


def alter_color_scheme(view):
	scheme = view.settings().get("color_scheme")
	print("Light scheme: {0}, Dark scheme: {1}".format(
		view.settings().get("light_color_scheme"),
		view.settings().get("dark_color_scheme"))
	)

	if view.is_read_only():
		view.settings().set("dark_color_scheme", "Mariana Readonly.sublime-color-scheme")
		view.settings().set("light_color_scheme", "Breakers Readonly.sublime-color-scheme")
	else:
		view.settings().erase("dark_color_scheme")
		view.settings().erase("light_color_scheme")

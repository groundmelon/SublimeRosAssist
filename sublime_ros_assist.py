import sublime
import sublime_plugin
import os


def oprint(s):
    print("[ros_assist] {}".format(s))


def generate_package_paths(ros_ws_path):
    pkg_paths = list()
    for root, dirs, files in os.walk(ros_ws_path):
        if 'package.xml' in files \
                and root.find('src') >= 0 \
                and 'CATKIN_IGNORE' not in files:
            pkg_paths.append(root)
    return pkg_paths


def generate_include_flags(ros_ws_path):
    inc_paths = [os.path.join(os.path.join(ros_ws_path, 'devel'), 'include')] \
        + [os.path.join(path, 'include')
           for path in generate_package_paths(ros_ws_path)]
    oprint(inc_paths)
    return ["-I"+p for p in inc_paths]


class SublimeRosAssistRevealPackageCommand(sublime_plugin.WindowCommand):

    def finish_package(self, i):
        if i >= 0:
            active_window = sublime.active_window()
            active_window.open_file(
                os.path.join(self.pkg_paths[i], 'package.xml'))
            active_window.run_command("reveal_in_side_bar")
            active_window.active_view().close()

    def finish_ros_ws(self, i):
        if i >= 0:
            oprint("select \"{}\"".format(self.ros_ws_paths[i]))
            pkg_paths = generate_package_paths(self.ros_ws_paths[i])
            self.pkg_paths = pkg_paths
            active_window = sublime.active_window()
            active_window.show_quick_panel(
                pkg_paths, self.finish_package, 0, 0)
        else:
            oprint("Withdraw select")

    def run(self):
        active_window = sublime.active_window()
        proj_paths = [d['path']
                      for d in active_window.project_data()['folders']]
        oprint("project_paths:{}".format(proj_paths))

        ros_ws_paths = list()
        for proj_path in proj_paths:
            for root, dirs, files in os.walk(proj_path):
                if 'setup.bash' in files and root[-5:] == 'devel':
                    ros_ws_paths.append(os.path.dirname(root))
        oprint("ros_ws_paths:{}".format(ros_ws_paths))
        self.ros_ws_paths = ros_ws_paths

        if len(self.ros_ws_paths) > 1:
            active_window.show_quick_panel(
                proj_paths, self.finish_ros_ws, 0, 0)
        else:
            self.finish_ros_ws(0)


class SublimeRosAssistGenerateClangFlagsCommand(sublime_plugin.WindowCommand):

    def finish(self, i):
        if i >= 0:
            oprint("select \"{}\"".format(self.ros_ws_paths[i]))
            inc_flags = generate_include_flags(self.ros_ws_paths[i])
            active_window = sublime.active_window()
            data = active_window.project_data()
            if 'settings' not in data:
                data['settings'] = dict()

            plugin_settings = sublime.load_settings(
                "sublime_ros_assist.sublime-settings")
            extra_flags = plugin_settings.get('extra_flags_for_clang', list())

            data['settings']['sublimeclang_options'] = extra_flags + inc_flags
            active_window.set_project_data(data)
        else:
            oprint("Withdraw select")

    def run(self):
        active_window = sublime.active_window()
        proj_paths = [d['path']
                      for d in active_window.project_data()['folders']]
        oprint("project_paths:{}".format(proj_paths))

        ros_ws_paths = list()
        for proj_path in proj_paths:
            for root, dirs, files in os.walk(proj_path):
                if 'setup.bash' in files and root[-5:] == 'devel':
                    ros_ws_paths.append(os.path.dirname(root))
        oprint("ros_ws_paths:{}".format(ros_ws_paths))
        self.ros_ws_paths = ros_ws_paths

        if len(self.ros_ws_paths) > 1:
            active_window.show_quick_panel(proj_paths, self.finish, 0, 0)
        else:
            self.finish(0)

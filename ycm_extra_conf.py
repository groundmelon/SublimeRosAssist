# -*- coding: utf-8 -*-

##################################################################################
##                                                                              ##
##  An Enhanced ycm_extra_conf.py for ROS, C++YouCompleteMe and Sublime-text-3  ##
##                                                                              ##
##################################################################################
#                                                                                #
# Inspired by https://github.com/mavlink/mavros/blob/master/.ycm_extra_conf.py   #
#                                                                                #
# Modified from                                                                  #
#     https://github.com/Valloric/ycmd/blob/master/cpp/ycm/.ycm_extra_conf.py    #
#                                                                                #
# You can save this file to your catkin_ws folder to make it work.               #
#                                                                                #
##################################################################################

import os
import ycm_core
import itertools


def get_ros_package_paths():
    '''
      This function assume that this script is on or above ros_ws src
      This function will locate *devel/setup.bash to find the path for src folder
    '''

    ros_ws_path = None
    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
        if 'setup.bash' in files and root[-5:] == 'devel':
            ros_ws_path = os.path.abspath(os.path.dirname(root))

    pkg_paths = list()
    if ros_ws_path:
        for root, dirs, files in os.walk(ros_ws_path):
            if 'package.xml' in files \
                    and 'CMakeLists.txt' in files \
                    and root.find('src') >= 0 \
                    and 'CATKIN_IGNORE' not in files:
                pkg_paths.append(root)
    return pkg_paths


def get_ros_package_include_dirs():
    '''
      This function will add /include to each item of get_ros_package_paths()
    '''

    return [path + "/include" for path in get_ros_package_paths()]


def get_ros_package_include_flags():    
    '''
      This function will add '-I' between each item of get_ros_package_include_dirs()
    '''
    return list(itertools.chain.from_iterable(('-I', p) for p in get_ros_package_include_dirs()))


default_flags = [
    '-Wall',
    '-Wextra',
    # '-Werror',
    # '-Wc++98-compat',
    # '-Wno-long-long',
    # '-Wno-variadic-macros',
    '-fexceptions',
    # '-DNDEBUG',
    # THIS IS IMPORTANT! Without a "-std=<something>" flag, clang won't know
    # which language to use when compiling headers. So it will guess. Badly. So
    # C++ headers will be compiled as C headers. You don't want that so ALWAYS
    # specify a "-std=<something>".
    # For a C project, you would set this to something like 'c99' instead of
    # 'c++11'.
    # '-std=c++03',
    '-std=c++11',
    '-stdlib=libstdc++',
    # ...and the same thing goes for the magic -x option which specifies the
    # language that the files to be compiled are written in. This is mostly
    # relevant for c++ headers.
    # For a C project, you would set this to 'c' instead of 'c++'.
    '-x',
    'c++',
    '-I',
    '.',

    # include third party libraries
    # '-isystem',
    # '/some/path/include',
    '-I',
    '/usr/include/eigen3/',
    '-I',
    '/home/ltb/catkin_ws/devel/include/',
    '-I',
    '/opt/ros/indigo/include/',
    '-I',
    '/usr/include/',
    '-I',
    '/usr/include/c++/4.8/',
    '-I',
    '/usr/include/x86_64-linux-gnu/c++/4.8/',
]

flags = default_flags + get_ros_package_include_flags()

# Print log in the tmp folder
with open("/tmp/ycm_extra_conf_{}.log".format(__file__.replace('/', '_').replace('.', '_')), 'w') as f:
    f.write("[\n")
    for item in flags:
        f.write(item)
        f.write(",\n")
    f.write("]")

    f.write("-------- compile flag --------\n")
    for item in flags:
        f.write(item)
        if item == "-I" or item == "-isystem":
            pass
        else:
            f.write(" ")
    f.write("\n")

# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# You can get CMake to generate this file for you by adding:
#   set( CMAKE_EXPORT_COMPILE_COMMANDS 1 )
# to your CMakeLists.txt file.
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
compilation_database_folder = ''

if os.path.exists(compilation_database_folder):
    database = ycm_core.CompilationDatabase(compilation_database_folder)
else:
    database = None

SOURCE_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.c', '.m', '.mm']


def DirectoryOfThisScript():
    return os.path.dirname(os.path.abspath(__file__))


def MakeRelativePathsInFlagsAbsolute(flags, working_directory):
    if not working_directory:
        return list(flags)
    new_flags = []
    make_next_absolute = False
    path_flags = ['-isystem', '-I', '-iquote', '--sysroot=']
    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith('/'):
                new_flag = os.path.join(working_directory, flag)

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith(path_flag):
                path = flag[len(path_flag):]
                new_flag = path_flag + os.path.join(working_directory, path)
                break

        if new_flag:
            new_flags.append(new_flag)
    return new_flags


def IsHeaderFile(filename):
    extension = os.path.splitext(filename)[1]
    return extension in ['.h', '.hxx', '.hpp', '.hh']


def GetCompilationInfoForFile(filename):
    # The compilation_commands.json file generated by CMake does not have entries
    # for header files. So we do our best by asking the db for flags for a
    # corresponding source file, if any. If one exists, the flags for that file
    # should be good enough.
    if IsHeaderFile(filename):
        basename = os.path.splitext(filename)[0]
        for extension in SOURCE_EXTENSIONS:
            replacement_file = basename + extension
            if os.path.exists(replacement_file):
                compilation_info = database.GetCompilationInfoForFile(
                    replacement_file)
                if compilation_info.compiler_flags_:
                    return compilation_info
        return None
    return database.GetCompilationInfoForFile(filename)


def FlagsForFile(filename, **kwargs):
    if database:
        # Bear in mind that compilation_info.compiler_flags_ does NOT return a
        # python list, but a "list-like" StringVec object
        compilation_info = GetCompilationInfoForFile(filename)
        if not compilation_info:
            return None

        final_flags = MakeRelativePathsInFlagsAbsolute(
            compilation_info.compiler_flags_,
            compilation_info.compiler_working_dir_)

        # NOTE: This is just for YouCompleteMe; it's highly likely that your project
        # does NOT need to remove the stdlib flag. DO NOT USE THIS IN YOUR
        # ycm_extra_conf IF YOU'RE NOT 100% SURE YOU NEED IT.
        try:
            final_flags.remove('-stdlib=libc++')
        except ValueError:
            pass
    else:
        relative_to = DirectoryOfThisScript()
        final_flags = MakeRelativePathsInFlagsAbsolute(flags, relative_to)

    return {
        'flags': final_flags,
        'do_cache': False
    }

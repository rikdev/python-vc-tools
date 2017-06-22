# coding: utf-8
"""Module/script to using Visual Studio C++ tools."""

import os
import subprocess
import sys


class VCTools:
    """Visual Studio environments keeper.

    This class look for installed Visual Studio toolset and downloads
    environment for it."""

    VERSIONS = {'2012': 11, '2013': 12, '2015': 14, '2017': 15}
    COMMANDS = [
        'check_call',
        'devenv',
        'msbuild',
        'nmake',
        'cl',
        'ml',
        'lib',
        'link',
    ]

    class VersionError(Exception):
        """The requested Visual Studio version is not supported."""
        pass

    class NotInstalledError(Exception):
        """The requested version of Visual Studio is not installed."""
        pass

    class PlatformError(Exception):
        """The requested target platform is not supported by Visual Studio."""
        pass

    def __init__(self, version_name=None, platform='x86'):
        """
        Args:
            version_name (str or None): Visual Studio version name ('2012',
                '2013', '2015', '2017', etc.). If None, it uses the most recent
                installed Visual Studio toolset (supported from this class, see
                VERSIONS)
            platform (str): Host_target platform ('x86', 'amd64', 'x86_amd64',
                'amd64_x86', etc.). This parameter passed to script
                vcvarsall.bat from Visual studio toolset.

        Raises:
            VersionError: The requested Visual Studio version is not supported.
            NotInstalledError: The requested version of Visual Studio is not
                installed.
            PlatformError: The requested target platform is not supported by
            Visual Studio.
        """

        # The environment variables that exposes by the script vcvarsall.bat
        # to launch the utility that comes with Visual Studio
        self.environ = None
        if version_name is not None:
            self.version_name = version_name
            version = self.VERSIONS.get(version_name)
            if version is None:
                raise self.VersionError('Visual Studio {} is not '
                                        'supported'.format(version_name))
            self.environ = self.__get_vsvars(version, platform)
        else:
            # search for the latest installed version of Visual Studio
            for item in sorted(self.VERSIONS.items(), reverse=True,
                               key=lambda version: version[1]):
                try:
                    self.version_name, version = item
                    self.environ = self.__get_vsvars(version,
                                                     platform)
                except (self.NotInstalledError, self.PlatformError):
                    continue
                break
        if self.environ is None:
            raise self.NotInstalledError('Visual Studio is not installed '
                                         'for target platform')

    def get_vc_install_dir(self):
        '''Returns the Visual C install directory.'''
        return self.environ['VCINSTALLDIR']

    def get_vs_install_dir(self):
        '''Returns the Visual Studio install directory.'''
        vs_install_dir = self.environ.get('VSINSTALLDIR')
        if not vs_install_dir:
            version = self.VERSIONS[self.version_name]
            vs_install_dir = self.__get_vs_install_dir(version)
        return vs_install_dir

    def get_target_platform(self):
        '''Returns the target platform name.'''
        return self.environ.get('PLATFORM', 'X86').upper()

    def check_call(self, *nargs, **kwargs):
        '''Run command with arguments (equivalent subprocess.check_call) in
        Visual Studio environment.'''

        if kwargs.get('env') is None:
            kwargs['env'] = self.environ
        kwargs['shell'] = True
        return subprocess.check_call(*nargs, **kwargs)

    def __get_vsvars(self, version, platform):
        vs_path = self.__get_vs_install_dir(version)
        if version < 15:
            vcvarsall_path = os.path.join(vs_path, 'VC', 'vcvarsall.bat')
        else:
            vcvarsall_path = os.path.join(vs_path, 'VC', 'Auxiliary', 'Build',
                                          'vcvarsall.bat')

        cmd = [vcvarsall_path, platform]
        # vcvarsall.bat always returns 0, but in case of error it out put error
        # message to the console
        popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        stdout_str = stdout.decode()
        if popen.returncode != 0 \
           or 'Error in script usage.' in stdout_str \
           or stderr:
            raise self.PlatformError('\n'.join([stdout_str,
                                                stderr.decode()]))

        return _get_environ(cmd)

    def __getattr__(self, name):
        if name not in self.COMMANDS:
            raise AttributeError(name)
        return lambda *n, **kw: self.__check_call_cmd(name, *n, **kw)

    def __check_call_cmd(self, cmd, cmd_args=None, *nargs, **kwargs):
        command = [cmd]
        if cmd_args is not None:
            command += cmd_args if isinstance(cmd_args, list) else [cmd_args]
        return self.check_call(command, *nargs, **kwargs)


    def __get_vs_install_dir(self, version):
        def find_vs_path_by_environ(version):
            vs_tools_env_name = 'VS{}0COMNTOOLS'.format(version)
            try:
                vs_tools_path = os.environ[vs_tools_env_name]
                return os.path.normpath(os.path.join(vs_tools_path, '..', '..'))
            except KeyError:
                pass
            return None

        def find_vs_path_by_registry(version):
            if sys.version_info >= (3, 0):
                import winreg as reg
                exception = FileNotFoundError
            else:
                import _winreg as reg
                exception = WindowsError

            sub_key = r'SOFTWARE\Microsoft\VisualStudio\SxS\VS7'
            try:
                with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, sub_key, 0,
                                 reg.KEY_QUERY_VALUE|reg.KEY_WOW64_32KEY) as key:
                    value_name = '{}.0'.format(version)
                    vs_path = reg.QueryValueEx(key, value_name)[0]
                    return os.path.normpath(vs_path)
            except exception:
                pass
            return None

        vs_install_dir = find_vs_path_by_environ(version)
        if not vs_install_dir:
            vs_install_dir = find_vs_path_by_registry(version)
        if not vs_install_dir:
            raise self.NotInstalledError("Can't find VisualStudio/{}."
                                         .format(version))
        return vs_install_dir


def _get_environ(args=None):
    """Returns the environment variables that the command exports to shell.

    Args:
        args (None, str, list): Command for calling. If None, then command not
            calling and returns environment variables for current application.

    Returns:
        map: Environment variables exported with the command
    """
    if args is not None:
        if not isinstance(args, list):
            args = [args]
        args += ['>', 'nul', '&&']
    args += ['set']

    popen = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.returncode != 0:
        raise subprocess.CalledProcessError(popen.returncode, ' '.join(args),
                                            output=stderr.decode('cp866'))
    result = {}
    for line in stdout.decode('cp866').splitlines():
        key, value = line.strip().split('=', 1)
        try:
            result[str(key).upper()] = str(value)
        except UnicodeEncodeError:
            pass
    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(add_help=True,
                                     description='Visual Studio C++ tools '
                                     'runner.')
    parser.add_argument('--version-name', '-v', default=None,
                        help='Visual Studio version')
    parser.add_argument('--target-platform', '-t', default='x86',
                        help='target platform')
    parser.add_argument('command', choices=VCTools.COMMANDS,
                        help='command [command arguments]')
    args, command_argv = parser.parse_known_args()

    tools = VCTools(args.version_name, args.target_platform)
    getattr(tools, args.command)(command_argv)

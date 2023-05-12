from conans.errors import ConanException


def msbuild_verbosity_cmd_line_arg(conanfile):
    if verbosity := conanfile.conf.get("tools.build:verbosity"):
        if verbosity not in (
            "quiet",
            "error",
            "warning",
            "notice",
            "status",
            "verbose",
            "normal",
            "debug",
            "v",
            "trace",
            "vv",
        ):
            raise ConanException(f"Unknown value '{verbosity}' for 'tools.build:verbosity'")
        # "Quiet", "Minimal", "Normal", "Detailed", "Diagnostic"
        verbosity = {
            "quiet": "Quiet",
            "error": "Minimal",
            "warning": "Minimal",
            "notice": "Minimal",
            "status": "Normal",
            "verbose": "Normal",
            "normal": "Normal",
            "debug": "Detailed",
            "v": "Detailed",
            "trace": "Diagnostic",
            "vv": "Diagnostic"
        }.get(verbosity)
        return f'/verbosity:{verbosity}'


def msbuild_arch(arch):
    return {'x86': 'x86',
            'x86_64': 'x64',
            'armv7': 'ARM',
            'armv8': 'ARM64'}.get(str(arch))


class MSBuild(object):
    """
    MSBuild build helper class
    """

    def __init__(self, conanfile):
        """
        :param conanfile: ``< ConanFile object >`` The current recipe object. Always use ``self``.
        """
        self._conanfile = conanfile
        #: Defines the build type. By default, ``settings.build_type``.
        self.build_type = conanfile.settings.get_safe("build_type")
        # if platforms:
        #    msvc_arch.update(platforms)
        arch = conanfile.settings.get_safe("arch")
        msvc_arch = msbuild_arch(arch)
        if conanfile.settings.get_safe("os") == "WindowsCE":
            msvc_arch = conanfile.settings.get_safe("os.platform")
        #: Defines the platform name, e.g., ``ARM`` if ``settings.arch == "armv7"``.
        self.platform = msvc_arch

    def command(self, sln, targets=None):
        """
        Gets the ``msbuild`` command line. For instance,
        :command:`msbuild "MyProject.sln" /p:Configuration=<conf> /p:Platform=<platform>`.

        :param sln: ``str`` name of Visual Studio ``*.sln`` file
        :param targets: ``targets`` is an optional argument, defaults to ``None``, and otherwise it is a list of targets to build
        :return: ``str`` msbuild command line.
        """
        # TODO: Enable output_binary_log via config
        cmd = f'msbuild "{sln}" /p:Configuration="{self.build_type}" /p:Platform={self.platform}'

        if verbosity := msbuild_verbosity_cmd_line_arg(self._conanfile):
            cmd += f" {verbosity}"

        if maxcpucount := self._conanfile.conf.get(
            "tools.microsoft.msbuild:max_cpu_count", check_type=int
        ):
            cmd += f" /m:{maxcpucount}"

        if targets:
            if not isinstance(targets, list):
                raise ConanException("targets argument should be a list")
            cmd += f' /target:{";".join(targets)}'

        return cmd

    def build(self, sln, targets=None):
        """
        Runs the ``msbuild`` command line obtained from ``self.command(sln)``.

        :param sln: ``str`` name of Visual Studio ``*.sln`` file
        :param targets: ``targets`` is an optional argument, defaults to ``None``, and otherwise it is a list of targets to build
        """
        cmd = self.command(sln, targets=targets)
        self._conanfile.run(cmd)

    @staticmethod
    def get_version(_):
        return NotImplementedError("get_version() method is not supported in MSBuild "
                                   "toolchain helper")

import os

from conan.tools.build import build_jobs
from conan.tools.meson.toolchain import MesonToolchain


class Meson(object):
    """
    This class calls Meson commands when a package is being built. Notice that
    this one should be used together with the ``MesonToolchain`` generator.
    """

    def __init__(self, conanfile):
        """
        :param conanfile: ``< ConanFile object >`` The current recipe object. Always use ``self``.
        """
        self._conanfile = conanfile

    def configure(self, reconfigure=False):
        """
        Runs ``meson setup [FILE] "BUILD_FOLDER" "SOURCE_FOLDER" [-Dprefix=PACKAGE_FOLDER]``
        command, where ``FILE`` could be ``--native-file conan_meson_native.ini``
        (if native builds) or ``--cross-file conan_meson_cross.ini`` (if cross builds).

        :param reconfigure: ``bool`` value that adds ``--reconfigure`` param to the final command.
        """
        source_folder = self._conanfile.source_folder
        build_folder = self._conanfile.build_folder
        generators_folder = self._conanfile.generators_folder
        cross = os.path.join(generators_folder, MesonToolchain.cross_filename)
        native = os.path.join(generators_folder, MesonToolchain.native_filename)
        meson_filenames = []
        if os.path.exists(cross):
            cmd_param = " --cross-file"
            meson_filenames.append(cross)
        else:
            cmd_param = " --native-file"
            meson_filenames.append(native)

        if machine_files := self._conanfile.conf.get(
            "tools.meson.mesontoolchain:extra_machine_files",
            default=[],
            check_type=list,
        ):
            meson_filenames.extend(machine_files)

        cmd = "meson setup" + "".join(
            [f'{cmd_param} "{meson_option}"' for meson_option in meson_filenames]
        )
        cmd += f' "{build_folder}" "{source_folder}"'
        if self._conanfile.package_folder:
            cmd += f' -Dprefix="{self._conanfile.package_folder}"'
        if reconfigure:
            cmd += ' --reconfigure'
        self._conanfile.output.info(f"Meson configure cmd: {cmd}")
        self._conanfile.run(cmd)

    def build(self, target=None):
        """
        Runs ``meson compile -C . -j[N_JOBS] [TARGET]`` in the build folder.
        You can specify ``N_JOBS`` through the configuration line ``tools.build:jobs=N_JOBS``
        in your profile ``[conf]`` section.

        :param target: ``str`` Specifies the target to be executed.
        """
        meson_build_folder = self._conanfile.build_folder
        cmd = f'meson compile -C "{meson_build_folder}"'
        if njobs := build_jobs(self._conanfile):
            cmd += f" -j{njobs}"
        if target:
            cmd += f" {target}"
        self._conanfile.output.info(f"Meson build cmd: {cmd}")
        self._conanfile.run(cmd)

    def install(self):
        """
        Runs ``meson install -C "."`` in the build folder. Notice that it will execute
        ``self.configure(reconfigure=True)`` at first.
        """
        self.configure(reconfigure=True)  # To re-do the destination package-folder
        meson_build_folder = self._conanfile.build_folder
        cmd = f'meson install -C "{meson_build_folder}"'
        self._conanfile.run(cmd)

    def test(self):
        """
        Runs ``meson test -v -C "."`` in the build folder.
        """
        if self._conanfile.conf.get("tools.build:skip_test", check_type=bool):
            return
        meson_build_folder = self._conanfile.build_folder
        cmd = f'meson test -v -C "{meson_build_folder}"'
        # TODO: Do we need vcvars for test?
        # TODO: This should use conanrunenv, but what if meson itself is a build-require?
        self._conanfile.run(cmd)

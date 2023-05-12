from conan.internal import check_duplicated_generator
from conan.tools.build import save_toolchain_args


class BazelToolchain(object):

    def __init__(self, conanfile, namespace=None):
        self._conanfile = conanfile
        self._namespace = namespace

    def generate(self):
        check_duplicated_generator(self, self._conanfile)
        content = {}
        if configs := ",".join(
            self._conanfile.conf.get(
                "tools.google.bazel:configs", default=[], check_type=list
            )
        ):
            content["bazel_configs"] = configs

        if bazelrc := self._conanfile.conf.get("tools.google.bazel:bazelrc_path"):
            content["bazelrc_path"] = bazelrc

        save_toolchain_args(content, namespace=self._namespace)

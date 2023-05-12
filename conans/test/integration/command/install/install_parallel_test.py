import textwrap
import unittest

from conans.test.utils.tools import GenConanfile, TestClient


class InstallParallelTest(unittest.TestCase):

    def test_basic_parallel_install(self):
        client = TestClient(default_server_user=True)
        threads = 4
        counter = 8

        client.save({"global.conf": f"core.download:parallel={threads}"},
                    path=client.cache.cache_folder)
        client.save({"conanfile.py": GenConanfile()})

        for i in range(counter):
            client.run(
                f"create . --name=pkg{i} --version=0.1 --user=user --channel=testing"
            )
        client.run("upload * --confirm -r default")
        client.run("remove * -c")

        # Lets consume the packages
        conanfile_txt = ["[requires]"]
        conanfile_txt.extend(f"pkg{i}/0.1@user/testing" for i in range(counter))
        conanfile_txt = "\n".join(conanfile_txt)

        client.save({"conanfile.txt": conanfile_txt}, clean_first=True)
        client.run("install .")
        self.assertIn(
            f"Downloading binary packages in {threads} parallel threads",
            client.out,
        )
        for i in range(counter):
            self.assertIn(f"pkg{i}/0.1@user/testing: Package installed", client.out)

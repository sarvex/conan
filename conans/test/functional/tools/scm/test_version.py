import textwrap

from conans.test.utils.tools import TestClient


def test_version():
    c = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.scm import Version

        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            settings = "compiler"
            def configure(self):
                v = Version(self.settings.compiler.version)
                assert v > "10"

                v = Version("1.2.3")
                self.output.warning(f"The major of 1.2.3 is {v.major}")
                self.output.warning(f"The minor of 1.2.3 is {v.minor}")
                self.output.warning(f"The patch of 1.2.3 is {v.patch}")
        """)
    c.save({"conanfile.py": conanfile})
    settings = "-s compiler=gcc -s compiler.libcxx=libstdc++11"
    c.run(f"create . {settings} -s compiler.version=11")
    assert "The major of 1.2.3 is 1" in c.out
    assert "The minor of 1.2.3 is 2" in c.out
    assert "The patch of 1.2.3 is 3" in c.out

    c.run(f"create . {settings} -s compiler.version=9", assert_error=True)

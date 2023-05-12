import textwrap

from conan.tools.cmake.cmakedeps.templates import CMakeDepsFileTemplate

"""
    foo-config-version.cmake

"""


class ConfigVersionTemplate(CMakeDepsFileTemplate):

    @property
    def filename(self):
        if self.file_name == self.file_name.lower():
            return f"{self.file_name}-config-version.cmake"
        else:
            return f"{self.file_name}ConfigVersion.cmake"

    @property
    def context(self):
        return {"version": self.conanfile.ref.version}

    @property
    def template(self):
        return textwrap.dedent(
            """
            set(PACKAGE_VERSION "{{ version }}")

            if(PACKAGE_VERSION VERSION_LESS PACKAGE_FIND_VERSION)
                set(PACKAGE_VERSION_COMPATIBLE FALSE)
            else()
                if("{{ version }}" MATCHES "^([0-9]+)\\\\.")
                    set(CVF_VERSION_MAJOR {{ '${CMAKE_MATCH_1}' }})
                else()
                    set(CVF_VERSION_MAJOR "{{ version }}")
                endif()

                if(PACKAGE_FIND_VERSION_MAJOR STREQUAL CVF_VERSION_MAJOR)
                    set(PACKAGE_VERSION_COMPATIBLE TRUE)
                else()
                    set(PACKAGE_VERSION_COMPATIBLE FALSE)
                endif()

                if(PACKAGE_FIND_VERSION STREQUAL PACKAGE_VERSION)
                    set(PACKAGE_VERSION_EXACT TRUE)
                endif()
            endif()
            """
        )

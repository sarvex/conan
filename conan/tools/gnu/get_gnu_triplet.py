from conans.errors import ConanException


def _get_gnu_triplet(os_, arch, compiler=None):
    """
    Returns string with <machine>-<vendor>-<op_system> triplet (<vendor> can be omitted in practice)

    :param os_: os to be used to create the triplet
    :param arch: arch to be used to create the triplet
    :param compiler: compiler used to create the triplet (only needed fo windows)
    """

    if os_ == "Windows" and compiler is None:
        raise ConanException("'compiler' parameter for 'get_gnu_triplet()' is not specified and "
                             "needed for os=Windows")

    # Calculate the arch
    machine = {"x86": "i686" if os_ != "Linux" else "x86",
               "x86_64": "x86_64",
               "armv8": "aarch64",
               "armv8_32": "aarch64",  # https://wiki.linaro.org/Platform/arm64-ilp32
               "armv8.3": "aarch64",
               "asm.js": "asmjs",
               "wasm": "wasm32",
               }.get(arch, None)

    if not machine:
        # https://wiki.debian.org/Multiarch/Tuples
        if os_ == "AIX":
            if "ppc32" in arch:
                machine = "rs6000"
            elif "ppc64" in arch:
                machine = "powerpc"
        elif "arm" in arch:
            machine = "arm"
        elif "ppc32be" in arch:
            machine = "powerpcbe"
        elif "ppc64le" in arch:
            machine = "powerpc64le"
        elif "ppc64" in arch:
            machine = "powerpc64"
        elif "ppc32" in arch:
            machine = "powerpc"
        elif "mips64" in arch:
            machine = "mips64"
        elif "mips" in arch:
            machine = "mips"
        elif "sparcv9" in arch:
            machine = "sparc64"
        elif "sparc" in arch:
            machine = "sparc"
        elif "s390x" in arch:
            machine = "s390x-ibm"
        elif "s390" in arch:
            machine = "s390-ibm"
        elif "sh4" in arch:
            machine = "sh4"
        elif "e2k" in arch:
            # https://lists.gnu.org/archive/html/config-patches/2015-03/msg00000.html
            machine = "e2k-unknown"

    if machine is None:
        raise ConanException("Unknown '%s' machine, Conan doesn't know how to "
                             "translate it to the GNU triplet, please report at "
                             " https://github.com/conan-io/conan/issues" % arch)

    # Calculate the OS
    windows_op = "w64-mingw32" if compiler == "gcc" else "unknown-windows"
    op_system = {"Windows": windows_op,
                 "Linux": "linux-gnu",
                 "Darwin": "apple-darwin",
                 "Android": "linux-android",
                 "Macos": "apple-darwin",
                 "iOS": "apple-ios",
                 "watchOS": "apple-watchos",
                 "tvOS": "apple-tvos",
                 # NOTE: it technically must be "asmjs-unknown-emscripten" or
                 # "wasm32-unknown-emscripten", but it's not recognized by old config.sub versions
                 "Emscripten": "local-emscripten",
                 "AIX": "ibm-aix",
                 "Neutrino": "nto-qnx"}.get(os_, os_.lower())

    if os_ in ("Linux", "Android"):
        if "arm" in arch and "armv8" not in arch:
            op_system += "eabi"

        if arch in ["armv5hf", "armv7hf"] and os_ == "Linux":
            op_system += "hf"

        if arch == "armv8_32" and os_ == "Linux":
            op_system += "_ilp32"  # https://wiki.linaro.org/Platform/arm64-ilp32

    return f"{machine}-{op_system}"

import argparse, os, string, logging, tempfile, glob, shutil, errno, io, sys
from string import Template


logging.basicConfig(level=logging.WARNING, format="packaging(%(levelname)s): %(message)s")
logger = logging.getLogger('packaging')


# Copy the platforms that match the pattern to the staging directory
# template the wrapper CMake script to provide platform and dep name
# Zip the resulting package and put it somewhere

class MyTemplate(Template):
    delimiter = '@'


def generate_script(keyword_map, in_script_path, out_script_path):
    """
    :type keyword_map: dict
    :type in_script_path: str
    :type out_script_path: str
    :rtype: None
    """
    # we have to be careful in how we do this to preserve the different newline styles of script files
    # (linux_mac vs dos)
    with io.open(in_script_path, 'r', newline='') as file:
        lines = file.readlines()
    with io.open(out_script_path, 'w', newline='') as file:
        lines_out = []
        for line in lines:
            line_out = MyTemplate(line).safe_substitute(keyword_map)
            lines_out.append(line_out)

        file.writelines(lines_out)


def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Creates Packman packages out of CMake install builds")

    parser.add_argument("rootdir", help="The root directory where all of the install targets are built to.")
    parser.add_argument("platform",
                        help="The platforms you want to include in this package. A wildcard * will be added to the end "
                             "to match them. Example: vc14win")
    parser.add_argument("package", help="The root name of the package, Example: pxshared")
    parser.add_argument("version", help="Version number to give to the package")
    parser.add_argument("script", help="The location of the wrapper script to template and include in the package")
    parser.add_argument("versionscript",
                        help="The location of the version script to template and include in the package. It will be "
                             "templated with the version specified.")

    parser.add_argument("-o", "--output-dir", dest="output_dir",
                        help="The directory to write output package to. If not provided, current working directory "
                             "will be used.")

    parser.add_argument("-s", "--staging-dir", dest="staging_dir", help="The directory to stage the package into. If not provided, a temporary directory will be used.")

    args = parser.parse_args(argv)

    # if stagingdir provided, check it exists.

    if not args.staging_dir:
        stagingdir = tempfile.mkdtemp()
    else:
        stagingdir = args.staging_dir

    # Sanity check, rootdir exists?

    if not os.path.isdir(args.rootdir):
        print "Rootdir path '%s' doesn't seem to exist." % args.rootdir
        exit(1)

    # Sanity check - more than one platform matches?

    dirs = glob.glob("%s\%s*" % (args.rootdir, args.platform))

    if len(dirs) < 2:
        print "Only %d directories matched '%s\%s*' - need at least two for this script." % (len(dirs), args.rootdir,
                                                                                             args.platform)
        exit(1)

    # Script template exists?

    if not os.path.isfile(args.script):
        raise RuntimeError("Script '%s' doesn't seem to exist." % args.script)

    # Version script template exists?

    if not os.path.isfile(args.versionscript):
        raise RuntimeError("Version script '%s' doesn't seem to exist." % args.versionscript)

    # TODO: Script template has keys?
    key_map = {'PLATFORM_NAME': args.platform, 'DEPENDENCY_NAME': args.package}

    # TODO: Version number meets CMake standards!
    version_parts = args.version.split(".")

    if len(version_parts) > 4:
        raise RuntimeError("CMake packages can only have up to 4 version numbers - major[.minor[.patch[.tweak]]]")

    # Now, any non-numeric characters in any parts?
    for part in version_parts:
        if not part.isdigit():
            raise RuntimeError("CMake Version parts may only contain numbers. '%s' is not valid." % part)

    # Create the new package directory in the staging directory

    new_package_name = args.package + "-" + args.platform

    package_version_path = os.path.join(stagingdir, new_package_name, args.version)

    tl_cmake_dir = os.path.join(package_version_path, "cmake")

    try:
        os.makedirs(tl_cmake_dir)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise

    platforms_dir = os.path.join(package_version_path, "platforms")

    try:
        os.makedirs(platforms_dir)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise

    # Now copy over the platforms, making sure to delete them if they're already there (we didn't clean up!)
    for dir in dirs:
        current_platform = os.path.basename(dir)
        print "Current platform: %s from %s" % (current_platform, dir)
        dest_dir = os.path.join(platforms_dir, current_platform)

        print "Copying %s to %s" % (dir, dest_dir)
        copy_and_overwrite(dir, dest_dir)

    # After this point, package needs to be lowercase
    args.package = args.package.lower()

    key_map = {'PLATFORM_NAME': args.platform, 'DEPENDENCY_NAME': args.package}

    outputscript = os.path.join(tl_cmake_dir, "%s-config.cmake" % args.package)

    generate_script(key_map, args.script, outputscript)

    # We'll be ignoring the version.cmake files in the individual platforms, as they might not be the same as what the
    # user is specifying here. Instead we'll template our own.

    key_map = {'PACKAGE_VERSION': args.version}

    versionscript = os.path.join(tl_cmake_dir, "%s-config-version.cmake" % args.package)

    generate_script(key_map, args.versionscript, versionscript)

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.getcwd()

    pack(package_version_path, output_dir)

    # Don't delete the manually specified staging dir
    if not args.staging_dir:
        shutil.rmtree(stagingdir)


def pack(version_path, output_path):
    my_dir = os.path.dirname(os.path.realpath(__file__))
    packman_dir = os.path.join(my_dir, '..', 'packman')
    sys.path.append(packman_dir)
    import packmanapi
    packmanapi.pack(version_path, output_path)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error(exc.message)
        exit(1)

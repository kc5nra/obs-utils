import subprocess
import os
import re
import props

def exec_cmd(*cmd):
    return subprocess.check_output(cmd)

def cmd(cmd):
    return subprocess.check_output(cmd.split(' ')).rstrip('\r\n')


# committedVersionNumber=00.55.04
# committedVersionName=Open Broadcaster Software v0.554b
# branch=stable
# commitSHA1=800823c60f16ac4a0357e76c515b6d2aa906d3e3
# commitSHA1Abbrev=800823c
# commitCount=1481
# commitDate=2013-08-31 09\:38\:48 -0700
# committer=jp9000

def gen_commit(branch):

    commit_count = cmd('git rev-list HEAD --count')
    commit_sha1 = cmd('git show -s --format=%H')
    commit_sha1_abbrev = cmd('git show -s --format=%h')
    commit_date = cmd('git show -s --format=%ai')
    committer = cmd('git show -s --format=%an')


    vfile = open('Source/Main.h')
    vfile_contents = vfile.read()
    vfile.close()

    ver_num_match = re.search(r'#define\s+OBS_VERSION\s+[0][x]([\d]{2})([\d]{2})([\d]{2})', vfile_contents)
    if not len(ver_num_match.groups()) == 3:
        print "could not find version number in Source/Main.h"
        exit(1)

    committed_version_number = ".".join(ver_num_match.groups())

    ver_name_match = re.search(r'#define\s+OBS_VERSION_STRING_RAW\s+[\"](.*)?["]', vfile_contents)
    if not len(ver_name_match.groups()):
        print "could not find version name in Source/Main.h"
        exit(1)

    committed_version_name = ver_name_match.group(1)

    return {
        'committedVersionNumber': committed_version_number,
        'committedVersionName': committed_version_name,
        'branch': branch,
        'commitSHA1': commit_sha1,
        'commitSHA1Abbrev': commit_sha1_abbrev,
        'commitCount': commit_count,
        'commitDate': commit_date,
        'committer': committer
    }

def obs_build(arch, build_def, multi):
    mt = '/m' if multi else ''
    build_cmd = [
        'msbuild OBS-All.sln /t:Clean;Build',
        '/p:Configuration=Release;Platform={0}',
        '/p:DynamicDefines="{1}" {2}'
    ]

    if os.system(build_cmd.format(arch, build_def, mt)):
        exit(1)

def gen_build_def(commit):
    defs = [
        'MANIFEST_WITH_ARCHIVES=1',
        'MANIFEST_PATH="/updates/org.catchexception.builds.xconfig"',
        'MANIFEST_URL="https://builds.catchexception.org/update.json"',
        'UPDATE_PATH="/updates/org.catchexception.builds.updater.exe"',
        'UPDATE_CHANNEL="'+commit['branch']+'"',
        'OBS_VERSION_SUFFIX=" ('+commit['branch']+'/'+commit['commitSHA1Abbrev']+')"'
    ]
    return ";".join(defs).replace('"', r'\"')


from os import path, errno

def mkdir(dirname):
    try:
        os.makedirs(dirname)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

def zip(zip_path, name):
    _7z = path.join(path.dirname(path.realpath(__file__)), "7z")
    zip_cmd = '{0} a {1} {2} > NUL'.format(_7z, name, path.join(path.abspath(zip_path), "*"))
    if os.system(zip_cmd):
        print 'failed to zip: '+zip_cmd
        exit(1)

def zip_release(arch, commit):


    name = path.join('archives', props.file_path(commit, arch))
    mkdir(path.dirname(name))

    print "zipping "+name
    if arch == 'x86':
        zip('installer/32bit', name)
    else:
        zip('installer/64bit', name)

def obs_pkg(commit):
    import shutil
    import glob
    # clean
    shutil.rmtree('archives')
    shutil.rmtree('installer/32bit')
    shutil.rmtree('installer/64bit')
    # clean up archives
    for f in glob.glob("*.7z"):
        os.remove(f)

    os.system("cd installer && generate_binaries_test")

    zip_release('x86', commit)
    zip_release('x64', commit)
    f = open(path.join('archives', props.archive_path(commit)), 'w')
    f.writelines(['{0}={1}\n'.format(k, props.val_escape(v)) for k, v in commit.items()])
    f.close()

import argparse
parser = argparse.ArgumentParser(description='ce.org builds xml gen')
parser.add_argument('-b', '--branch', dest='branch', required=True)
parser.add_argument('-p', '--package-only', dest='package_only', required=False, action='store_true', default=False)
parser.add_argument('-m', '--multithreaded', dest='multi', required=False, action='store_true', default=False)
args = parser.parse_args()

commit = gen_commit(args.branch)
build_def = gen_build_def(commit)

if not args.package_only:
    obs_build('win32', build_def, args.multi)
    obs_build('x64', build_def, args.multi)

obs_pkg(commit)



import fnmatch
import os

import argparse
parser = argparse.ArgumentParser(description='ce.org builds xml gen')
parser.add_argument('-d', '--root-dir', dest='root', default='.')
parser.add_argument('-o', '--out-file', dest='out', default='builds.xml')

args = parser.parse_args()

def prop_val_unescape(propval):
    return propval.replace(r'\:', ':').replace(r'\=', '=')

def read_prop(prop_name):
    prop_file = open(prop_name)
    prop_array = prop_file.readlines()
    props = dict()
    for l in prop_array:
        l = l.rstrip('\r\n')

        if l.lstrip(' ').startswith('#'):
            continue  # comment

        pair = l.split('=', 1)

        if (len(pair) != 2):
            continue  # not prop

        props[pair[0]] = prop_val_unescape(pair[1])
    return props

from collections import defaultdict
branches = defaultdict(list)

print 'gen build structure in \''+args.root+'\''

for root, dirs, files in os.walk(args.root):
    for name in fnmatch.filter(files, 'archive.properties'):
        p = read_prop(os.path.join(root, name))
        branches[p['branch']].append(p)

from xml.etree import ElementTree as ET

def gen_file_name(prop, arch):
    return 'OBS-'+prop['committedVersionNumber']+'-'+prop['commitSHA1Abbrev']+'-'+arch+'.7z'

def gen_rev_dir(prop):
    return prop['commitCount']+'-'+prop['committedVersionNumber']

def gen_file_path(prop, arch):
    return prop['branch']+'/'+gen_rev_dir(prop)+'/'+gen_file_name(prop,arch)

def gen_rev_attr(prop, arch):
    return {
        'blame': prop['committer'],
        'commitSHA1': prop['commitSHA1'],
        'commitSHA1Abbrev': prop['commitSHA1Abbrev'],
        'date': prop['commitDate'],
        'name': gen_file_name(prop, arch),
        'obsBuildNumber': prop['commitCount'],
        'obsDir': gen_rev_dir(prop),
        'obsVersion': prop['committedVersionNumber'],
        'obsVersionName': prop['committedVersionName']
    }

def gen_bin_attr(prop, arch):
    return {
        'link': gen_file_path(prop, arch),
        'name': gen_file_name(prop, arch),
        'size': str(os.path.getsize(gen_file_path(prop, arch)))
    }

branchesEle = ET.Element('branches')
for k, v in branches.items():
    bEle = ET.SubElement(branchesEle, 'branch', { 'name': k})
    w32 = ET.SubElement(bEle, 'win')
    w64 = ET.SubElement(bEle, 'win64')
    for p in v:  # snicker
        r32 = ET.SubElement(w32, 'revision', gen_rev_attr(p, 'x86'))
        ET.SubElement(r32, 'binary', gen_bin_attr(p, 'x86'))
        r64 = ET.SubElement(w64, 'revision', gen_rev_attr(p, 'x64'))
        ET.SubElement(r64, 'binary', gen_bin_attr(p, 'x64'))

ET.dump(branchesEle)





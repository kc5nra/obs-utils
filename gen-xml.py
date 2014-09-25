import fnmatch
import os
import props

def gen_rev_attr(prop, arch):
    return {
        'blame': prop['committer'],
        'commitSHA1': prop['commitSHA1'],
        'commitSHA1Abbrev': prop['commitSHA1Abbrev'],
        'date': prop['commitDate'],
        'name': props.file_name(prop, arch),
        'obsBuildNumber': prop['commitCount'],
        'obsDir': props.rev_dir(prop),
        'obsVersion': prop['committedVersionNumber'],
        'obsVersionName': prop['committedVersionName']
    }

def gen_bin_attr(prop, arch):
    return {
        'link': props.file_path(prop, arch),
        'name': props.file_name(prop, arch),
        'size': str(os.path.getsize(props.file_path(prop, arch)))
    }

def gen_xml(root_dir, out):
    from collections import defaultdict
    branches = defaultdict(list)

    for root, dirs, files in os.walk(root_dir):
        for name in fnmatch.filter(files, 'archive.properties'):
            p = props.read_from_file(os.path.join(root, name))
            branches[p['branch']].append(p)

    from xml.etree import ElementTree as ET

    branches_ele = ET.Element('branches')
    for k, v in branches.items():
        bEle = ET.SubElement(branches_ele, 'branch', { 'name': k})
        w32 = ET.SubElement(bEle, 'win')
        w64 = ET.SubElement(bEle, 'win64')
        for p in v:  # snicker
            r32 = ET.SubElement(w32, 'revision', gen_rev_attr(p, 'x86'))
            ET.SubElement(r32, 'binary', gen_bin_attr(p, 'x86'))
            r64 = ET.SubElement(w64, 'revision', gen_rev_attr(p, 'x64'))
            ET.SubElement(r64, 'binary', gen_bin_attr(p, 'x64'))

    with open(out, 'w') as output:
        output.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        output.write('<?xml-stylesheet type="text/xsl" href="assets/obsbuilds.xsl"?>')
        ET.ElementTree(branches_ele).write(output, xml_declaration=False, encoding='utf-8')


import argparse
parser = argparse.ArgumentParser(description='ce.org builds xml gen')
parser.add_argument('-d', '--root-dir', dest='root', default='.')
parser.add_argument('-o', '--out-file', dest='out', default='builds.xml')
args = parser.parse_args()

gen_xml(args.root, args.out)







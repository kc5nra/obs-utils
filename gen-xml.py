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

def hash(fp):
    import hashlib
    m = hashlib.sha1()
    with open(fp, 'rb') as f:
        m.update(f.read())
    return m.hexdigest()

def gen_update_arch_attr(prop, arch):
    return {
        'sha1': hash(props.file_path(prop, arch)),
        'version': ' ({0}/{1})'.format(prop['branch'], prop['commitSHA1Abbrev']),
        'url': 'http://builds.catchexception.org/'+props.file_path(prop, arch),
        'file': props.file_name(prop, arch)
    }

def gen_update_attr(prop):
    return {
        'win': gen_update_arch_attr(prop, 'x86'),
        'win64': gen_update_arch_attr(prop, 'x64')
    }

def gen_bin_attr(prop, arch):
    return {
        'link': props.file_path(prop, arch),
        'name': props.file_name(prop, arch),
        'size': str(os.path.getsize(props.file_path(prop, arch)))
    }

def gen_xml(root_dir, out, update_out):
    from collections import defaultdict
    branches = defaultdict(list)
    update = {}

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
        
        latest = -1
        
        for p in v:  # snicker
            current = int(p['commitCount'])
            if current > latest:
                 latest = current
                 update[k] = p
            
            r32 = ET.SubElement(w32, 'revision', gen_rev_attr(p, 'x86'))
            ET.SubElement(r32, 'binary', gen_bin_attr(p, 'x86'))
            r64 = ET.SubElement(w64, 'revision', gen_rev_attr(p, 'x64'))
            ET.SubElement(r64, 'binary', gen_bin_attr(p, 'x64'))

        if latest:
            update[k] = gen_update_attr(update[k])

    with open(out, 'w') as output:
        output.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        output.write('<?xml-stylesheet type="text/xsl" href="assets/obsbuilds.xsl"?>')
        ET.ElementTree(branches_ele).write(output, encoding='utf-8')

    update['updater'] = {
        'sha1': hash('org.catchexception.builds.updater.exe'),
        'url': 'http://builds.catchexception.org/org.catchexception.builds.updater.exe'
    }
	
    import time
    update['updated'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    import json
    update_json = json.dumps(update, indent=4)
    with open(update_out, 'w') as f:
    	print >> f, update_json 

import argparse
parser = argparse.ArgumentParser(description='ce.org builds xml gen')
parser.add_argument('-d', '--root-dir', dest='root', default='.')
parser.add_argument('-o', '--out-file', dest='out', default='builds.xml')
parser.add_argument('-u', '--update-out-file', dest='up_out', default='update.json')
args = parser.parse_args()

gen_xml(args.root, args.out, args.up_out)


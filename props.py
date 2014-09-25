def val_unescape(propval):
    return propval.replace(r'\:', ':').replace(r'\=', '=')

def val_escape(propval):
    return propval.replace(':', r'\:').replace('=', r'\=')

def read_from_file(prop_name):
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

        props[pair[0]] = val_unescape(pair[1])
    return props

def file_name(prop, arch):
    return 'OBS-'+prop['committedVersionNumber']+'-'+prop['commitSHA1Abbrev']+'-'+arch+'.7z'

def rev_dir(prop):
    return prop['commitCount']+'-'+prop['committedVersionNumber']

def file_path(prop, arch):
    return prop['branch']+'/'+rev_dir(prop)+'/'+file_name(prop,arch)
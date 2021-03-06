import py, re, os, signal, time, commands
from subprocess import Popen, PIPE

mod_re = (r"\bmodule\s+(", r")\s*\(\s*")
func_re = (r"\bfunction\s+(", r")\s*\(")
pydef_re = (r"\bdef\s+(", r")\s*\(")

def extract_definitions(fpath, name_re=r"\w+", def_re=""):
    regex = name_re.join(def_re)
    matcher = re.compile(regex)
    return (m.group(1) for m in matcher.finditer(fpath.read()))

def extract_mod_names(fpath, name_re=r"\w+"):
    return extract_definitions(fpath, name_re=name_re, def_re=mod_re)

def extract_func_names(fpath, name_re=r"\w+"):
    return extract_definitions(fpath, name_re=name_re, def_re=func_re)

def extract_def_names(fpath, name_re=r"\w+"):
    return extract_definitions(fpath, name_re=name_re, def_re=pydef_re)

def collect_test_modules(dirpath=None):
    dirpath = dirpath or py.path.local("./")
    print "Collecting openscad test module names"

    test_files = {}
    for fpath in dirpath.visit('*.py'):
	if not fpath.basename in ['openscadpy_testing.py', 'openscadpy_utils.py', 'test_docs.py', 'test_mcadpy.py']:
	        defs = extract_def_names(fpath, r"test\w*")
	        test_files[fpath] = defs
    return test_files

class Timeout(Exception): pass

def call_openscad(path, stlpath, timeout=35):
    command = ['openscadpy', '-s', str(stlpath),  str(path)]
    print command
    if timeout:
        try:
            proc = Popen(command,
                stdout=PIPE, stderr=PIPE, close_fds=True)
            calltime = time.time()
            time.sleep(0.05)
            #print calltime
            while True:
                if proc.poll() is not None:
                    break
                time.sleep(0.5)
                #print time.time()
                if time.time() > calltime + timeout:
                    raise Timeout()
        finally:
            try:
                proc.terminate()
                proc.kill()
            except OSError:
                pass

        return (proc.returncode,) + proc.communicate()
    else:
        output = commands.getstatusoutput(" ".join(command))
        return output + ('', '')

def parse_output(text):
    pass

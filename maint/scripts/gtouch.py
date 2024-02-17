#!/usr/bin/python3
#-*- coding: ISO-8859-1 -*-
#
# (c)2020, 2022  Henrique Moreira

"""
List and Touches git repositories!
"""

###
### See also ghelp.test.py (tester of 'ghelp')
###

# pylint: disable=unused-argument, invalid-name

import sys
import git
from ghelper.ghelp import run_list, run_touch, run_detail
from ghelper.pgit import GRepo, working_dir
from tconfig.archs import dirs

REPO_SAMPLE_NAME = "anyrepo"


def main(args):
    """Just basic module tests.
    """
    param = []
    if args:
        cmd = args[0]
        param = args[1:]
        code = run_main(cmd, param)
    else:
        code = None
    if code is None:
        print("""gtouch.py command [options]

Commands are:
   ls       Directory listing (similar to 'ls -1F -a')

   list     List files

   touch    Touch files

   detail   Details of repository (log)

Options:
   --verbose      Verbose output
   --dry-run      Show what the command would do (but does not do it)
   --r            (Only for 'touch')
""")
    sys.exit(code if code else 0)


def run_main(cmd, args, debug=0):
    """ Main run! """
    out_file = sys.stdout
    err_file = sys.stderr
    name = REPO_SAMPLE_NAME
    param = args
    opts = {
        "r": False,  # Recursive
        "dry-run": False,
        "verbose": 0,
    }
    default_dir = working_dir()
    assert default_dir

    if cmd == "list":
        if not param:
            param = [default_dir]
        where = param[0]
        del param[0]
        rpl = new_repo(err_file, where, name)
        code, _ = run_list(out_file, err_file, rpl, param, debug=debug)
        return code
    if cmd == "touch":
        while param and param[0].startswith("-"):
            if param[0] == "--dry-run":
                del param[0]
                opts["dry-run"] = True
                continue
            if param[0] in ("-v", "--verbose",):
                del param[0]
                opts["verbose"] += 1
                continue
            if param[0] in ("-r", "--recursive",):
                del param[0]
                opts["r"] += 1
                continue
            return None
        if param:
            where = param[0]
            del param[0]
            if param:
                return None
        else:
            where = default_dir
        opt_list = [opts["verbose"], 0]
        rpl = new_repo(err_file, where, name)
        code, queue = run_list(None, err_file, rpl, opt_list, debug=debug)
        if code:
            return code
        run_touch(out_file, err_file, rpl, queue, opts)
        return code
    if cmd == "detail":
        if param == []:
            param = [default_dir]
        where = param[0]
        del param[0]
        rpl = new_repo(err_file, where, name)
        code = run_detail(err_file, rpl, param, debug=debug)
        return code
    if cmd == "ls":
        if param == []:
            param = [default_dir]
        code = do_ls(out_file, err_file, param)
        return code
    return None


def new_repo(err_file, where, name, ret_error=2):
    """ Function to return GRepo, but handles exception if repository does not exist.
    """
    assert isinstance(ret_error, int)
    try:
        repo_obj = GRepo(where, name)
    except git.InvalidGitRepositoryError:
        repo_obj = None
    if repo_obj is not None:
        return repo_obj
    err_file.write(f"Invalid repo: {where}\n")
    sys.exit(ret_error)


def do_ls(out_file, err_file, params, debug=0):
    """ Simple ls (directory listing)
    """
    code = 0
    param, do_all = params, False
    if param[0] == '-a':
        do_all = True
        del param[0]
    for path in param:
        if path.startswith("-"):
            return 4
    for path in param:
        if do_all:
            mask = None
        else:
            mask = 0
        di = dirs.DirList(path, mask)
        di.get_dir(path)
        di.sort()
        for f in di.folders:
            out_file.write("{}/\n".format(f))
        for f in di.entries:
            out_file.write("{}\n".format(f))
    if debug > 0:
        print("""
Debug:
{}
<<<"""
              "".format(di))
    return code


#
# Main script
#
if __name__ == "__main__":
    main(sys.argv[1:])

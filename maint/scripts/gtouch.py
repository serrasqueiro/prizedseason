# (c)2020  Henrique Moreira (h@serrasqueiro.com)

"""
List and Touches git repositories!
"""

###
### See also ghelp.test.py (tester of 'ghelp')
###

# pylint: disable=no-else-return, invalid-name

import sys
import git
from ghelper.ghelp import run_list, run_touch, run_detail
from ghelper.pgit import GRepo, working_dir

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
   list     List files

   touch    Touch files

   details  Details of repository (log)

Options:
   --dry-run      Show what the command would do (but does not do it)
""")
        code = 0
    sys.exit(code)


def run_main(cmd, args, debug=0):
    """ Main run! """
    out_file = sys.stdout
    err_file = sys.stderr
    name = REPO_SAMPLE_NAME
    param = args
    opts = {"dry-run": False,
            }
    default_dir = working_dir()
    assert default_dir

    if cmd == "list":
        if param == []:
            param = [default_dir]
        where = param[0]
        del param[0]
        rp = new_repo(err_file, where, name)
        code, _ = run_list(out_file, err_file, rp, param, debug=debug)
        return code
    elif cmd == "touch":
        if param:
            if param[0] == "--dry-run":
                opts["dry-run"] = True
                del param[0]
        else:
            param = [default_dir]
        where = param[0]
        del param[0]
        rp = new_repo(err_file, where, name)
        code, queue = run_list(None, err_file, rp, param, debug=debug)
        if code == 0:
            run_touch(out_file, err_file, rp, queue, opts)
        return code
    elif cmd == "detail":
        if param == []:
            param = [default_dir]
        where = param[0]
        del param[0]
        rp = new_repo(err_file, where, name)
        code = run_detail(err_file, rp, param, debug=debug)
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
    if repo_obj:
        return repo_obj
    err_file.write("Invalid repo: {}\n".format(where))
    sys.exit(ret_error)


#
# Main script
#
if __name__ == "__main__":
    main(sys.argv[1:])

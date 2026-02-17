import argparse # Handles command-line arguments
import configparser
from datetime import datetime # For saving the date and time when making commits
import grp, pwd # To get owner/group ID of files
from fnmatch import fnmatch # To match filenames
import hashlib # To use SHA-1
from math import ceil
import os
import re
import sys
import zlib # For compressing 


class GitRepository(object):
    """A git repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")
        
        # Before creating a repo object it checks first if there is a .git dir
        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository {path}")

        # Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion: {vers}")


argparser = argparse.ArgumentParser(description="The stupidest content tracker") 

# To handle subcommands in git: init, add, status etc.
# dest returns the name of the subparser in a field called "command"
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")

# We're telling it that git must have a subcommand like: git COMMAND and not just git
argsubparsers.required = True

argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository")

def main(argv=sys.argv[1:]): # We're removing the filename inside of the sys.argv list
    args = argparser.parse_args(argv)

    match args.command:
        case "add"          : cmd_add(args)
        case "cat-file"     : cmd_cat_file(args)
        case "check-ignore" : cmd_check_ignore(args)
        case "checkout"     : cmd_checkout(args)
        case "commit"       : cmd_commit(args)
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        case "log"          : cmd_log(args)
        case "ls-files"     : cmd_ls_files(args)
        case "ls-tree"      : cmd_ls_tree(args)
        case "rev-parse"    : cmd_rev_parse(args)
        case "rm"           : cmd_rm(args)
        case "show-ref"     : cmd_show_ref(args)
        case "status"       : cmd_status(args)
        case "tag"          : cmd_tag(args)
        case _              : print("Bad command.")


def repo_path(repo, *path):
    """Returns the combined .git directory and *paths path"""
    return os.path.join(repo.gitdir, *path)


def repo_file(repo, *path, mkdir=False):
    """
    Same as repo_path, but create dirname(*path) if absent. For
    example, repo_file(r, \"refs\", \"remotes\", \"origin\", \"HEAD\") will
    create .git/refs/remotes/origin
    """

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir"""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None

def repo_create(path):
    """Create a new repository at path"""

    repo = GitRepository(path, True)

    # Checks if the path doesn't exist or an empty directory

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is not empty")
    else:
        os.makedirs(repo.worktree)

    # Creates the other subdirectories inside of .git
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # creates the .git/description file
    with open(repo_file(repo, "description"), "w") as f:
        f.write("refs: refs/heads/master\n")
        

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")


    return ret

def cmd_init(args):
    repo_create(args.path)



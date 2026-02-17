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

argparser = argparse.ArgumentParser(description="The stupidest content tracker") 

# To handle subcommands in git: init, add, status etc.
# dest returns the name of the subparser in a field called "command"
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")

# We're telling it that git must have a subcommand like: git COMMAND and not just git
argsubparsers.required = True

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




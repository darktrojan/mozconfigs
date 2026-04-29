#!/usr/bin/python3
import json
import os
import subprocess


def a_hook(ui, repo, **kwargs):
    root = repo.root.decode()
    rev = kwargs["opts"][b"rev"]

    if rev == []:
        print("No revision specified")
        return True

    pushing_to_try = b"try" in kwargs["pats"] or b"try-comm" in kwargs["pats"]
    artifact_build = False

    status = repo.status(unknown=True)
    if len(status.added) or len(status.modified) or len(status.removed):
        print("Uncommitted changes:")
        print("\n".join([f.decode() for f in status.added + status.modified + status.removed]))
        return True

    if pushing_to_try and b"try_task_config.json" in status.unknown:
        print("try_task_config.json not added to revision")
        return True

    task_config_path = os.path.join(root, "try_task_config.json")
    if os.path.isfile(task_config_path):
        if pushing_to_try:
            with open(task_config_path) as fp:
                try:
                    j = json.load(fp)
                    if "use-artifact-builds" in j and j["use-artifact-builds"]:
                        artifact_build = True
                except:
                    print("try_task_config.json errors")
                    return True
        else:
            print("Pushing try_task_config.json to a non-Try repo")
            return True
    elif pushing_to_try:
        print("Not pushing try_task_config.json to a Try repo")
        return True

    revision = repo.revs(rev[0]).last()
    last_public = repo.revs("public()").last()
    # for a in repo.revs('%s:' % last_public):
    #     if repo[a].isancestorof(repo[revision]):
    #         print(repo[a].description())
    # return True

    compiled_files = [".cpp", ".h", ".mm", ".rs", "metrics.yaml", "components.conf", ".idl"]

    changes = repo.status(node1=last_public, node2=revision)
    for change in changes.modified:
        change = change.decode()
        print("M " + change)
        if artifact_build and [c for c in compiled_files if change.endswith(c)]:
            print("\033[91m*** artifact build but you modified a compiled file! ***\033[m")
    for change in changes.added:
        change = change.decode()
        print("A " + change)
        if artifact_build and [c for c in compiled_files if change.endswith(c)]:
            print("\033[91m*** artifact build but you added a compiled file! ***\033[m")

    if len(changes.modified) + len(changes.added) > 0:
        mach_dir = os.path.dirname(root) if root.endswith("comm") else root
        arguments = (
            [os.path.join(mach_dir, "mach"), "commlint"]
            + ["comm/" + c.decode() for c in changes.modified if not c.decode().startswith("third_party/rust")]
            + ["comm/" + c.decode() for c in changes.added if not c.decode().startswith("third_party/rust")]
        )
        subprocess.call(arguments, cwd=mach_dir)

        okay = input("Okay? ")
        if okay.lower() in ["f", "fix"]:
            arguments = arguments[0:2] + ["--fix"] + arguments[2:]
            subprocess.call(arguments, cwd=mach_dir)
            return True

        if okay.lower() not in ["y", "yes"]:
            print("That's not okay!")
            return True

    # print(ui, repo, kwargs)
    # return True

    # TODO: finish this hook
    return False

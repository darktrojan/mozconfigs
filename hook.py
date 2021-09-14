#!/usr/bin/python3
# actually 2.7
import json
import os
import subprocess


def a_hook(ui, repo, **kwargs):
    if kwargs['opts']['rev'] == []:
        print('No revision specified')
        return True

    pushing_to_try = 'try' in kwargs['pats']

    status = repo.status(unknown=True)
    if len(status.added) or len(status.modified) or len(status.removed):
        print('Uncommitted changes:')
        print('\n'.join(status.added + status.modified + status.removed))
        return True

    if pushing_to_try and 'try_task_config.json' in status.unknown:
        print('try_task_config.json not added to revision')
        return True

    task_config_path = os.path.join(repo.root, 'try_task_config.json')
    if os.path.isfile(task_config_path):
        if pushing_to_try:
            with open(task_config_path) as fp:
                try:
                    json.load(fp)
                except:
                    print('try_task_config.json errors')
                    return True
        else:
            print('Pushing try_task_config.json to a non-Try repo')
            return True
    elif pushing_to_try:
        print('Not pushing try_task_config.json to a Try repo')
        return True

    revision = repo.revs(kwargs['opts']['rev'][0]).last()
    last_public = repo.revs('public()').last()
    # for a in repo.revs('%s:' % last_public):
    #     if repo[a].isancestorof(repo[revision]):
    #         print(repo[a].description())
    # return True
    changes = repo.status(node1=last_public, node2=revision)
    for change in changes.modified:
        print('M ' + change)
    for change in changes.added:
        print('A ' + change)
    mach_dir = os.path.dirname(repo.root) if repo.root.endswith('comm') else repo.root
    arguments = [os.path.join(mach_dir, 'mach'), 'lint', '-l', 'eslint', '-l', 'black'] + changes.modified + changes.added
    subprocess.call(arguments)

    okay = raw_input('Okay? ')
    if okay.lower() in ['f', 'fix']:
        arguments = arguments[0:6] + ['--fix'] + arguments[6:]
        subprocess.call(arguments)
        return True

    if okay.lower() not in ['y', 'yes']:
        print 'That\'s not okay!'
        return True

    # print(ui, repo, kwargs)
    # return True

    # TODO: finish this hook
    return False

import argparse
import subprocess
import sys
import urllib.request
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--update', action='store_true')
parser.add_argument('rev', nargs='?')
args = parser.parse_args()

if args.rev is not None:
  hg_data = subprocess.run(['hg', 'log', '--rev', args.rev, '--template', '{node}'], capture_output=True)
else:
  hg_data = subprocess.run(['hg', 'log', '--rev', 'last(public() and ancestors(.))', '--template', '{node}'], capture_output=True)

hg_data.check_returncode()
rev = hg_data.stdout.decode()
print('c-c revision is', rev)

url = 'https://firefox-ci-tc.services.mozilla.com/api/index/v1/task/comm.v2.comm-central.revision.{rev}.taskgraph.decision/artifacts/public/parameters.yml'

res = urllib.request.urlopen(url.format(rev=rev))
yaml_data = res.read()
data = yaml.load(yaml_data, Loader=yaml.CLoader)
print('m-c revision is', data.get('head_rev'))

if args.update:
  subprocess.run(['hg', '-R', '..', 'pull', '-u', '-r', data.get('head_rev')])

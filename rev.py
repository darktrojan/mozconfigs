import subprocess
import urllib.request
import yaml

hg_data = subprocess.run(['hg', 'log', '--rev', 'last(public())', '--template', '{node}'], capture_output=True)
rev = hg_data.stdout.decode()
print('c-c revision is', rev)

url = 'https://firefox-ci-tc.services.mozilla.com/api/index/v1/task/comm.v2.comm-central.revision.{rev}.taskgraph.decision/artifacts/public/parameters.yml'
# print('url is', url.format(rev=rev))

res = urllib.request.urlopen(url.format(rev=rev))
yaml_data = res.read()
data = yaml.load(yaml_data, Loader=yaml.CLoader)
print('m-c revision is', data.get('head_rev'))

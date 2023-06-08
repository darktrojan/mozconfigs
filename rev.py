import argparse
import subprocess
import urllib3
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--update", action="store_true")
parser.add_argument("rev", nargs="?")
args = parser.parse_args()

if args.rev is not None:
    hg_data = subprocess.run(
        ["hg", "log", "--rev", args.rev, "--template", "{node} {fxheads}"], capture_output=True
    )
else:
    hg_data = subprocess.run(
        [
            "hg",
            "log",
            "--rev",
            "last(public() and ancestors(.))",
            "--template",
            "{node} {fxheads}",
        ],
        capture_output=True,
    )

hg_data.check_returncode()
hg_output = hg_data.stdout.decode().split()
rev = None
head = None
if len(hg_output) == 2:
    [rev, head] = hg_output
else:
    [rev] = hg_output
tree = head if head in ["ash", "comm-beta", "comm-esr102"] else "comm-central"
print(tree, "revision is", rev)

url = "https://firefox-ci-tc.services.mozilla.com/api/index/v1/task/comm.v2.{tree}.revision.{rev}.taskgraph.decision/artifacts/public/parameters.yml"

res = urllib3.PoolManager().request("GET", url.format(tree=tree, rev=rev))
yaml_data = res.data
data = yaml.load(yaml_data, Loader=yaml.CLoader)
print("mozilla-central revision is", data.get("head_rev"))

if args.update:
    hg_data = subprocess.run(["hg", "-R", "..", "pull", "-r", data.get("head_rev")])
    hg_data.check_returncode()
    hg_data = subprocess.run(["hg", "-R", "..", "update", data.get("head_rev")])
    hg_data.check_returncode()

import argparse
import os.path
import subprocess
import sys
import urllib3
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--update", action="store_true")
parser.add_argument("rev", nargs="?")
args = parser.parse_args()

if args.rev is not None:
    hg_data = subprocess.run(
        ["hg", "log", "--rev", args.rev, "--template", "{node} {fxheads}"],
        capture_output=True,
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
tree = (
    head
    if head in ["ash", "comm-beta", "comm-esr102", "comm-esr115", "comm-esr128", "comm-esr140", "comm-release"]
    else "comm-central"
)
print("{tree} revision is {rev}".format(tree=tree, rev=rev))

url = "https://firefox-ci-tc.services.mozilla.com/api/index/v1/task/comm.v2.{tree}.revision.{rev}.taskgraph.decision/artifacts/public/parameters.yml"

res = urllib3.PoolManager().request("GET", url.format(tree=tree, rev=rev))
if res.status == 404:
    print(res.geturl(), res.status)
    sys.exit(-1)
yaml_data = res.data
data = yaml.load(yaml_data, Loader=yaml.CLoader)
head_tree = os.path.basename(data.get("head_repository"))
head_rev = data.get("head_rev")
print("{tree} revision is {rev}".format(tree=head_tree, rev=head_rev))

if args.update and data.get("head_rev"):
    hg_data = subprocess.run(
        ["hg", "-R", "..", "pull"]
    )  # , "-r", data.get("head_rev")])
    hg_data.check_returncode()
    hg_data = subprocess.run(["hg", "-R", "..", "update", data.get("head_rev")])
    hg_data.check_returncode()

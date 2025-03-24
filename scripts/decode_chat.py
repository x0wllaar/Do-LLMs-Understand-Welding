import json
import sys

from util import base85json2obj

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

all_data = str(sys.stdin.read())
all_data = all_data.strip()

obj = base85json2obj(all_data)

json.dump(obj, sys.stdout, indent=4)

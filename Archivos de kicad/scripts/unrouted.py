import sys, re, collections
t = open(sys.argv[1], encoding="utf-8").read(); c = collections.Counter()
for blk in t.split("\n["):
    if blk.startswith("unconnected_items") or blk.startswith("[unconnected_items"):
        for m in re.finditer(r"\[(/[^\]]+|GND|unconnected[^\]]*)\]", blk): c[m.group(1)] += 1
print("conexiones sin rutear por red:", dict(c.most_common()))

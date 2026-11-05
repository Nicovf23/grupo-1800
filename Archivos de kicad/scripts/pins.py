import re,sys
S="C:/Program Files/KiCad/9.0/share/kicad/symbols/"
def pins(lib,name):
    t=open(S+lib+".kicad_sym",encoding="utf-8").read()
    i=t.find('(symbol "%s"'%name); 
    # end = next top-level symbol
    j=t.find('\n\t(symbol "',i+10)
    blk=t[i:j if j>0 else None]
    ext=re.search(r'\(extends "([^"]+)"',blk)
    if ext: return pins(lib,ext.group(1))
    out=[]
    for m in re.finditer(r'\(pin (\w+) \w+.*?\(name "([^"]*)".*?\(number "([^"]*)"',blk,re.S):
        out.append((m.group(3),m.group(2),m.group(1)))
    fp=re.search(r'\(property "Footprint" "([^"]*)"',blk)
    return out,(fp.group(1) if fp else "")
for spec in sys.argv[1:]:
    lib,name=spec.split(":")
    r=pins(lib,name)
    p,fp=r if isinstance(r,tuple) else (r,"")
    print("==",spec,"FP:",fp); print("  "+"; ".join("%s=%s(%s)"%x for x in p))

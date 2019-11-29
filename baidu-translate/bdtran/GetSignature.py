import re
import math
from termcolor import cprint

def rightShift(val, n):
    return ( val % 0x100000000 ) >> n

def a(r):
    pass

def n(r, o):
    for t in range (0, len(o)-2, 3):
        a = o[2+t]
        a =  ord(a[0]) - 87  if a >= 'a' else int(a)
        a = rightShift(r, a) if '+'==o[t+1] else r << a
        r = r + a & 4294967295 if '+'==o[t] else r^a

    return r

def getSign(r, gtk):

    o = re.match(r'[\uD800-\uDBFF][\uDC00-\uDFFF]', r)
    if o is None:
        t = len(r)
        if t > 30:
            r = "" + r[0:10] + r[math.floor(t/2)-5 : math.floor(t/2)-5+10] + r[-10:]
    else:
        e = re.split(r'[\uD800-\uDBFF][\uDC00-\uDFFF]', r)
        C = 0; h = len(e); f = [];
        while h > C:
            if e[C] != "":
                f = list(e[C])
                if C != h - 1: f.append(o[C]);
            C += 1

        g = len(f)
        if g > 30:
            "".join(f[0:10])+"".join(f[math.floor(g/2)-5, math.floor(g/2)+5])+"".join(f[-10:])

    d = str.split(gtk, '.')
    S = []; c = 0; v = 0;
    while v < len(r):
        A = ord(r[v]);
        if  128 > A:
            S.append(A); c += 1;
        else:
            if 2048 > A:
                S.append(A >> 6 | 192); c += 1;
            else:
                if 55296 == 64512 & A and v + 1 < len(r) and\
                        56320 == (64512 & r[v+1]):
                            A = 65536 + ((1023 & A) << 10) + (1023 & r[v+1]); v+=1;
                            S.append(A >> 18 | 240); c+=1;
                            S.append( A >> 12 & 63 | 128); c+=1;
                else:
                    S.append(A >> 12 | 224); c+=1;
                    S.append(A >> 6 & 63 | 128);

            S.append(63 & A | 128); c+=1;

        v += 1

    m = p = int(d[0]);
    s = int(d[1]); 
    F ="+-a^+6"; 
    D = "+-3^+b+-f";  
    b = 0; 
    while b < len(S):
        p += S[b];
        p=n(p, F);
        b+=1

    p = n(p, D); p ^= s; 
    if 0 > p: p = (2147483647 & p) + 2147483648
    p %= 1e6;

    signature = str(int(p))+'.'+str(int(p)^m)

    return signature

#!/usr/bin/python3

def subsetsum(data, wanted, sort=True, approximate=False):
    sums = []
    for item in sorted(data) if sort else data:
        if item > wanted:
            continue
        for xdata, xsum in sums[:len(sums)]:
            if xsum + item > wanted:
                continue
            if xsum + item == wanted:
                return xdata + [item]
            sums.append((xdata + [item], xsum + item))
        sums.append(([item], item))
    if not approximate:
        raise ValueError("No matching subset found")
    cdata, csum = sums[0]
    for xdata, xsum in sums[1:]:
        if abs(wanted - xsum) < abs(wanted - csum):
            cdata, csum = xdata, xsum
    return cdata

if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input', metavar='FILE', type=open)
    p.add_argument('sum', type=int)
    p.add_argument('--sort', action='store_true')
    p.add_argument('--approximate', action='store_true')
    args = p.parse_args()
    data = [int(val) for val in args.input.read().split() if val.strip()]
    data = subsetsum(data, args.sum, sort=args.sort, approximate=args.approximate)
    if sum(data) != args.sum:
        print("No exact match found, closest match: %d" % sum(data))
    print("\n".join([str(x) for x in data]))


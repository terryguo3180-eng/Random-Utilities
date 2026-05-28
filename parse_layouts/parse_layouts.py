import argparse
import json
import sys


def parse_layouts(layouts: str):
    block = ''
    parsed = {}

    for line in layouts.split('\n'):
        if (
            line.startswith('[')
            and line.endswith(']')
            and set(line[1:-1]) == {'-'}
        ):
            # New block
            parsed.update(parse_block(block))
            block = ''
        else:
            block += line + '\n'

    parsed.update(parse_block(block))

    return parsed


def parse_block(block: str):
    block = block.strip()
    lines = [line.rstrip() for line in block.split('\n')]

    char = lines.pop(0)
    pixels = []
    origin = None

    y = len(lines)
    for line in lines:
        y -= 1

        units = [line[j:j+2] for j in range(0, len(line), 2)]
        for x, u in enumerate(units):
            if u == '  ':
                continue
            if u == '##':
                pixels.append((x, y))
                continue
            if u == '->':
                if origin is not None:
                    raise SyntaxError(f'{char!r}: Multiple origin points')
                origin = (x, y)
                continue

            raise SyntaxError(f'{char!r}: Invalid unit {u!r}')
    
    if origin is None:
        raise SyntaxError(f'{char!r}: No origin points')

    x0, y0 = origin
    for i, (x, y) in enumerate(pixels):
        pixels[i] = (x-x0, y-y0)

    return {char: sorted(pixels)}


def main():
    parser = argparse.ArgumentParser(
        description='Parse layout files'
    )
    parser.add_argument(
        '-i', '--input',
        type=str,
        default='layouts',
        help='Input file path (default layouts)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default stdout)'
    )
    
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        layouts_content = f.read()
    
    try:
        result = parse_layouts(layouts_content)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        exit(1)
    
    output = json.dumps(result)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)

if __name__ == '__main__':
    main()

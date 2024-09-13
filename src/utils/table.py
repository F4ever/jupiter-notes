def format_abi(args: list, typ: str):
    return format_table(
        ['name', 'type'],
        args,
        typ,
    )


def format_table(headers: list[str], rows: list[list[str]], typ: str):
    table = f'| {typ} | ' + ' | '.join(headers) + ' |\n'
    table += f'| :- ' * len(headers) + '| :- |\n'

    if not rows:
        table += '| - ' * len(headers) + '| - |\n'

    for index, args in enumerate(rows):
        table += f'| {index + 1} | ' + ' | '.join((str(args[head]) for head in headers)) + ' |\n'
    return table

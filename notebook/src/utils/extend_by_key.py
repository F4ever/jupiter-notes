def extend(list1: list, list2: list, key: str | None) -> list:
    """
    Merge two lists into one. Ignore items from list1 if that key exists in list2.
    """
    r = list()

    for i1 in list1:
        found = False

        if key not in i1:
            continue

        for i2 in list2:
            if key not in i2:
                continue

            if i1[key] == i2[key]:
                found = True
                break

        if not found:
            r.append(i1)

    r.extend(list2)

    return r

def format_number(number: str):
    lst = number.split(',')
    if lst[0] == '':
        raise ValueError("Invalid number")
    res = lst[0]
    for i in range(1, len(lst)):
        if len(lst[i]) == 3:
            res += lst[i]
        else:
            res += "." + lst[i]
    return round(float(res), 4)
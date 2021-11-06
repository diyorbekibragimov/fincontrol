class Separator():
    def format_number(self, number: str):
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

    def format_repr(self, number: str):
        extra = ""
        res = ""
        left = ""
        if number.count("-") > 0:
            res = number.split("-")[1]
            extra += "-"
        if number.count(".") > 0:
            lst = number.split('.')
            number = lst[0]
            left += '.' + lst[1]
        number = number[::-1]
        step = 3
        line = [number[i:i+step] for i in range(0, len(number), step)]
        for i in line:
            if len(i) == 3 and i != line[-1]:
                res += i + ','
            else:
                res += i
        res = res[::-1]
        res += left
        res = extra + res
        return res
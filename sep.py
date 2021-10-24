def format(number):
    string = str(number)
    n = 3
    formatted_list = [string[i:i+n] for i in range(0, len(string), n)]
    return formatted_list
    # result = ""
    # for x in formatted_list:
    #     result += x + ","
    # return result[0:len(result) - 1]
    
if __name__ == '__main__':
    number = int(input("Number: "))
    print(format(number))
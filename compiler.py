def tokenize(code):
    start = -1
    cLen = len(code)
    tokens = []
    while True:
        start += 1
        if start > cLen:
            break
        else:
            if code[start].lower() in "abcdefghijklmnopqrstuvwxyz_":
                #namespaces and stuff etc
                pass
            elif code[start] == ".":
                if start + 1 > cLen:
                    print("ERROR: NO POINTER VALUE SPECIFIED")
                    return
                elif code[start + 1] == ".":
                    tokens.append(["abspointer"])
                    start += 1
                else:
                    tokens.append(["relpointer"])
            elif code[start] in "1234567890":
                num = code[start]
                decimal = False
                while True:
                    start += 1
                    if start > cLen:
                        break
                    if code[start] in "1234567890": #regular digits
                        num += code[start]
                    elif code[start] == ".": #handling decimals
                        if decimal: #numbers can't have two decimal points in them
                            print("ERROR: MALFORMED NUMBER")
                            return
                        else: #specify that this is indeed a decimal number
                            num += code[start]
                            decimal = True
                    elif code[start].lower() in "qwertyuiopasdfghjklzxcvbnm_": #numbers aren't alphabetical
                        print("ERROR: MALFORMED NUMBER")
                        return
                    else:
                        break
                    
                        
            elif code[start] in "()[]{}+-/*":
                tokens.append(["symbol", code[start]])
                

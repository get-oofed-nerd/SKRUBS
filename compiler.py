def tokenize(code):
    start = -1
    cLen = len(code)
    tokens = []
    while True:
        start += 1
        if start + 1> cLen:
            break
        else:
            if code[start].lower() in "abcdefghijklmnopqrstuvwxyz_":
                cache = code[start]
                while True:
                    start += 1
                    if start + 1 > cLen:
                        break
                    elif code[start].lower() in "qwertyuiopasdfghjklzxcvbnm1234567890_":
                        cache += code[start]
                    else:
                        start -= 1
                        break

                if cache in ["true" , "false"]:
                    tokens.append(["boolean", cache])
                elif cache == "inline":
                    tokens.append(["inline"])
                elif cache in ["if", "elseif", "else", "while", "end"]:
                    tokens.append(["cflow", cache])
                elif cache in ["and", "or", "not"]:
                    tokens.append(["binop", cache])
                else:
                    tokens.append(["namespace", cache])
            elif code[start] in "1234567890.":
                num = code[start]
                decimal = code[start] == "."
                while True:
                    start += 1
                    if start + 1 > cLen:
                        break
                    elif code[start] in "1234567890": #regular digits
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
                        start -= 1
                        break

                tokens.append(["number", num])
                    
                        
            elif code[start] in "()[]{},":
                tokens.append(["symbol", code[start]])

            elif code[start] in "+-*/<>":
                tokens.append(["binop", code[start]])

            elif code[start] in "=":
                if start + 2 > cLen:
                    print("ERROR: NO VALUE ASSIGNED")
                    return
                elif code[start + 1] == "=":
                    tokens.append(["binop", "=="])
                    start += 1
                else:
                    tokens.append(["assign"])

    return tokens

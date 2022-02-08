OOO = {"and": 1, "or": 2, "==": 3, "<": 4, ">": 5, "+": 6, "-": 7, "*": 8, "/": 9}
UrnOps = {"not", "-"}

class compiler:
    tc = -1
    parenDepth = 0
    idxDepth = 0
    tbDepth = 0
    
    def tokenize(self, code):
        start = -1
        cLen = len(code)
        tokens = []
        while True:
            start += 1
            if start + 1 > cLen:
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
                    elif cache == "inline": #inlining will come in handy when making functions for customizability
                        tokens.append(["inline"])
                    elif cache in ["if", "elseif", "else", "while", "end", "return"]:
                        tokens.append(["cflow", cache])
                    elif cache in ["and", "or", "not"]:
                        tokens.append(["operation", cache]) #compiler flags to tell where to get variables
                    elif cache in ["mousex", "mousey", "moused"]:
                        tokens.append(["flag", cache])
                    else:
                        tokens.append(["variable", cache])
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
                    tokens.append(["operation", code[start]])

                elif code[start] in "=":
                    if start + 2 > cLen:
                        print("ERROR: NO VALUE ASSIGNED")
                        return
                    elif code[start + 1] == "=":
                        tokens.append(["operation", "=="])
                        start += 1
                    else:
                        tokens.append(["assign"])

        return tokens

    def parseVal(self, tokens):
        leftOp = None
        while True:
            self.tc += 1
            if self.tc > len(tokens) - 1:
                break
            tk = tokens[self.tc]
            
            if tk[0] == "operation" and tk[1] in UrnOps: #urnary operations
                return [tk[1], self.parseVal(tokens)]
            elif tk[0] in ["number", "string", "variable", "boolean"] and leftOp == None:
                leftOp = tk
            elif tk[0] == "symbol":
                #yanderedev tier code
                #deals with parenthesis stuff
                if tk[1] == "(":
                    self.parenDepth += 1
                    return self.expressionEval(tokens)
                elif tk[1] == "[":
                    #getting an index
                    if leftOp != None:
                        self.idxDepth += 1
                        leftOp = ["idx", leftOp, self.expressionEval(tokens)]
                    else:
                        print("ERROR: where is ur table lmao")
                        return
                    
                elif tk[1] == "{":
                    self.tbDepth += 1
                    #coming soon
            else:
                self.tc -= 1
                break

        return leftOp
                
                

    def expressionEval(self, tokens):
        print(self.parseVal(tokens))
        

    def compile(self, code):
        tokens = self.tokenize(code)
        if tokens == None:
            return
        else:
            self.tc = -1
            self.parenDepth = 0
            self.idxDepth = 0
            self.tbDepth = 0
            self.expressionEval(tokens)

skrubs = compiler()
skrubs.compile("sex[1]")

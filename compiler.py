OOO = {"and": 1, "or": 2, "==": 3, "<": 4, ">": 5, "+": 6, "-": 7, "*": 8, "/": 9}
UrnOps = {"not", "-"}

class compiler:
    tc = -1
    parenDepth = 0
    idxDepth = 0
    tbDepth = 0
    commaDepth = 0
    
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
                    elif cache in ["mousex", "mousey", "moused", "clock"]:
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
                                raise Exception("ERROR: MALFORMED NUMBER")
                            else: #specify that this is indeed a decimal number
                                num += code[start]
                                decimal = True
                        elif code[start].lower() in "qwertyuiopasdfghjklzxcvbnm_": #numbers aren't alphabetical
                            raise Exception("ERROR: MALFORMED NUMBER")
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
                        raise Exception("ERROR: NO VALUE ASSIGNED")
                    elif code[start + 1] == "=":
                        tokens.append(["operation", "=="])
                        start += 1
                    else:
                        tokens.append(["assign"])

        return tokens


    def parseVal(self, tokens): #gets a standalone value within skrubs
        leftOp = None
        while True:
            self.tc += 1
            if self.tc > len(tokens) - 1:
                break
            tk = tokens[self.tc]
            
            if tk[0] == "operation" and tk[1] in UrnOps: #urnary operations
                return [tk[1], self.parseVal(tokens)]
            elif tk[0] in ["number", "string", "variable", "boolean", "flag"] and leftOp == None:
                leftOp = tk
            elif tk[0] == "symbol":
                #yanderedev tier code
                #deals with parenthesis stuff
                if tk[1] == "(":
                    if leftOp == None:
                        self.parenDepth += 1
                        leftOp = self.expressionEval(tokens)
                    elif leftOp[0] == "variable": #function call
                        pdc = self.parenDepth
                        self.parenDepth += 1
                        args = []
                        while True:
                            self.commaDepth += 1
                            args.append(self.expressionEval(tokens))
                            if self.parenDepth == pdc:
                                break
                        leftOp = ["fcall", leftOp[1], args]
                    else: #omg we can multiply by sticking brackets together in math no way wowzers!
                        self.parenDepth += 1
                        leftOp = ["*", leftOp, self.expressionEval(tokens)]
                        
                elif tk[1] == "[":
                    #getting an index
                    if leftOp != None:
                        self.idxDepth += 1
                        leftOp = ["idx", leftOp, self.expressionEval(tokens)]
                    else:
                        raise Exception("ERROR: where is ur table lmao")
                    
                elif tk[1] == "{":
                    pdc = self.tbDepth
                    self.tbDepth += 1
                    args = []
                    while True:
                        self.commaDepth += 1
                        args.append(self.expressionEval(tokens))
                        if self.tbDepth == pdc:
                            break

                    leftOp = ["table", args]

                elif tk[1] in ")]},":
                    if leftOp == None:
                        raise Exception("ERROR: Please stop trying to force null lmao")
                    else:
                        self.tc -= 1
                        return leftOp

                        
            else:
                self.tc -= 1
                break

        return leftOp
                
                

    def expressionEval(self, tokens): #equations and stuff ig
        tree = self.parseVal(tokens)
        didOperation = False
        while True:
            self.tc += 1
            if self.tc > len(tokens) - 1:
                break
            operation = tokens[self.tc]
            if operation[0] == "operation":
                if self.tc > len(tokens) - 1:
                    raise Exception("ERROR: Field two incomplete for operation")
                else:
                    t2 = self.parseVal(tokens)
                    if didOperation: #order of operations enforcement
                        if OOO[operation[1]] > OOO[tree[0]]: #the current operation comes first
                            tree = [tree[0], tree[1], [operation[1], tree[2], t2]]
                        else: #tre operation comes first
                            tree = [operation[1], tree, t2]
                    else:
                        tree = [operation[1], tree, t2]
                        didOperation = True

            elif operation[0] == "symbol": #parenthesis handler
                if operation[1] == ")":
                    if self.parenDepth >= 0:
                        self.parenDepth -= 1
                        return tree
                    else:
                        raise Exception("ERROR: malformed bracket")

                elif operation[1] == "]":
                    if self.idxDepth >= 0:
                        self.idxDepth -= 1
                        return tree
                    else:
                        raise Exception("ERROR: malformed idxBracket")
                elif operation[1] == "}":
                    if self.tbDepth >= 0:
                        self.tbDepth -= 1
                        return tree
                    else:
                        raise Exception("ERROR: malformed tableBracket")
                    
                elif operation[1] == ",":
                    if tree == None or self.commaDepth < 0:
                        raise Exception("Malformed comma")
                    else:
                        self.commaDepth -= 1
                        return tree

        return tree


        

    def compile(self, code):
        tokens = self.tokenize(code)
        if tokens == None:
            return
        else:
            self.tc = -1
            self.parenDepth = 0
            self.idxDepth = 0
            self.tbDepth = 0
            print(self.expressionEval(tokens))

skrubs = compiler()
skrubs.compile("{1, {2, 3}}")

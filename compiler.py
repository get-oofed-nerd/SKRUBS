OOO = {"and": 1, "or": 2, "==": 3, "<": 4, ">": 5, "+": 6, "-": 7, "*": 8, "/": 9, "%": 10}
OPERATIONMAP = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD", "and": "AND", "or": "OR", "<": "LT", "==": "EQ"}
FLAGS = {"mousex": "MX", "mousey": "MY", "moused": "MDWN", "clock": "CLOCK"}
UrnOps = {"not", "-"}

class compiler:
    tc = -1
    parenDepth = 0
    idxDepth = 0
    tbDepth = 0
    commaDepth = 0
    ifDepth = 0
    scopeDepth = 0
    inFunction = False
    residentFunctions = {}
    
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
                    elif cache in ["if", "elseif", "else", "while", "end", "return", "function"]:
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

                elif code[start] in "+-*/<>%":
                    tokens.append(["operation", code[start]])

                elif code[start] in "=":
                    if start + 2 > cLen:
                        raise Exception("ERROR: NO VALUE ASSIGNED")
                    elif code[start + 1] == "=":
                        tokens.append(["operation", "=="])
                        start += 1
                    else:
                        tokens.append(["assign"])

                elif code[start] in '\'"': #string parse
                    lookFor = code[start]
                    isEscape = False
                    start += 1
                    string = ""
                    while True:
                        if start + 1 > cLen:
                            raise Exception("ERROR: Malformed String")
                        else:
                            char = code[start]
                            if isEscape:
                                string += eval('"\\' + char + '"')
                                isEscape = False
                            else:
                                if char == "\\":
                                    isEscape = True
                                elif char == lookFor:
                                    break
                                else:
                                    string += char

                        start += 1

                    tokens.append(["string", string])

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
            else:
                break

        return tree

    def makeCB(self, tokens): #makes the blocks of code
        tree = []
        while True:
            self.tc += 1
            if self.tc > len(tokens) - 1:
                break
            else:
                tk = tokens[self.tc]
                if tk[0] == "variable": #variable assigning and function calls
                    self.tc += 1
                    if self.tc > len(tokens) - 1:
                        raise Exception("ERROR: Invalid code block")
                    else:
                        nThing = tokens[self.tc]
                        self.tc -= 2 #conpensating for funny architecture with expressionEval and parseVal
                        if nThing[0] == "symbol" and nThing[1] == "(": #function calls
                            tree.append(self.parseVal(tokens))
                        else: #assigning things
                            assign = []
                            
                            while True: #getting every field we want to assign
                                item = self.parseVal(tokens)
                                if item[0] in ["idx", "variable"]:
                                    assign.append(item)
                                else:
                                    raise Exception("ERROR: Can only assign values to table indexes or variables")

                                self.tc += 1
                                tk = tokens[self.tc]
                                if tk[0] == "assign":
                                    break
                                elif tk[0] == "symbol" and tk[1] == ",":
                                    pass
                                else:
                                    raise Exception("ERROR: Expected comma after field to assign")


                            vTable = []
                            for i in range(len(assign)): #get corresponding values and add it to the value table
                                if i > 0 and not tokens[self.tc][1] == ",":
                                    raise Exception("ERROR: Expected comma to separate each value")
                                
                                self.commaDepth += 1
                                vTable.append(self.expressionEval(tokens))
                                
                            self.commaDepth -= 1 #commas = #values - 1

                            tree.append(["assign", assign, vTable])
                            self.tc -= 1

                elif tk[0] == "inline": #inlining code i love assembly and C makeout (real)
                    #hmmm i wonder how many args this inline will take up
                    self.tc += 1
                    if self.tc > len(tokens) - 1:
                        raise Exception("ERROR: Unspecified inline code")
                    else:
                        inline = tokens[self.tc]
                        if inline[0] == "variable":
                            args = 0 #argument counter
                            if inline[1] in ["PUP", "PDOWN", "PCLR", "RCLOCK"]: #takes no arguments
                                pass
                            elif inline[1] in ["JUMP", "TEST", "PWIDTH", "PRINT", "MX", "MY", "MDWN", "RETURN", "RELTOGGLE", "CLOCK"]:
                                args = 1 #takes one argument
                            elif inline[1] in ["URN", "NOT", "LOADTABLE", "MOVE", "PMOVE", "IUP", "FREF"]:
                                args = 2 #takes two arguments
                            elif inline[1] in ["ADD", "SUB", "MUL", "DIV", "MOD", "RND", "CMATH", "JOIN", "CHRAT", "STRIN", "AND", "OR", "LT", "EQ", "LOADV", "PHSV",
                                               "FCALL", "RAN"]:
                                args = 3 #takes three arguments
                            else:
                                raise Exception("ERROR: Invalid inline code specified")

                            aTable = []
                            for i in range(args):
                                self.tc += 1
                                if self.tc > len(tokens) - 1:
                                    raise Exception("ERROR: Not enough values specified for inline code")
                                aTable.append(tokens[self.tc])

                            tree.append(["inline", inline, aTable])

                        else: #do NOT use numbers as inline codes (1984)
                            raise Exception("ERROR: Malformed inline code")
                elif tk[0] == "cflow":
                    if tk[1] == "return": #returning a specified value
                        tree.append(["return", self.expressionEval(tokens)])
                        self.tc -= 1
                    elif tk[1] == "if": #if statements
                        self.tc += 1
                        if self.tc > len(tokens) - 1:
                            raise Exception("ERROR: No condition specified")
                        else:
                            self.tc -= 1
                            condition = self.expressionEval(tokens)
                            self.tc -= 1
                            self.scopeDepth += 1
                            self.ifDepth += 1
                            cflow = []
                            cflow.append([condition, self.makeCB(tokens)])
                            self.ifDepth -= 1
                            while True:
                                tk = tokens[self.tc]
                                self.scopeDepth += 1
                                if tk[1] == "end": #ends also are final
                                    self.scopeDepth -= 1
                                    break
                                elif tk[1] == "elseif": #elseifs can be chained
                                    self.ifDepth += 1
                                    condition = self.expressionEval(tokens)
                                    self.tc -= 1
                                    cflow.append([condition, self.makeCB(tokens)])
                                    self.ifDepth -= 1
                                elif tk[1] == "else": #elses are the final
                                    cflow.append(["else", self.makeCB(tokens)])

                            tree.append(["conditional", cflow])
                                
                    elif tk[1] == "function":
                        if self.inFunction:
                            raise Exception("ERROR: Cannot nest a function within a function")
                        else:
                            func = self.parseVal(tokens)
                            self.tc -= 1
                            self.scopeDepth += 1
                            body = self.makeCB(tokens)
                            self.inFunction = True
                            tree.append(["function", func, body])
                            self.inFunction = False
                    elif tk[1] == "elseif" or tk[1] == "else":
                        if self.ifDepth < 0:
                            raise Exception("ERROR: cflow not found")
                        else:
                            self.scopeDepth -= 1
                            return tree
                        
                    elif tk[1] == "while": #i love substructures taking care of all the work for me lol
                        self.scopeDepth += 1
                        condition = self.expressionEval(tokens)
                        self.tc -= 1
                        tree.append(["loop", condition, self.makeCB(tokens)])
                    elif tk[1] == "end":
                        self.scopeDepth -= 1
                        if self.scopeDepth < 0:
                            raise Exception("ERROR: Malformed end")
                        else:
                            return tree

        if self.scopeDepth > 0:
            raise Exception("ERROR: Unclosed cflow")
        
        return tree

    def opcodes(self, tree, inFunction, pstart, memory, _return=False): #turns an abstract syntax tree into portable bytecode
        stkReserve = pstart #keeping tabs on how much of the stack is reserved
        opcodes = []
        
        for term in tree:
            if term[0] == "assign":
                for i in range(len(term[1])): #create a new variable
                    if not term[1][i][1] in memory:
                        pstart += 1
                        memory[term[1][i][1]] = pstart #assigning the variable a memory address
                        
                    valTo = self.opcodes(term[2], inFunction, pstart, memory) #assign variable certain value
                    for op in valTo:
                        opcodes.append(op)

            elif term[0] in UrnOps: #i love urnary operations!
                ez = ""
                addr = pstart + 1
                if term[0] == "-":
                    ez = "URN"
                else:
                    ez = "NOT"

                t1 = self.opcodes([term[1]], inFunction, pstart + 1, memory)
                if t1[0][0] == "variable":
                    if t1[0][1] in memory:
                        addr = memory[t1[0][1]]
                    else:
                        raise Exception("ERROR: Undeclared variable")

                else:
                    for op in t1:
                        opcodes.append(op)

                opcodes.append([ez, addr, pstart])

            elif term[0] in OOO: #compiles a datatype operational statement
                a1 = pstart + 1
                a2 = pstart + 2
                
                t1 = self.opcodes([term[1]], inFunction, pstart + 1, memory)
                if t1[0][0] == "variable":
                    if t1[0][1] in memory:
                        a1 = memory[t1[0][1]]
                    else:
                        raise Exception("ERROR: Undeclared variable")
                else:
                    for op in t1:
                        opcodes.append(op)

                t2 = self.opcodes([term[2]], inFunction, pstart + 2, memory)
                if t2[0][0] == "variable":
                    if t2[0][1] in memory:
                        a2 = memory[t2[0][1]]
                    else:
                        raise Exception("ERROR: Undeclared variable")
                else:
                    for op in t2:
                        opcodes.append(op)


                if term[0] == ">":
                    opcodes.append(["LT", a2, a1, pstart])
                else:
                    opcodes.append([OPERATIONMAP[term[0]], a1, a2, pstart])

            elif term[0] == "number": #loading constant :troll:
                opcodes.append(["LOADV", "number", term[1], pstart])

            elif term[0] == "variable": #temporary container so we can point to the according address of the variable
                opcodes.append(term)

            elif term[0] == "string":
                FRMT = ""
                for char in term[1]:
                    asc = hex(ord(char))
                    FRMT += asc[2:len(asc)]

                opcodes.append(["LOADV", "string", FRMT, pstart])

            elif term[0] == "boolean":
                opcodes.append(["LOADV", "boolean", term[1], pstart])

            elif term[0] == "flag":
                opcodes.append([FLAGS[term[1]], pstart])

            elif term[0] == "conditional": #i love conditionals!
                BROJUMPPLEASE = [] #we need to find every exit conditional in order or the cflow to compile properly lol
                pstart += 1
                for flow in term[1]:
                    if flow[0] == "else":
                        for c in self.opcodes(flow[1], inFunction, pstart, memory):
                            opcodes.append(c)

                    else:
                        
                        #add a test opcode to see if the condition is true or not
                        for i in self.opcodes([flow[0]], inFunction, pstart, memory):
                            opcodes.append(i)

                        opcodes.append(["TEST", pstart])
                        body = self.opcodes(flow[1], inFunction, pstart, memory)
                        opcodes.append(["JUMP", len(body) + 1])
                        for c in body:
                            opcodes.append(c)

                        opcodes.append(["JUMP", 42069]) #we will come back to this opcode later
                        BROJUMPPLEASE.append(len(opcodes) - 1)

                pstart -= 1

                    

                for idx in BROJUMPPLEASE: #making the exits for each conditional functional
                    opcodes[idx][1] = len(opcodes) - idx - 1

            elif term[0] == "inline":
                code = [term[1][1]]
                for i in term[2]:
                    code.append(i[1])

                opcodes.append(code)

            elif term[0] == "loop":
                loc = len(opcodes)
                cond = self.opcodes([term[1]], inFunction, pstart + 1, memory)
                for code in cond:
                    opcodes.append(code)

                opcodes.append(["TEST", pstart + 1])
                body = self.opcodes(term[2], inFunction, pstart + 1, memory)
                opcodes.append(["JUMP", len(body) + 1])

                for code in body:
                    opcodes.append(code)

                opcodes.append(["JUMP", loc - len(opcodes) - len(cond) - 1])

            elif term[0] == "function":
                self.residentFunctions[term[1][1]] = [len(term[1][2]), len(opcodes) + 1] #put the amount of parameters and the area where the function will
                #be resident
                ez = self.opcodes(term[2], True, 0, {}, True)
                opcodes.append(["JUMP", len(ez)]) #do NOT run functions unless otherwise specified (1984)
                for i in ez:
                    opcodes.append(i)

            elif term[0] == "fcall":
                if term[1] in self.residentFunctions:
                    noZeroAddr = False #NO assigning values to the memory address 0 (1984)
                    if pstart == 0:
                        pstart = 1
                        noZeroAddr = 1
                        
                    for i in range(self.residentFunctions[term[1]][0]):
                        ez = self.opcodes([term[2][i]], inFunction, pstart + i, memory)
                        if ez[0][0] == "variable":
                            opcodes.append(["MOVE", pstart + i, memory[ez[0][1]]])
                        else:
                            for code in ez:
                                opcodes.append(code)
                        
                    opcodes.append(["FCALL", self.residentFunctions[term[1]][1], pstart, pstart])

                    if noZeroAddr: #setting it back once we are done doing the funny workaround
                        pstart = 0
                else:
                    raise Exception("ERROR: Undefined function")

            elif term[0] == "return":
                r = self.opcodes([term[1]], inFunction, pstart + 1, memory)
                if r[0][0] == "variable":
                    opcodes.append(["RETURN", memory[r[0][1]]])
                else:
                    for i in r:
                        opcodes.append(i)
                    opcodes.append(["RETURN", pstart + 1])


        if _return:
            opcodes.append(["RETURN", 0])
            
        return opcodes

    def serialize(self, opcodes): #serializes all opcodes in string format in order for skrubs to execute
        serial = ""
        for i in opcodes:
            serial += ","
            for j in range(len(i)):
                if j > 0:
                    serial += "."

                serial += str(i[j])

        return serial

    def compile(self, code):
        tokens = self.tokenize(code)
        if tokens == None:
            return
        else:
            self.tc = -1
            self.parenDepth = 0
            self.idxDepth = 0
            self.tbDepth = 0
            self.ifDepth = 0
            self.scopeDepth = 0
            self.inFunction = False
            self.residentFunctions = {}
            tree = self.makeCB(tokens)
            codes = self.opcodes(tree, False, 0, {})
            print(self.serialize(codes))

skrubs = compiler()
skrubs.compile("function print(a) inline PRINT 1 return 1 end haida = print('Hello world!') print(haida + 1)")

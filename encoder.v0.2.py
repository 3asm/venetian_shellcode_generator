#!/usr/bin/env python

import sys
import getopt
from utils import prettyText #add code coloring

debugMode = False
debugLevel = 1

def contains(small,big):
    for c in small:
        if c not in big:
            return False
    return True

def usage():

    print prettyText("%s --alphabet <alphabet_word_file> --word <word_hex> --list <function_list>" % sys.argv[0],"green")
    print prettyText("--alphabet, -a : TODO","green")
    print prettyText("--word, -w : TODO","green")
    print prettyText("--list, -l : TODO","green")
    print prettyText("--offset, -o : TODO","green")
    print prettyText("--mutation, -m : TODO","green")
    print prettyText("--help, -h : this help","green")
    print prettyText("example: %s --alphabet alphabet.txt --word 12131415 --list add,sub" % sys.argv[0],"green")


def debugListHex(pos, description, level=1):
    if debugMode and level >= debugLevel:
        print prettyText("[D] %s %s" % (description, str([hex(c) for c in pos])),"green")

def debug(description,level=1):
    if debugMode and level >= debugLevel:
        print prettyText("[D] %s" % description,"green")

def info(description):
    print prettyText("[*] %s" % description,"blue")

def error(description):
    print prettyText("[-] %s" % description,"red")

def generateRepresentation(word,base=1):
    '''
    Generate all possible representation of 'word' in the current base
   for example the representations for the the word '0x12 0x13 0x14 0x15' in base 2 are:
    [D] ** ['0x12', '0x13', '0x14', '0x15']
    [D] ** ['0x212', '0x13', '0x14', '0x15']
	[D] ** ['0x10', '0x213', '0x14', '0x15']
	[D] ** ['0x210', '0x213', '0x14', '0x15']
	[D] ** ['0x12', '0x11', '0x214', '0x15']
	[D] ** ['0x212', '0x11', '0x214', '0x15']
	[D] ** ['0x10', '0x211', '0x214', '0x15']
	[D] ** ['0x210', '0x211', '0x214', '0x15']
	[D] ** ['0x12', '0x13', '0x12', '0x215']
	[D] ** ['0x212', '0x13', '0x12', '0x215']
	[D] ** ['0x10', '0x213', '0x12', '0x215']
	[D] ** ['0x210', '0x213', '0x12', '0x215']
	[D] ** ['0x12', '0x11', '0x212', '0x215']
	[D] ** ['0x212', '0x11', '0x212', '0x215']
	[D] ** ['0x10', '0x211', '0x212', '0x215']
	[D] ** ['0x210', '0x211', '0x212', '0x215']
    '''

    chars = word

    tmp = []
    lstRep = []


    for m in range(-base,base+1):
        for l in range(2**len(chars)):
            tmp = []
            tmp.extend(chars)
            #debugListHex(tmp,"%d : " % l)
            if l % 2 == 1:
                tmp[0] = tmp[0] + 0x100 * m
                #debugListHex(tmp,"%d : %d :" % (l, l%2))


            if l % 4 in (2,3):
                tmp[0] = tmp[0] - 0x1 * m
                tmp[1] = tmp[1] + 0x100 * m

            if l % 8 in range(4,8):
                tmp[1] = tmp[1] - 0x1 * m
                tmp[2] = tmp[2] + 0x100 * m

            if l % 16 in range(8,16):
                tmp[2] = tmp[2] - 0x1 * m
                tmp[3] = tmp[3] + 0x100 * m

            lstRep.append(tmp)

        for l in lstRep:
            debugListHex(l,"**")

    return lstRep


def generateSpaceEx(func, initSpace, alphabet):
    lSpace = []
    for c in alphabet:
        for i in initSpace:
            lSpace.append([func(c,i),c,i,func])

    #debug
    for i in lSpace:
        debug("%s = %s %s. %s" % (hex(i[0]),hex(i[1]),i[3].func_name,hex(i[2])))

    return lSpace


def findCombination(word,lstFunc,alphabet,offset,reprs):

    debug("findCombination(%s,%s,%s)" % (word,lstFunc,alphabet))

    found = False
    tmpAlph = []
    mutation = 1
    his = dict()
    spaces = dict()
    spaceTree = Tree()
    spaceTree.add_features(space=offset)

    if contains(word,alphabet):
        info("Alphabet contains Word")
        info("PUSH %s" % word)
        exit()

    while not found:
        info("Mutation: %d !" % mutation)

        #debug
        #debug("> Tree:")
        #print spaceTree
        #print spaceTree.get_ascii(attributes=['space',])


        for n in spaceTree.get_leaves():

            #debug(">> Node:")
            #print spaceTree.get_ascii(attributes=['space',])

            for f in lstFunc:
                tmpAlph = n.space

                #generate space from the new alphabet
                space = generateSpaceEx(f,tmpAlph,alphabet)
                tmpSpace = list(set([c[0] for c in space]))
                debugListHex(tmpSpace,"SPACE")

                #check to see any the word representation exists in the space
                for r in reprs:
                    #debugListHex(r,"Checking Representation")
                    if contains(r,tmpSpace):
                        found = True
                        info("FOUND : %s" % r)
                        lstAncestors = [n,]
                        lstAncestors.extend(n.get_ancestors())
                        nodeF = n.add_child(name=f)
                        nodeF.add_features(space=tmpSpace,history=space)
                        lstAncestors = [nodeF,]
                        lstAncestors.extend(nodeF.get_ancestors())
                        getSolution(r,offset,lstAncestors)
                        exit()


                nodeF = n.add_child(name=f)
                nodeF.add_features(space=tmpSpace,history=space)
        mutation = mutation + 1

def getSolution(reprs,offset,his):

    debugListHex(reprs,"reprs:",2)
    debugListHex(offset,"offset:",2)
    sol = dict()
    sol2 = dict()
    for rg in range(len(reprs)):
        r = reprs[rg]
        of = offset[rg]
        #print prettyText("searching for 0x%02x <= 0x%02x" % (r,of),"red")
        tPath = Tree(name=r)
        tPath.add_features(value=r)
        for h in his[:-1]:
            #print prettyText("in H","red")
            for leaf in tPath.get_leaves():
                r = leaf.value
                #print prettyText("leaves: %s" % str(tPath.get_leaves()),"cyan")
                for line in h.history:
                    res, alph, past, method = line[0], line[1], line[2], line[3].func_name
                    #debug("0x%02x = 0x%02x %s. (0x%02x)" % (res,alph,method,past),2)
                    #print prettyText("comparing res=0x%02x ?= r=0x%02x" % (res,r),"yellow")
                    if res == r:
                        n = leaf.add_child(name=alph)
                        n.add_features(function=method,value=past)
        #print tPath.get_ascii(attributes=['name','function','value'])
        lf = tPath.get_leaves()[0]
        anc = lf.get_ancestors()[:-1]
        llf = [lf,]
        llf.extend(anc)
        vls = [c.name for c in llf]
        sol[rg] = llf

    debug("sol:" + str(sol),4)
    for i in sol:
        vls = [(c.name, c.function) for c in sol[i]]
        debug(vls,4)
        sol2["method"] = []
        for j in range(len(vls)):
            sol2["method"].append(vls[j][1])
            if sol2.has_key(j):
                sol2[j].append(vls[j][0])
            else:
                sol2[j] = []
                sol2[j].append(vls[j][0])
    print prettyText("Solution:","red")
    info("PUSH\t\t0x%02x%02x%02x%02x" % (offset[0],offset[1],offset[2],offset[3]))

    test = []
    test.append(offset[0] * 0x01000000 + offset[1] * 0x00010000 + offset[2] * 0x00000100 + offset[3] * 0x00000001)

    debug(sol2,4)

    for m in range(len(sol2["method"])):


        test.append(sol2[m][0] * 0x01000000 + sol2[m][1] * 0x00010000 + sol2[m][2] * 0x00000100 + sol2[m][3] * 0x00000001)

        info("%s\t\t\t0x%02x%02x%02x%02x" % (sol2["method"][m],sol2[m][0],sol2[m][1],sol2[m][2],sol2[m][3]))


    info("RESULT\t\t0x%08x" % (reprs[0] * 0x01000000 + reprs[1] * 0x00010000 + reprs[2] * 0x00000100 + reprs[3] * 0x00000001))
    testResult(test,(reprs[0] * 0x01000000 + reprs[1] * 0x00010000 + reprs[2] * 0x00000100 + reprs[3] * 0x00000001))

def testResult(lst,res):
    error("Testing only support ADD only solution !!!")
    f = 0x0
    for l in lst:
        f = f + l

    if f == res:
        debug("True",2)
        return True
    else:
        debug("False",2)
        return False


def ADD(a,b):
    return a+b

def SUB(a,b):
    return b-a


def AND(a,b):
    return a & b

def XOR(a,b):
    return a ^ b

def OR(a,b):
    return a | b

if __name__ == "__main__":

    try:
        from ete2 import Tree
    except:
        error("ete2 not installed")
        error("try: easy_install -U ete2 or apt-get install python-ete2 to install ete2")
        exit(1)

    debug("Parsing options ...")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:w:l:d:o:m:",["help","alphabet=","word=","list=","debug=","offset=","mutation="])
    except getopt.GetoptError, err:
        print prettyText(str(err),"red")
        sys.exit(2)


    initialAlphabet = []
    word = [] #word to search ['\x12','\x13','\x14','\x15']
    funcList = []
    offset = [0x00,0x00,0x00,0x00]
    mutationLimit = 0
    representation = [] #list of word representation to search for
    debug(opts)

    for o, a in opts:
        if o in ("-h","--help"):
            usage()
            sys.exit()
        elif o in ("-a","--alphabet"):
            initialAlphabet = [int(c.strip('\n'),16) for c in open(a,'r').readlines()]
        elif o in ("-w","--word"):
            for i in range(0,len(a),2):
                word.append(int(a[i:i+2],16))
        elif o in ("-l","--list"):
            tmpfuncList = a.split(',')
            for f in tmpfuncList:
                if f.lower() == "add":
                    funcList.append(ADD)
                elif f.lower() == "sub":
                    funcList.append(SUB)
                elif f.lower() == "and":
                    funcList.append(AND)
                elif f.lower() == "xor":
                    funcList.append(XOR)
                elif f.lower() == "or":
                    funcList.append(OR)
                else:
                    print prettyText("%s not support !" % f,"red")
                    usage()
                    sys.exit(2)
        elif o in ("-d","--debug"):
            debugMode = True
            debugLevel = int(a)
            info("Debug Level %d" % debugLevel)
        elif o in ("-o","--offset"):
            offset = []
            if a != '00000000':
                error("Result might be wrong, only offset 0x00000000 is garnteed to work !")
            for i in range(0,len(a),2):
                offset.append(int(a[i:i+2],16))
        elif o in ("-m","--mutation"):
            mutationLimit = int(a)
        else:
            usage()
            sys.exit(1)


    debugListHex(initialAlphabet,"Alphabet:")
    debugListHex(word,"Word:")
    debugListHex(offset,"Offset:")
    debug(str(funcList))
    debug("Mutation Limit: %d" % mutationLimit)

    representation.extend(generateRepresentation(word,mutationLimit))
    debug(representation,3)

    findCombination(word,funcList,initialAlphabet,offset,representation)


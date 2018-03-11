#RAINBOWS.l Interpreter by Douglas Reilly
from sys import stdin, stdout, argv
import time
data_types = {
    '$':'string',
    'h$':'hex string',
    '%f':'float',
    '%':'integer',
    '@':'variable',
    '_':'input',
    '+':'array',
}
flags = {'ifstat':0,'moveahead':1,'pointer':0,'setmode':0,'back':0,'inputmode':0}
variables = {}
arguments = []
functions = {}
labels    = {}
error = lambda line: print('"%s" Contained Error'%line)
label = lambda var: var.replace('@','')
chunks = lambda l,n: [l[i:i+n] for i in range(0, len(l), n)] if n>1 else [l[i:i+1] for i in range(0, len(l), 1)]

def rFormat(data, Type):
    global data_types
    if Type != 'array':
        for dataPrefix in data_types.keys():
            dataType = data_types[dataPrefix]
            if dataType == Type or dataPrefix == Type:
                if not '{0}'.format(data).startswith(dataPrefix):
                    return '{0}{1}'.format(dataPrefix,data)
                else:
                    return '{0}'.format(data)
    else:
        if not '{0}'.format(data).startswith('+['):
            if '{0}'.format(data).startswith('['):
                return '+{0}]'.format(data)
            else:
                return '+[{0}]'.format(data)
        else:
            return data


def rConvert(data):
    global data_types
    dType = type(data)
    rType = '$'
    if dType == str:
        rType = 'string'
    elif dType == int:
        rType = 'integer'
    elif dType == list:
        rType = 'array'
    return rFormat(data, rType)

def data(arg):
    #print(arg)
    for dataPrefix in data_types.keys():
        if dataPrefix*2 in arg:
            arg = arg.replace(dataPrefix*2, dataPrefix)
    if Type(arg)=='string':
        if flags['setmode']: return arg
        else:
            string = str(arg[1:]).replace('>n','\n').replace('>t','\t').replace('>:',';')
            for word in string.split(' '):
                for dataPrefix in data_types.keys():
                    if word.startswith(dataPrefix):
                        string = string.replace(word, str(data(word)))
            return string
    if Type(arg)=='hex string':
        return data('$%s'%''.join([chr(int(c,16)) for c in chunks(arg[2:],2)]))
    if Type(arg)=='integer':
        if flags['setmode']: return arg
        else: return int(arg[1:])
    if Type(arg)=='float':
        if flags['setmode']: return arg
        else: return float(arg[2:])
    if Type(arg)=='variable':
        if '[' not in arg:
            return data(variables[label(arg)])
        elif '[' in arg and ']' in arg:
            varName = arg[1:arg.index('[')]
            arrayIndex = data(arg.split('[')[1].replace(']',''))
            varData = data(variables[varName])
            if flags['setmode']:
                return varData[arrayIndex]
            else:
                return data(varData[arrayIndex])
    if Type(arg)=='input':
        user_in = input(arg[arg.index('[')+1:arg.index(']')])
        return arg[1] + user_in
    if Type(arg)=='array':
        array = arg[arg.index('[')+1:arg.index(']')].split(',')
        return [item.replace(' \'','').replace("'",'') for item in array]
    
def Type(data):
    global data_types
    try: return [data_types[prefix] for prefix in data_types.keys() if data.startswith(prefix)][0]
    except: pass
    
def evaluate(line):
    #print('\t'+line) # for debugging
    for subline in line.split(';'):
        flags['moveahead']=1
        tokens = subline.split(' ')
        
        if tokens[0] == 'set':
            flags['setmode']=1
            if Type(tokens[2]) == 'input':
                flags['inputmode']=1
            if Type(tokens[2]) == 'variable':
                setType, setDat = Type(variables[label(tokens[2])]), variables[label(tokens[2])]
            elif Type(tokens[2]) == 'array':
                setType = 'array'
                setDat = ''.join(tokens[2:])
            else:
                setType, setDat = Type(tokens[2]), data(tokens[2])
                
            if flags['inputmode']:
                variables[label(tokens[1])] = rFormat(setDat[1:], setDat[0])
            else:
                variables[label(tokens[1])] = rFormat(setDat, setType)
            #print(variables)
            flags['setmode']=0
            flags['inputmode']=0
            
        if tokens[0] == 'add':
            if Type(tokens[3])!='variable':
                    error(line)
            else:
                variables[label(tokens[3])]='%'+'%d'%(data(tokens[1])+data(tokens[2]))
        if tokens[0] == 'sub':
            if Type(tokens[3])!='variable':
                    error(line)
            else:
                variables[label(tokens[3])]='%'+'%d'%(data(tokens[1])-data(tokens[2]))
        if tokens[0] == 'mult':
            if Type(tokens[3])!='variable':
                    error(line)
            else:
                variables[label(tokens[3])]='%'+'%d'%(data(tokens[1])*data(tokens[2]))
        if tokens[0] == 'div':
            if Type(tokens[3])!='variable':
                    error(line)
            else:
                variables[label(tokens[3])]='%'+'%d'%(data(tokens[1])/data(tokens[2]))
        if tokens[0] == 'disp':
             stdout.write('{0}'.format(data(' '.join(tokens[1:]))))
        if tokens[0] == 'dispn':
             stdout.write('{0}\n'.format(data(' '.join(tokens[1:]))))
        if tokens[0] == 'if':
            if tokens[2] == '=':
                if data(tokens[1])==data(tokens[3]): flags['ifstat']=1
                else: flags['ifstat']=0
            elif tokens[2]=='!=':
                if data(tokens[1])!=data(tokens[3]): flags['ifstat']=1
                else: flags['ifstat']=0
            else: error(line)
        if tokens[0] == 'then':
            if flags['ifstat']==1: evaluate(' '.join(tokens[1:]))
        if tokens[0] == 'else':
            if flags['ifstat']==0: evaluate(' '.join(tokens[1:]))
        if tokens[0] == 'jump':
            jumpPointer = tokens[1]
            if Type(jumpPointer) == 'string':
                jumpTo = labels[data(jumpPointer)]
            elif Type(jumpPointer) == 'integer':
                jumpTo = data(jumpPointer) - 2
            flags['pointer'] = jumpTo
        if tokens[0] == 'skip':
            flags['pointer'] += data(tokens[1])+1
        if tokens[0]=='go': flags['pointer'],flags['back']=parsedcode.index('.%s'%tokens[1]),flags['pointer']
        if tokens[0]=='end': flags['pointer']=flags['back']
        if tokens[0]=='delay': time.sleep(data(tokens[1]))
        if tokens[0]=='inc':
            variable = label(tokens[1])
            if len(tokens) == 3:
                incN = data(tokens[2])
            elif len(tokens) == 2:
                incN = 1
            variables[variable] = rFormat(data(variables[variable]) + incN, 'integer')
        if tokens[0]=='dec':
            variable = label(tokens[1])
            if len(tokens) == 3:
                decN = data(tokens[2])
            elif len(tokens) == 2:
                decN = 1
            variables[variable] = rFormat(data(variables[variable]) - incN, 'integer')
        if tokens[0] == 'app':
            arrayName = label(tokens[1])
            appendVal = tokens[2]
            arrayNow = variables[arrayName]
            #print('{0}: {1}'.format(arrayName,variables[arrayName]))
            #print(appendVal)
            variables[arrayName] = rConvert(data(variables[arrayName]) + [appendVal])
        if tokens[0]=='func':
            functions[tokens[1]]={'number_of_arguments':data(tokens[2]),'expression':' '.join(tokens[3:]).replace('->',';')}
        if tokens[0]=='call':
            funcName = tokens[1]
            funcDat = functions[funcName]
            expr = funcDat['expression']
            arguments = [data(arg) for arg in ' '.join(tokens[2:]).split(',')]
            for i in range(funcDat['number_of_arguments']):
                argCall = '|%d'%(i+1)
                argValu = arguments[i]
                #print(argValu)
                expr = expr.replace(argCall,rConvert(argValu))
            evaluate(expr)
        if tokens[0]=='read':
            try: variables[label(tokens[2])]='$%s'%open(data(tokens[1]),'r').read()
            except: pass
        if tokens[0]=='write':
            try: open(data(tokens[1]),'w').write(data(' '.join(tokens[2:]))).close()
            except: pass
        if tokens[0]=='pyth':
            exec(data(' '.join(tokens[1:])))

def runcode(code):
    lines = code.split('\n')
    parsedcode = [line[:line.index('#')-1] if '#' in line else line for line in code.split('\n')]
    for i, line in enumerate(parsedcode):
        tokens = line.split(' ')
        if tokens[0] == 'lbl':
            labels[data(tokens[1])] = i
    while flags['pointer']<len(parsedcode):
        evaluate(parsedcode[flags['pointer']])
        flags['pointer']+=flags['moveahead']

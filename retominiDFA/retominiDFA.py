from graphviz import Digraph
from queue import *
from copy import *


opchar = "|·*()"  # 运算符优先级与其在字符串中的下标对应


# 获取运算符的优先级
def getpri(c):
    return opchar.find(c)


# 获取item中的第一个元素，用于排序
def getFirst(item):
    return item[0]


# 将边集合里面的值按起始结点分组
def devidelist(l):
    newlist = []
    k = 0
    for i in range(1, len(l)):
        if l[i][0] != l[i - 1][0]:
            newlist.append(l[k:i])
            k = i
    newlist.append(l[k:len(l)])
    return newlist


# 求结点a的闭包
def getnodeset(a, l):
    s = []
    s.append(a)
    q = Queue()
    q.put(a)
    while not q.empty():
        e = q.get()
        for i in l:
            if i[0] == e and i[2] == 'ε' and i[1] not in s:
                s.append(i[1])
                q.put(i[1])
    return s


# 以BFS的方式构造图
def resortnode(g, start, end, edgelist):
    no = 0
    s = [-1] * (len(edgelist) + 1)
    q = Queue()
    q.put(start)
    while not q.empty():
        e = q.get()
        if s[e] == -1:
            s[e] = no
            g.node(name=str(no), shape="circle")
            no += 1
        if e == end:
            continue
        for edge in edgelist[e]:
            if s[edge[1]] == -1:
                s[edge[1]] = no
                g.node(name=str(no), shape="circle")
                no += 1
                q.put(edge[1])
            g.edge(str(s[e]), str(s[edge[1]]), label=edge[2])
    g.node(name=str(s[end]), shape="doublecircle")
    g.node(name='', shape="none")
    g.edge('', '0', label="start")


mDFAedgelist = []       # 最小化DFA的边
translist = []          # 最小化DFA的转换条件
# 存边的形式如下：
#       translist   a   b   c
# mDFAedgelist[0]   1   3   ε
# mDFAedgelist[1]   3   ε   5

def rtmdfa(exp):
    # exp = input("Input Regular Expression：")

    # 由正则表达式到逆波兰表达式
    lexp = list(exp)
    k = 0
    # 在正则表达式中添加·运算符
    while k < len(lexp):
        try:
            if ((lexp[k] not in opchar) or lexp[k] == ')' or lexp[k] == '*') and \
                    ((lexp[k + 1] not in opchar) or lexp[k + 1] == '('):
                lexp.insert(k + 1, '·')
        except:
            pass
        k += 1
    opstack = []
    result = []
    # 求逆波兰表达式
    for i in range(len(lexp)):
        if lexp[i] not in opchar:
            result.append(lexp[i])
        else:
            if lexp[i] == '(':
                opstack.append(lexp[i])
            elif lexp[i] == ')':
                while opstack[-1] != '(':
                    result.append(opstack[-1])
                    opstack.pop()
                opstack.pop()
            else:
                if len(opstack) == 0:
                    opstack.append(lexp[i])
                elif opstack[-1] == '(':
                    opstack.append(lexp[i])
                elif getpri(opstack[-1]) >= getpri(lexp[i]):
                    while getpri(opstack[-1]) >= getpri(lexp[i]) and opstack[-1] != '(':
                        result.append(opstack[-1])
                        opstack.pop()
                        if len(opstack) == 0:
                            break
                    opstack.append(lexp[i])
                else:
                    opstack.append(lexp[i])
    while len(opstack):
        result.append(opstack[-1])
        opstack.pop()
    result = ''.join(result)

    # 由逆波兰表达式到NFA
    g = Digraph("NFA", format='png')
    g.graph_attr['rankdir'] = 'LR'  # 设置图的方向为从左向右
    no = 0  # 节点编号
    edgelist = []  # 边集合，边的存放形式为[起始结点， 终止结点， 转移条件 ]
    nodelist = []  # 点集合栈
    selist = []  # 开始节点与结束节点集合栈
    for i in result:
        # 添加起始节点与结束节点
        s = no
        e = no + 1
        if i not in opchar:     # 若当前字符不是运算符，直接添加起始与结束结点并入栈
            nodelist.append([s, e])
            selist.append([s, e])
            edgelist.append([s, e, i])
        else:
            nodeset = []
            if i == '|':        # 若为|运算符，从栈中取出两个点集进行合并，然后入栈
                nodeset.append(nodelist[-1])
                nodeset.append(nodelist[-2])
                nodeset.append(s)
                nodeset.append(e)
                nodelist.pop()
                nodelist.pop()
                nodelist.append(nodeset)
                edgelist.append([s, selist[-1][0], 'ε'])
                edgelist.append([s, selist[-2][0], 'ε'])
                edgelist.append([selist[-1][1], e, 'ε'])
                edgelist.append([selist[-2][1], e, 'ε'])
                selist.pop()
                selist.pop()
                selist.append([s, e])
            elif i == '*':      # 若为*运算符，从栈中取出一个点集，并添加相应的点，然后入栈
                nodelist[-1].append(s)
                nodelist[-1].append(e)
                edgelist.append([s, selist[-1][0], 'ε'])
                edgelist.append([selist[-1][1], e, 'ε'])
                edgelist.append([s, e, 'ε'])
                edgelist.append([selist[-1][1], selist[-1][0], 'ε'])
                selist.pop()
                selist.append([s, e])
            elif i == '·':      # 若为·运算符，从栈中取出两个点集进行合并，然后入栈
                nodeset.append(nodelist[-1])
                nodeset.append(nodelist[-2])
                nodeset.append(s)
                nodeset.append(e)
                nodelist.pop()
                nodelist.pop()
                nodelist.append(nodeset)
                edgelist.append([selist[-1][1], e, 'ε'])
                edgelist.append([s, selist[-2][0], 'ε'])
                edgelist.append([selist[-2][1], selist[-1][0], 'ε'])
                selist.pop()
                selist.pop()
                selist.append([s, e])
        no += 2
    edgelist.sort(key=getFirst)
    start = getnodeset(selist[0][0], edgelist)              # 求DFA开始结点的闭包
    cedgelist = edgelist[:]
    edgelist = devidelist(edgelist)                         # 将边集合里面的值按起始结点分组
    resedgelist = deepcopy(edgelist)
    resortnode(g, selist[0][0], selist[0][1], edgelist)     # 以BFS的方式构造图
    g.render('NFA')

    # 由NFA到DFA
    gd = Digraph("DFA", format='png')
    gd.graph_attr['rankdir'] = 'LR'
    end = selist[0][1]
    DFAedgelist = []
    DFAnodelist = [start]
    blocklist = [1 if end in start else 0]      # 用于标记各结点是否为终止结点，初始判断NFA的终止结点是否在start中
    dic = {}                                    # 临时存放DFA中各结点通过某一符号转换为哪一状态
    for i in exp:
        if i not in opchar:
            dic[i] = []
    q = Queue()
    q.put(start)
    while not q.empty():                        # 以BFS的方式搜索各点的闭包
        e = q.get()
        order = []                              # 记录转移符出现的顺序
        eindex = DFAnodelist.index(e)
        for i in e:
            if i != end:                        # 因为终止结点无出边，需特判一下
                for j in edgelist[i]:
                    if j[2] not in opchar and j[2] != 'ε':      # 若转移条件不为空，则加入order
                        if j[2] not in order:
                            order.append(j[2])
                        for k in getnodeset(j[1], cedgelist):    # 求目标结点的闭包，并加入临时存放转换条件与转换结点的dic中
                            if k not in dic[j[2]]:
                                dic[j[2]].append(k)
        for i in order:                         # 在图中添加结点与边
            if len(dic[i]) != 0:
                if dic[i] in DFAnodelist:       # 若该结点已经在图中，只需加边
                    idx = DFAnodelist.index(dic[i])
                    gd.edge(str(eindex), str(idx), label=i)
                    DFAedgelist.append([eindex, idx, i])
                else:                           # 不在图中，则需判断该结点是否为DFA的终止结点
                    tmp = deepcopy(dic[i])
                    DFAnodelist.append(tmp)
                    blocklist.append(1 if end in tmp else 0)
                    q.put(tmp)
                    gd.node(name=str(eindex), shape=("doublecircle" if end in e else "circle"))
                    gd.node(name=str(DFAnodelist.index(dic[i])), shape=("doublecircle" if end in dic[i] else "circle"))
                    gd.edge(str(eindex), str(DFAnodelist.index(dic[i])), label=i)
                    DFAedgelist.append([eindex, DFAnodelist.index(dic[i]), i])
                dic[i].clear()
    gd.node(name='', shape="none")
    gd.edge('', '0', label="start")
    gd.render('DFA')

    # 由DFA到miniDFA
    mgd = Digraph("miniDFA", format='png')
    mgd.graph_attr['rankdir'] = 'LR'  # 设置图的方向为从左向右
    DFAedgelist = devidelist(DFAedgelist)
    newblocklist = [-1] * len(blocklist)                       # 记录分组后的结点的编号
    for i in exp:                                              # 获取转移符列表
        if (i not in opchar) and (i not in translist):
            translist.append(i)
    cmplist = blocklist[:]                                     # 用来和旧的状态比较
    tp = []                                                    # 用于临时存放各点能到达的点,其转换条件与translist中转换条件的下标一致
    while True:
        for el in range(len(blocklist)):
            k = -1
            for edges in range(len(DFAedgelist)):
                if DFAedgelist[edges][0][0] == el:
                    k = edges
                    break
            if k != -1:
                for ts in translist:
                    flag = False
                    for e in DFAedgelist[k]:                  # 若该结点能通过某一转换条件到达另一个结点，则存入这个结点
                        if e[2] == ts:
                            tp.append(cmplist[e[1]])
                            flag = True
                    if not flag:                               # 不能到达则填充ε字符
                        tp.append('ε')
                tp.append(blocklist[el])                       # 将是否为终结节点存入
                tp.append(cmplist[el])                         # 最后将当前结点的区号放到末尾
            else:
                for i in range(len(translist)):
                    tp.append('ε')
                tp.append(blocklist[el])                       # 将是否为终结节点存入
                tp.append(cmplist[el])
            if tp in mDFAedgelist:                             # 若当前类型的结点已存在，则其区号直接在mDFAedgelist中找
                idx = mDFAedgelist.index(tp)
                newblocklist[el] = idx
            else:
                mDFAedgelist.append(deepcopy(tp))              # 若不存在，放入newblocklist的末尾，区号为newblocklist的长度-1
                newblocklist[el] = len(mDFAedgelist) - 1
            tp.clear()
        if newblocklist == cmplist:                            # 若新的状态与旧的状态相同则跳出
            break
        mDFAedgelist.clear()
        cmplist.clear()
        cmplist = newblocklist[:]
        newblocklist = [-1] * len(blocklist)
    nodeset = set()
    for e in mDFAedgelist:
        if e[-1] not in nodeset:
            nodeset.add(e[-1])
            mgd.node(name=str(e[-1]), shape="doublecircle" if blocklist[newblocklist.index(e[-1])] else "circle")
        for i in range(len(e)-2):
            if e[i] == 'ε':
                continue
            if e[i] not in nodeset:
                nodeset.add(e[i])
                mgd.node(name=str(e[i]), shape="doublecircle" if blocklist[newblocklist.index(e[i])] else "circle")
            mgd.edge(str(e[-1]), str(e[i]), label=translist[i])
    mgd.node(name='', shape="none")
    mgd.edge('', '0', label="start")
    mgd.render('miniDFA')
    for i in mDFAedgelist:
        if blocklist[newblocklist.index(i[-1])]:
            i.append(True)
        else:
            i.append(False)
    return result            # 返回逆波兰表达式


# 对输入串进行分析
def analystr(s):
    while (True):
        flag = mDFAedgelist[0][-1]                  # 记录到达结点的状态，初始状态为开始结点的状态
        loc = 0
        for i in s:
            if i not in translist:                  # 若存在不在转移符中的字符，则直接返回False
                return False
            for j in range(len(translist)):
                if translist[j] == i:
                    if mDFAedgelist[loc][j] == 'ε':     # 若存在走不动的情况直接返回False
                        return False
                    else:
                        flag = mDFAedgelist[mDFAedgelist[loc][j]][-1]           # 若能走动，修改当前到达的结点以及当前到达结点的状态
                        loc = mDFAedgelist[mDFAedgelist[loc][j]][-2]
        if flag:
            return True
        else:
            return False

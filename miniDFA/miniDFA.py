# a(a|b)*a(ab)*
# a·(ac|b)*|(ab|a)
# a*(abb)*b(b|a)*
# (a*|b*)b(ba)*
# (ab)*(a*|b*)(ba)*
# (a|b)*aa
# a*b
# a(ac|b)*|(ab|a)

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


def main():
    exp = input("Input Regular Expression：")

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
    print("Reverse Polish Notation:", result)

    # 由逆波兰表达式到NFA
    g = Digraph("NFA", format='png')
    g.graph_attr['rankdir'] = 'LR'  # 设置图的方向为从左向右
    no = 0  # 节点编号
    edgelist = []  # 边集合
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
    start = getnodeset(selist[0][0], edgelist)
    cedgelist = edgelist[:]
    edgelist = devidelist(edgelist)
    print("Edge Set: ", edgelist, '\n')
    resortnode(g, selist[0][0], selist[0][1], edgelist)
    g.view()

    # 由NFA到DFA
    gd = Digraph("DFA", format='png')
    gd.graph_attr['rankdir'] = 'LR'
    end = selist[0][1]
    DFAedgelist = []
    DFAnodelist = [start]
    blocklist = [1 if end in start else 0]      # 标记结点是否为终止结点
    dic = {}
    for i in exp:
        if i not in opchar:
            dic[i] = []
    q = Queue()
    q.put(start)
    while not q.empty():
        e = q.get()
        order = []
        eindex = DFAnodelist.index(e)
        for i in e:
            if i != end:
                for j in edgelist[i]:
                    if j[2] not in opchar and j[2] != 'ε':
                        if j[2] not in order:
                            order.append(j[2])
                        for k in getnodeset(j[1], cedgelist):
                            if k not in dic[j[2]]:
                                dic[j[2]].append(k)
        for i in order:
            if len(dic[i]) != 0:
                if dic[i] in DFAnodelist:
                    idx = DFAnodelist.index(dic[i])
                    gd.edge(str(eindex), str(idx), label=i)
                    DFAedgelist.append([eindex, idx, i])
                else:
                    tmp = deepcopy(dic[i])
                    DFAnodelist.append(tmp)
                    blocklist.append(1 if end in tmp else 0)
                    q.put(tmp)
                    gd.node(name=str(eindex), shape=("doublecircle" if end in e else "circle"))
                    gd.node(name=str(DFAnodelist.index(dic[i])), shape=("doublecircle" if end in dic[i] else "circle"))
                    gd.edge(str(eindex), str(DFAnodelist.index(dic[i])), label=i)
                    DFAedgelist.append([eindex, DFAnodelist.index(dic[i]), i])
                dic[i].clear()
    print("DFA Edge Set: ", DFAedgelist)
    print("Block List: ", blocklist, '\n')
    gd.node(name='', shape="none")
    gd.edge('', '0', label="start")
    gd.view()

    # 由DFA到miniDFA
    mgd = Digraph("miniDFA", format='png')
    mgd.graph_attr['rankdir'] = 'LR'  # 设置图的方向为从左向右
    DFAedgelist = devidelist(DFAedgelist)
    translist = []
    mDFAedgelist = []
    newblocklist = [-1] * len(blocklist)
    for i in exp:
        if (i not in opchar) and (i not in translist):
            translist.append(i)
    cmplist = blocklist[:]
    tp = []
    while True:
        for el in range(len(blocklist)):
            if el < len(DFAedgelist):
                for ts in translist:
                    flag = False
                    for e in DFAedgelist[el]:
                        if e[2] == ts:
                            tp.append(cmplist[e[1]])
                            flag = True
                    if not flag:
                        tp.append('ε')
                tp.append(cmplist[el])
            else:
                for i in range(len(translist)):
                    tp.append('ε')
                tp.append(cmplist[el])
            if tp in mDFAedgelist:
                idx = mDFAedgelist.index(tp)
                newblocklist[el] = idx
            else:
                mDFAedgelist.append(deepcopy(tp))
                newblocklist[el] = len(mDFAedgelist) - 1
            tp.clear()
        if newblocklist == cmplist:
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
        for i in range(len(e)-1):
            if e[i] == 'ε':
                continue
            if e[i] not in nodeset:
                nodeset.add(e[i])
                mgd.node(name=str(e[i]), shape="doublecircle" if blocklist[newblocklist.index(e[i])] else "circle")
            mgd.edge(str(e[-1]), str(e[i]), label=translist[i])
    mgd.node(name='', shape="none")
    mgd.edge('', '0', label="start")
    mgd.view()
    for i in mDFAedgelist:
        if blocklist[newblocklist.index(i[-1])]:
            i.append(True)
        else:
            i.append(False)
    print("New Block List", newblocklist)
    print("miniDFA Edge Set: ", mDFAedgelist)
    while(True):
        s=input("Input string to analyze(Input -1 to exit):")
        if s == "-1":
            break
        flag = mDFAedgelist[0][-1]
        flag1 = False
        loc = 0
        for i in s:
            for j in range(len(translist)):
                if translist[j] == i:
                    if mDFAedgelist[loc][j] == 'ε':
                        flag1 = True
                        break
                    else:
                        flag = mDFAedgelist[mDFAedgelist[loc][j]][-1]
                        loc = mDFAedgelist[mDFAedgelist[loc][j]][-2]
            if flag1 :
                break
        if flag1:
            print("Not Accepted")
        else:
            print("Accepted")


if __name__ == '__main__':
    main()

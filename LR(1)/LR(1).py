from graphviz import Digraph
from queue import *


def getFirst(dic, k, n):
    st = set()
    for i in dic[k]:
        if 'A' <= i[0] <= 'Z':                       # 若当前产生式的开头为非终结符，则求该串的First集合
            t = i
            if t[0] == k and [''] not in dic[k]:
                continue
            if t[0] == n and [''] not in dic[n]:
                continue
            elif t[0] == n and [''] in dic[n] or t[0] == k and [''] in dic[k]:
                t = t[1:]
            flag = True                                            # 标记是否可以继续求后续非终结符的First集合
            for j in range(len(t)):
                if 'A' <= t[j] <= 'Z':                             # 若后续字符为为非终结符，则进行处理
                    if t[j] == n and [''] in dic[n]:
                        continue
                    elif t[j] == n and [''] not in dic[n]:
                        break
                    if flag:                                       # 求后续非终结符的First集合
                        tmp = getFirst(dic, t[j], n)
                        st = st | tmp
                    else:                                          # 上一个字符的First集合中不含ε，若位处理到最后，并且ε在其中，则将ε移除
                        if j < len(t) and '' in st:
                            st.remove('')
                        break
                    if '' not in tmp:                            # 若ε不在后续字符的First集合中，将flag置为False
                        flag = False
                else:                                              # 若后续字符为终结符，直接加入First集合，并终止循环
                    st.add(t[j])
                    break
                if not flag:
                    break
        else:                                                      # 若当前产生式的开头为终结符，直接加到Firs集合中
            st.add(i[0])
    return st


# 求某一串的first集合
def extendFirst(first, s, p):
    if len(s) == 0:
        return p
    res = []
    for i in range(len(s)):
        if 'A' <= s[i] <= 'Z':
            for j in first[s[i]]:
                if j not in res and j != '':
                    res.append(j)
            if '' not in first[s[i]]:
                break
            if '' in first[s[i]] and i == len(s)-1:
                res.extend(p)
        else:
            if s[i] not in res:
                res.append(s[i])
                break
    res = tuple(res)
    return res


# 求某一结点可扩展的产生式
def extendPd(pd, pdic, first):
    res = [pd]
    q = Queue()
    q.put(pd)
    while not q.empty():
        e = q.get()
        idx = e[2]
        if idx < len(e[1]) and 'A' <= e[1][idx] <= 'Z':     # 若当前字符为非终结符则进行扩展
            nt = e[1][idx]
            s = e[1][idx+1:]
            for i in pdic[nt]:
                tmp = (nt, i, 0, extendFirst(first, s, e[3]))
                if tmp not in res:                          # 若得到的产生式不在当前状态中则加入
                    res.append(tmp)
                    q.put(tmp)
    return res


# 求DFA
def extendDfa(dfanode, dfaedge, pdic, first):
    q = Queue()
    dfanode[0] = tuple(extendPd(dfanode[0][0], pdic, first))        # 将初始结点进行扩展
    q.put(dfanode[0])
    while not q.empty():
        e = q.get()
        tmpdic = {}
        keys = []
        for i in range(len(e)):
            if e[i][2] < len(e[i][1]) and e[i][1][0] != '':                      # 若前一状态的某一产生式还未分析到末尾，则有可能有新的状态
                op = e[i][1][e[i][2]]
                if op not in tmpdic.keys():
                    tmpdic[op] = [i]
                    keys.append(op)
                else:
                    tmpdic[op].append(i)
        for i in keys:
            tmp = []
            for j in tmpdic[i]:
                t = (e[j][0], e[j][1], e[j][2]+1, e[j][3])
                for k in extendPd(t, pdic, first):
                    if k not in tmp:
                        tmp.append(k)
            tmp = tuple(tmp)
            if tmp not in dfanode:
                dfanode.append(tmp)
                q.put(tmp)
            dfaedge.append((dfanode.index(e), dfanode.index(tmp), i))


# 将边按起始结点分组
def divideEdge(dfaedge):
    newlist = []
    k = 0
    for i in range(1, len(dfaedge)):
        if dfaedge[i][0] != dfaedge[i - 1][0]:
            newlist.append(dfaedge[k:i])
            k = i
    newlist.append(dfaedge[k:len(dfaedge)])
    return newlist


# 将每个状态中的产生式连接成一整个字符串，用于在DFA图上显示
def getLabel(node, n):
    pro = ['s' + str(n)]
    for i in node:
        tmp = list(i[1])
        tmp.insert(i[2], '.')
        t = ',' + '/'.join(i[3])
        tmp.append(t)
        tmp = ' '.join(tmp)
        pro.append(i[0] + ' → ' + tmp)
    pro = '\n'.join(pro)
    return pro


# 绘制DFA图
def drawDFA(dfanode, dfaedge):
    dfa = Digraph('dfa_LR(1)', format='png')
    dfa.graph_attr['rankdir'] = 'LR'
    dfa.node(name='s0', label=getLabel(dfanode[0], 0))
    q = Queue()
    flag = [False] * len(dfanode)       # 用于标记某一状态是否已加入DFA图
    flag[0] = True
    q.put(0)
    while not q.empty():                # BFS的方式构造DFA图
        e = q.get()
        k = -1
        for i in range(len(dfaedge)):   # 找以该状态为起始结点的边
            if dfaedge[i][0][0] == e:
                k = i
                break
        if k == -1:
            continue
        for i in dfaedge[k]:
            if not flag[i[1]]:
                dfa.node(name='s'+str(i[1]), label=getLabel(dfanode[i[1]], i[1]))
                flag[i[1]] = True
                q.put(i[1])
            dfa.edge('s'+str(e), 's'+str(i[1]), label=i[2])
    dfa.node(name='', shape='none')
    dfa.edge('', 's0', label='start')
    dfa.view()


# 创建分析表
def buildTable(action, goto, dfanode, dfaedge, apd, nt, term):
    flag = True
    for i in range(len(dfanode)):
        t = dfanode[i]
        n = -1
        for item in range(len(dfaedge)):            # 找到该状态的边集
            if dfaedge[item][0][0] == i:
                n = item
                break
        for j in t:
            if j[2] == len(j[1]) or j[1][0] == '':  # 若产生式已分析到最后，则操作为accept或者reduce
                if j[0][-1] == '0':
                    action[i][-1] = 'acc'
                else:
                    idx = apd.index(j[0:2])
                    for k in j[3]:
                        if action[i][term.index(k)] == '-' or action[i][term.index(k)] == 'r' + str(idx):
                            action[i][term.index(k)] = 'r' + str(idx)
                        else:
                            action[i][term.index(k)] = action[i][term.index(k)] + '/' + 'r' + str(idx)
                            flag = False
            else:  # 若产生式未分析完，则找出该状态的出边，根据出边的转换条件进行goto操作还是shift操作
                for item in dfaedge[n]:
                    if item[2] == j[1][j[2]]:
                        if 'A' <= item[2] <= 'Z':                   # 若到达目标结点是通过非终结符到达，则对goto列表进行操作
                            goto[i][nt.index(item[2])] = str(item[1])
                        else:                                       # 否则，进行的操作为shift操作
                            if action[i][term.index(item[2])] == '-' or action[i][term.index(item[2])] == 's' + str(item[1]):
                                action[i][term.index(item[2])] = 's' + str(item[1])
                            elif action[i][term.index(item[2])][-1] != str(item[1]):
                                action[i][term.index(item[2])] = action[i][term.index(item[2])] + '/' + 's' + str(item[1])
                                flag = False
                        break
    print('分析表:')
    print('  ', 'Action'.center(len(term)*5-1), 'Goto'.center(len(nt)*5-1))
    print('  ', end=' ')
    for i in term:
        print(i.center(5), end=' ')
    for i in nt:
        print(i.center(5), end=' ')
    print(' ')
    for i in range(len(dfanode)):
        print(str(i).ljust(2), end=' ')
        for j in action[i]:
            print(j.center(5), end=' ')
        for j in goto[i]:
            print(j.center(5), end=' ')
        print('')
    print('')
    return flag


def anaystr(action, goto, apd, st, term, nt):
    astack = ['$', 's0']
    istack = ['$']
    istack.extend(st.split(' ')[::-1])
    wid1 = 4 * len(action)
    wid2 = 4 * len(istack)
    n = 1
    op = ''
    print('  ', '分析栈'.center(wid1), '输入'.center(wid2), '操作')
    while True:
        for i in range(len(astack[-1])):
            if not '0' <= astack[-1][i] <= '9':
                id = int(astack[-1][i+1:])
                break
        op = action[id][term.index(istack[-1])]        # 从action列表中获取当前要进行的操作
        if op[0] == 's':                                                # shift操作
            k = op
            op = 'shift'
            print(str(n).ljust(2), ' '.join(astack).ljust(wid1), ' '.join(istack[::-1]).rjust(wid2), '    ' + op)
            astack.append(istack[-1])                                   # 移进分析栈的栈顶
            astack.append(k)                                            # 移进目标状态
            istack.pop()                                                # 弹出分析栈栈顶
        elif op[0] == 'r':                                              # reduce操作
            idx = op[1:]
            pro = apd[int(idx)]
            tmp = ' '.join(pro[1])
            op = 'reduce ' + pro[0] + ' → ' + ('ε' if tmp == '' else tmp)
            print(str(n).ljust(2), ' '.join(astack).ljust(wid1), ' '.join(istack[::-1]).rjust(wid2), '    ' + op)
            if tmp != '':
                k = len(pro[1]) - 1
                l = len(astack) - 1
                while k >= 0:                                               # 对于分析栈从后往前遍历，遍历到整个产生式的右端都能匹配完为止
                    if astack[l] == pro[1][k]:
                        k = k - 1
                    l = l - 1
                astack = astack[:l+1]                                       # 对分析栈进行切片，取开头到产生式右端能匹配完的位置
            astack.append(pro[0])
            k = 's' + goto[int(astack[-2][1:])][nt.index(pro[0])]
            astack.append(k)                                            # 将goto能到达的状态如分析栈
        elif op[0] == 'a':                                              # accept
            op = 'accept'
            print(str(n).ljust(2), ' '.join(astack).ljust(wid1), ' '.join(istack[::-1]).rjust(wid2), '    ' + op)
        else:                                                           # 无对应的操作则不接受
            op = 'not accept'
            print(str(n).ljust(2), ' '.join(astack).ljust(wid1), ' '.join(istack[::-1]).rjust(wid2), '    ' + op)
        n = n + 1
        if op == 'accept' or op == 'not accept':
            return


def main():
    print("请输入文法:")
    pd = []
    for line in iter(input, ''):
        pd.append(line)
    start = pd[0][0] + '0'
    pdic = {start: [(start[0])]}     # 存各非终结符能推出的式子
    nt = []                          # 存非终结符
    term = []                        # 存终结符
    for i in pd:
        pdic[i[0]] = []
        nt.append(i[0])
        tmp = i[4:].split('|')
        for j in tmp:
            tmp = j.strip().split(' ')
            for k in tmp:
                if not 'A' <= k <= 'Z' and k not in term and k != 'ε':
                    term.append(k)
            if 'ε' in tmp:
                tmp[tmp.index('ε')] = ''
            pdic[i[0]].append(tuple(tmp))

    term.append('$')
    first = {}
    for i in nt:
        first[i] = getFirst(pdic, i, i)
    dfaNode = [[(start, tuple([start[0]]), 0, tuple(['$']))]]  # 各节点所包含的产生式
    dfaEdge = []  # 存所有边
    extendDfa(dfaNode, dfaEdge, pdic, first)
    dfaEdge = divideEdge(dfaEdge)
    k = 0
    for i in range(len(dfaNode)):
        print('状态', getLabel(dfaNode[i], i), sep='')
        if k < len(dfaEdge) and dfaEdge[k][0][0] == i:
            for j in dfaEdge[k]:
                print('状态s', i, '通过条件 ', j[2], ' 跳转至', '状态s', j[1], sep='')
            k = k + 1
        print('\n')
    drawDFA(dfaNode, dfaEdge)
    apd = [(start, tuple([start[0]]))]  # 存所有产生式
    goto = []  # 存分析表的goto部分
    action = []  # 存分析表的action部分
    for i in range(len(dfaNode)):
        goto.append(['-'] * len(nt))
        action.append(['-'] * len(term))
    for i in nt:
        for j in pdic[i]:
            apd.append((i, j))
    print('产生式:')
    for i in range(len(apd)):
        print(str(i).ljust(2), apd[i][0] + ' -> ' + (' '.join(apd[i][1]) if ' '.join(apd[i][1]) != '' else 'ε'))
    print('\n')
    if not buildTable(action, goto, dfaNode, dfaEdge, apd, nt, term):
        print('该文法无法使用LR(1)分析')
        return
    while True:
        s = input("输入待分析的串:\n")
        if s == '':
            break
        anaystr(action, goto, apd, s, term, nt)
        print('')


if __name__ == '__main__':
    main()
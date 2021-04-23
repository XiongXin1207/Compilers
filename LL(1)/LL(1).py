from copy import *

# 判断一个非终结符的所有产生式有没有公共前缀
def hascmprefix(l):
    st = set()
    for i in l:
        st.add(i[0])
    if len(st) == len(l):
        return False
    else:
        return True


# 求a,b两个串的最大公共前缀
def commprefix(a, b):
    result = []
    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            result.append(a[i])
        else:
            break
    return result


# 求k的First集合
def getFirst(dic, k, n):
    st = set()
    for i in k:
        if 'A' <= i[0] <= 'Z':                       # 若当前产生式的开头为非终结符，则求该串的First集合
            t = i
            if t[0] == n and ['ε'] not in dic[n]:
                continue
            elif t[0] == n and ['ε'] in dic[n]:
                t = t[1:]
            flag = True                              # 标记是否可以继续求后续非终结符的First集合
            for j in range(len(t)):
                if 'A' <= t[j] <= 'Z':               # 若后续字符为为非终结符，则进行处理
                    if t[j] == n and ['ε'] in dic[n]:
                        continue
                    elif t[j] == n and ['ε'] not in dic[n]:
                        break
                    if flag:                         # 求后续非终结符的First集合
                        tmp = getFirst(dic, dic[t[j]], n)
                        st = st | tmp
                    else:                            # 上一个字符的First集合中不含ε，若未处理到最后，并且ε在其中，则将ε移除
                        if j < len(t) and 'ε' in st:
                            st.remove('ε')
                        break
                    if 'ε' not in tmp:              # 若ε不在后续字符的First集合中，将flag置为False
                        flag = False
                else:                                # 若后续字符为终结符，直接加入First集合，并终止循环
                    st.add(t[j])
                    break
                if not flag:
                    break
        else:                                        # 若当前产生式的开头为终结符，直接加到Firs集合中
            st.add(i[0])
    return st


# 求t的Follow集合
def getUnion(follow, contain, t, n):                    # contain 为非终结包含哪些非终结符的follow集合
    st = set()
    for i in contain[t]:                             # 一直递归到不包含其他任意一个非终结符的follow集合的非终结符为止
        if len(contain[i]) != 0 and (t not in contain[i]) and i != n:
            st = st | getUnion(follow, contain, i, n) | follow[i]
        else:
            st = st | follow[i]
    return st


# 求每个产生式的select集合
def getSelect(First, Follow, st):
    if st[1] == 'ε':
        return Follow[st[0]]
    sel = set()
    for i in range(1, len(st)):
        if 'A' <= st[i] <= 'Z':
            sel = sel | First[st[i]]
            if 'ε' not in First[st[i]]:
                return sel
            else:
                sel.remove('ε')
        else:
            sel.add(st[i])
            return sel
    sel = sel | Follow[st[0]]
    return sel


def main():
    print("Input grammar:")
    pd = []
    for line in iter(input, ''):
        pd.append(line)
    dic = {}    # 各非终结符所对应的产生式
    nT = []     # 非终结符列表
    term = []   # 终结符列表
    for i in pd:
        tmp = i[4:].split('|')
        dic[i[0]] = []
        for j in tmp:
            dic[i[0]].append(j.strip(' ').split(' '))
        nT.append(i[0])
    for k in nT:        # 求非终结符
        for i in dic[k]:
            for j in i:
                if not 'A' <= j <= 'Z' and j not in term and j != 'ε':
                    term.append(j)
    startnT = nT[0]     # 记录起始非终结符
    trans = {}          # 记录非终结符扩展了几次，如L、L0、L1
    for i in nT:
        trans[i] = 0

    # 消除左递归
    for i in range(len(nT)):
        for j in range(i):
            tmp = []
            for value in dic[nT[i]]:
                if value[0][0] == nT[j]:        # 若产生式最左端符号为非终结符，将其替换
                    for k in dic[nT[j]]:
                        t = deepcopy(k)
                        t.extend(value[1:])
                        tmp.append(t)
                else:
                    tmp.append(value)
            dic[nT[i]] = tmp
        tmpa = []                               # 对于形如A -> Aɑ1|Aɑ2|...|Aɑn|β1|β2|...|βm，
        tmpb = []                               # tmpa存的是各α的值，tmpb存的是各β的值
        for l in dic[nT[i]]:
            if l[0] == nT[i]:
                tmpa.append(l[1:])
            else:
                tmpb.append(l)
        if len(tmpa) == 0:
            continue
        dic[nT[i]].clear()
        newnode = nT[i] + '0'
        trans[nT[i]] = trans[nT[i]] + 1
        for l in tmpb:                          # 将tmpb的值加上A`，存入被清空后的dic{A}中
            if l[0] == 'ε':
                l.clear()
            l.append(newnode)
            dic[nT[i]].append(l)
        dic[newnode] = []
        for l in tmpa:                          # 将tmpa的值加上A`，存入dic{A`}中
            l.append(newnode)
            dic[newnode].append(l)
        dic[newnode].append(['ε'])             # 在最后dic{A`}中加上ε
        nT.append(newnode)
    print("消除左递归:")
    for i in nT:
        print(i, '->', end=' ')
        for j in dic[i]:
            print(' '.join(j), end=' | ' if j != dic[i][-1] else '\n')
    print('\n')

    # 提取左因子
    for k in nT:
        if hascmprefix(dic[k]):                 # 若某一非终结符的所有产生式中含有公共前缀的产生式则进行提取左因子操作
            pfixl = []
            for i in range(len(dic[k])):        # 求得两两产生式的公共前缀
                for j in range(i):
                    tmp = commprefix(dic[k][i], dic[k][j])
                    if len(tmp) != 0:
                        pfixl.append(tmp)
            pfixl.sort(key=len)                 # 对得到的所有公共前缀进行排序，取最大公共前缀进行提取
            pfix = pfixl[-1]
            newnode = k + str(trans[k])
            trans[k] = trans[k] + 1
            tmpa = []
            tmpb = []
            t = deepcopy(pfix)
            t.append(newnode)
            tmpa.append(t)
            for l in dic[k]:                    # 若有以最大公共前缀开头的产生式，则提取
                if (''.join(l)).startswith(''.join(pfix)):
                    s = l[len(pfix):]
                    if len(s) == 0:
                        s = ['ε']
                    tmpb.append(s)
                else:
                    tmpa.append(l)
            nT[nT.index(k)] = newnode           # 将原来A的位置变为A`,A加到列表的末尾，在循环到后面时可以继续对A中剩余的左因子进行提取
            nT.append(k)
            dic[k] = tmpa
            dic[newnode] = tmpb
    print("提取左因子：")
    for i in nT:
        print(i, '->', end=' ')
        for j in dic[i]:
            print(' '.join(j), end=' | ' if j != dic[i][-1] else '\n')
    print('\n')

    # 求First集合
    First = {}      # 存first集合
    for i in nT:
        First[i] = set()
    for i in nT:
        First[i] = getFirst(dic, dic[i], i)
    print("First集合：")
    for i in nT:
        print("First( %s ) = " % i, First[i])
    print('\n')

    # 求Follow集合
    Follow = {}             # 存follow集合
    Contain = {}            # 各非终极符包含的其他非终结符
    eachContain = set()     # 相互包含的终结符，最后处理
    for i in nT:
        Follow[i] = set()
        Contain[i] = set()
    Follow[startnT].add('$')
    for i in nT:
        for j in dic[i]:
            for k in range(len(j)):
                if 'A' <= j[k] <= 'Z':      # 在产生式右边找非终结符
                    t = k + 1
                    while t < len(j) + 1:
                        if t == len(j):     # 若该非终结符直接或间接（其紧跟的串的first集合中含有ε）成为产生式末尾，则其follow集合包含产生式左边的非终结符的follow集合
                            if j[k] != i:
                                Contain[j[k]].add(i)
                                if j[k] in Contain[i]:
                                    eachContain.add((j[k], i))
                            break
                        else:               # 否则其follow集合包含紧跟串的first集合
                            if 'A' <= j[t] <= 'Z':
                                Follow[j[k]] = Follow[j[k]] | First[j[t]]
                                if 'ε' in First[j[t]]:      # 若其中含ε，将其移除
                                    Follow[j[k]].remove('ε')
                                    t = t + 1
                                else:
                                    break
                            else:
                                Follow[j[k]].add(j[t])
                                break
    for i in nT:
        if len(Contain[i]) != 0:            # 若该非终结符包含了其他非终结符的follow集合，将其follow集合与被包含的非终结符的follow集合相并
            Follow[i] = Follow[i] | getUnion(Follow, Contain, i, i)
    for i in eachContain:                   # 相互包含的非终结符相等
        Follow[i[0]] = Follow[i[0]] | Follow[i[1]]
        Follow[i[1]] = deepcopy(Follow[i[1]])
    print("Follow集合：")
    for i in nT:
        print("Follow( %s ) = " % i, Follow[i])
    print('\n')

    # 构建分析表
    term.append('$')                    # 非终结符中加入$
    produce = []                        # 存单独的产生式
    for i in nT:
        for j in dic[i]:                # 为各产生式编号
            tmp = [i]
            tmp.extend(j)
            produce.append(deepcopy(tmp))
    print('产生式:')
    for i in range(len(produce)):
        print(str(i).ljust(2), produce[i][0] + ' -> ' + ' '.join(produce[i][1:]))
    print('\n')
    table = {}                          # 存分析表
    flag = True
    for i in nT:
        table[i] = ['-'] * len(term)
    for i in range(len(produce)):
        sel = getSelect(First, Follow, produce[i])  # 获取产生式的Select集合
        for j in sel:
            if table[produce[i][0]][term.index(j)] == '-':
                table[produce[i][0]][term.index(j)] = str(i)
            else:
                flag = False
                table[produce[i][0]][term.index(j)] = table[produce[i][0]][term.index(j)] + '/' + str(i)
    print('分析表:')
    print('    ', '      '.join(term))
    for i in nT:
        print(i.ljust(5), end='')
        for j in table[i]:
            print(j.ljust(7), end='')
        print('')
    print('\n')
    if not flag:
        print('该文法无法用LR(0)分析')
        return
    while True:
        st = input("输入待分析的串:\n")
        if st == '':
            break
        analystr(produce, table, term, st, startnT)
        print('')


# 分析输入串
def analystr(produce, table, term, st, startnT):
    astack = ['$', startnT]     # 分析栈
    istack = ['$']              # 输入栈
    wid = 4 * len(st) + 2
    istack.extend(st.split(' ')[::-1])
    num = 1
    op = ''
    print('  ', '分析栈'.center(max(wid, 8)), '输入'.center(max(wid, 8)), '\t动作'.ljust(10), sep='\t')
    while True:
        atop = astack[-1]
        itop = istack[-1]
        no = ''
        if 'A' <= astack[-1] <= 'Z':    # 若分析栈栈顶为非终结符，则通过产生式替换栈顶
            no = table[atop][term.index(itop)]
            if no != '-':
                op = produce[int(no)][0] + ' -> ' + ' '.join(produce[int(no)][1:])
            else:                       # 若分析栈栈顶的非终结符与输入栈中的终结符无对应的产生式，则对应的操作为不接受
                op = '不接受'
        else:                           # 若为非终结符
            if atop == itop:
                if atop == '$':         # 若分析栈栈顶与输入栈栈顶相等且为$，则对应的操作为接受
                    op = '接受'
                else:                   # 若不等于$，则对应的操作为匹配
                    op = '匹配'
            else:
                op = '不接受'
        print(str(num).ljust(2), ' '.join(astack[::-1]).rjust(max(wid, 8)),
              ' '.join(istack[::-1]).rjust(max(wid, 8)), ('\t' + op).ljust(10), sep='\t')
        if op == '不接受' or op == '接受':   # 若操作为不接受或接受则直接返回
            return
        elif op == '匹配':    # 若操作为匹配，则将分析栈与输入栈的栈顶都弹出
            astack.pop()
            istack.pop()
        else:                 # 其他的就将分析栈的栈顶替换为对应产生式的右端，特别地，当右端为ε时直接消去
            astack.pop()
            if produce[int(no)][1] != 'ε':
                astack.extend(produce[int(no)][1:][::-1])
        num = num + 1


if __name__ == "__main__":
    main()

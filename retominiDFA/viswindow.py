from tkinter import *
import tkinter.messagebox
import retominiDFA


window = Tk()
window.title('词法分析器')
window.geometry('1300x500')
window.resizable(0, 0)
e1 = Entry(window, show=None, width=20)     # 输入正则表达式的文本框
e1.grid(row=1, column=1, sticky=W)
rpexp = StringVar()                         # 存逆波兰表达式
label4 = Label(window, textvariable=rpexp, font=('KaiTi', 11), width=30)
label4.grid(row=1, column=3)

e2 = Entry(window, show=None, width=20)     # 输入待分析串的文本框
e2.grid(row=2, column=1, sticky=W)

aresult = StringVar()                       # 显示分析串结果的标签
label3 = Label(window, textvariable=aresult, font=('KaiTi', 11), width=18)
label3.grid(row=2, column=3)

s = Scrollbar(window, orient=HORIZONTAL)    # 显示图片的框体
s.grid(row=5, column=0, columnspan=8, sticky='W', ipadx=620)
mtext = Text(window, height=29, xscrollcommand=s.set, wrap='none')
mtext.grid(row=4, column=0, columnspan=8, sticky=W + E)
s.config(command=mtext.xview)

picNFA = ''        # 读NFA.png
picDFA = ''        # 读DFA.png
picMiniDFA = ''    # 读miniDFA.png


# 输入正则表达式的确定按钮的回调函数
def clkbtn1():
    exp = e1.get()
    if exp == '':                           # 若输入为空，提示输入
        tkinter.messagebox.showwarning('', '请输入正则表达式!')
        return
    npexp = retominiDFA.rtmdfa(exp)
    label4['width'] = 30 if 14 + len(npexp) + npexp.count('·') < 30 else 14 + len(npexp) + npexp.count('·') < 30
    rpexp.set('逆波兰表达式: ' + npexp)
    label4['background'] = 'yellow'
    global picNFA
    global picDFA
    global picMiniDFA
    picNFA = PhotoImage(file='NFA.png')
    picDFA = PhotoImage(file='DFA.png')
    picMiniDFA = PhotoImage(file='miniDFA.png')
    mtext.delete(1.0, END)
    mtext.insert(1.0, 'miniDFA:\n')
    mtext.image_create(END, image=picMiniDFA)


# 输入待分析串的确定按钮的回调函数
def clkbtn2():
    s = e2.get()
    if e1.get() == '':                             # 若输入为空，提示输入
        tkinter.messagebox.showwarning('', '请输入正则表达式!')
        return
    if e2.get() == '':                             # 若输入为空，提示输入
        tkinter.messagebox.showwarning('', '请输入待分析的串!')
        return
    flag = retominiDFA.analystr(s)
    if flag:
        label3['background'] = 'green'
        aresult.set('接受')
    else:
        label3['background'] = 'red'
        aresult.set('不接受')


# 显示NFA的按钮的回调函数
def btNFA():
    if e1.get() == '':
        return
    mtext.delete(1.0, END)
    mtext.insert(1.0, 'NFA:\n')
    mtext.image_create(END, image=picNFA)


# 显示DFA的按钮的回调函数
def btDFA():
    if e1.get() == '':
        return
    mtext.delete(1.0, END)
    mtext.insert(1.0, 'DFA:\n')
    mtext.image_create(END, image=picDFA)


# 显示miniDFA的按钮的回调函数
def btMiniDFA():
    if e1.get() == '':
        return
    mtext.delete(1.0, END)
    mtext.insert(1.0, 'miniDFA:\n')
    mtext.image_create(END, image=picMiniDFA)


if __name__ == '__main__':
    for i in range(10):                                                                     # 填充第0行
        Label(window, width=20).grid(row=0, column=i)

    label1 = Label(window, text='请输入正则表达式', font=('KaiTi', 11), width=18)           # 输入正则表达式
    label1.grid(row=1, column=0, sticky=W)
    btn1 = Button(window, text='确认', font=('KaiTi', 11), width=4, command=clkbtn1)
    btn1.grid(row=1, column=2, sticky=W)

    label2 = Label(window, text='请输入待分析的串', font=('KaiTi', 11), width=18)           # 输出待分析的串
    label2.grid(row=2, column=0, sticky=W)

    btn2 = Button(window, text='确认', font=('KaiTi', 11), width=4, command=clkbtn2)
    btn2.grid(row=2, column=2, sticky=W)

    btnNFA = Button(window, text='NFA', font=('KaiTi', 11), width=18, command=btNFA)                # 显示NFA的按钮
    btnNFA.grid(row=3, column=0)

    btnDFA = Button(window, text='DFA', font=('KaiTi', 11), width=18, command=btDFA)                # 显示DFA的按钮
    btnDFA.grid(row=3, column=1)

    btnmDFA = Button(window, text='miniDFA', font=('KaiTi', 11), width=18, command=btMiniDFA)          # 显示mDFA的按钮
    btnmDFA.grid(row=3, column=2)

    window.mainloop()

from easy.ast import Expression
from easy.visitors.base import BaseVisitor

class RegisterStack(object):
    def __init__(self):
        self.all_regs = ['%eax', '%ebx', '%ecx', '%edx', '%esi', '%edi']
        self.free_regs = self.all_regs[:]
        self.caller_save = ['%eax', '%ecx', '%edx']
        self.stack = []

    def pop(self):
        reg = self.stack.pop()
        if reg in self.all_regs:
            self.free_regs.append(reg)
        return reg

    def push(self):
        reg = self.free_regs.pop()
        self.stack.append(reg)
        return reg

class CodeGenVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(CodeGenVisitor, self).__init__(*args, **kwargs)
        self.output = ''
        self.reg_stack = RegisterStack()
        self._string_literals = {}

    def _get_string_location(self, string):
        if string in self._string_literals:
            return self._string_literals[string]
        self._string_literals[string] = 'LC%d' % len(self._string_literals)
        return self._string_literals[string]

    def _omit_rodata(self):
        self.omit('.section .rodata')

        for string, label in self._string_literals.iteritems():
            self.omit('.%s:' % label)
            self.omit('.string "%s"' % string)

    def _omit_header(self):
        self.omit('.text')
        self.omit('.globl main')

        self.omit('main:')
        self.omit('pushl %ebp')
        self.omit('movl %esp, %ebp')
        self.omit('')

    def _omit_footer(self):
        self.omit('')
        self.omit('leave')
        self.omit('ret')
        self.omit('')

    def omit(self, str):
        if str and str[-1] != ':' and sum(1 for x in ('.globl',) if str.startswith(x)) == 0:
            str = '\t' + str
        self.output += str + '\n'

    def visitStringExpr(self, node):
        label = self._get_string_location(node.string)
        #reg = self.reg_stack.push()
        #self.omit('movl $.%s, %s' % (label, reg))
        self.reg_stack.stack.append('$.%s' % label)

    def visitFuncCallExpr(self, node):
        regs_before = [x for x in self.reg_stack.stack if x.startswith('%')]
        for arg in regs_before:
            self.omit('pushl %s' % arg)

        self._visit_list(node.args)

        for arg in node.args:
            loc = self.reg_stack.pop()
            self.omit('pushl %s' % loc)

        self.omit('call %s' % node.func_name)
        self.omit('addl $%d, %%esp' % (len(node.args) * 4))

        dst = self.reg_stack.push()
        if dst != '%eax':
            self.omit('movl %%eax, %s' % dst)

        for arg in reversed(regs_before):
            self.omit('popl %s' % arg)

    def visitExprStatement(self, node):
        self.visit(node.expr)
        self.reg_stack.pop()

    def visitBlockStatement(self, node):
        self._omit_header()

        self._visit_list(node.block)

        self._omit_footer()
        self._omit_rodata()

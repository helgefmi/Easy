from easy.ast import Expression
from easy.visitors.base import BaseVisitor

class RegisterStack(object):
    def __init__(self):
        self._all_regs = ['%eax', '%ebx', '%ecx', '%edx', '%esi', '%edi']
        self._free_regs = self._all_regs[:]
        self._caller_save = ['%eax', '%ecx', '%edx']
        self._stack = []

    def pop(self):
        reg = self._stack.pop()
        if reg in self._all_regs:
            self._free_regs.append(reg)
        return reg

    def push(self, item=None):
        if item is not None:
            self._stack.append(item)
        else:
            reg = self._free_regs.pop()
            self._stack.append(reg)
        return self._stack[-1]

    def save_caller_regs(self, codegen):
        regs = [reg for reg in self._caller_save if reg not in self._free_regs]
        for reg in regs:
            codegen.omit('pushl %s' % reg)
        return regs

    def pop_regs(self, codegen, regs):
        for reg in regs:
            codegen.omit('popl %s' % reg)

class CodeGenVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(CodeGenVisitor, self).__init__(*args, **kwargs)
        self.output = ''
        self.reg_stack = RegisterStack()
        self._string_labels = {}

    def _get_string_label(self, string):
        if string in self._string_labels:
            return self._string_labels[string]
        self._string_labels[string] = 'LC%d' % len(self._string_labels)
        return self._string_labels[string]

    def _omit_rodata(self):
        self.omit('.section .rodata')

        for string, label in self._string_labels.iteritems():
            self.omit('.%s:' % label)
            self.omit('.string "%s"' % string)

    def _omit_header(self):
        self.omit((
            '.text',
            '.globl main',
            'main:',
            'pushl %ebp',
            'movl %esp, %ebp',
            '',
        ))

    def _omit_footer(self):
        self.omit('')
        self.omit('leave')
        self.omit('ret')
        self.omit('')

    def omit(self, line):
        if not isinstance(line, str):
            for l in line:
                self.omit(l)
            return

        if line and line[-1] != ':' and sum(1 for x in ('.globl',) if line.startswith(x)) == 0:
            line = '\t' + line
        self.output += line + '\n'

    def visitNumberExpr(self, node):
        self.reg_stack.push('$%d' % node.number)

    def visitStringExpr(self, node):
        label = self._get_string_label(node.string)
        #reg = self.reg_stack.push()
        #self.omit('movl $.%s, %s' % (label, reg))
        self.reg_stack.push('$.%s' % label)

    def visitFuncCallExpr(self, node):
        regs_saved = self.reg_stack.save_caller_regs(self)

        self._visit_list(node.args)

        for arg in node.args:
            loc = self.reg_stack.pop()
            self.omit('pushl %s' % loc)

        self.omit('call %s' % node.func_name)
        self.omit('addl $%d, %%esp' % (len(node.args) * 4))

        dst = self.reg_stack.push()
        if dst != '%eax':
            self.omit('movl %%eax, %s' % dst)

        self.reg_stack.pop_regs(self, regs_saved)

    def visitExprStatement(self, node):
        self.visit(node.expr)
        self.reg_stack.pop()

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitTopLevel(self, node):
        self._omit_header()
        self.visit(node.block)
        self._omit_footer()
        self._omit_rodata()

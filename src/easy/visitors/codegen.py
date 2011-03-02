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
        if item is None:
            item = self._free_regs.pop()
        self._stack.append(item)
        return item

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
        self.regs = RegisterStack()
        self._string_labels = {}
        self._label_no = 0

    def _get_string_label(self, string):
        if string in self._string_labels:
            return self._string_labels[string]
        self._string_labels[string] = 'LC%d' % len(self._string_labels)
        return self._string_labels[string]

    def _get_label(self):
        self._label_no += 1
        return 'L%d' % self._label_no

    def _omit_rodata(self):
        self.omit('.section .rodata')

        for string, label in self._string_labels.iteritems():
            self.omit('.%s:\t.string "%s"' % (label, string))

    def omit(self, line):
        if line and line[-1] != ':' and sum(1 for x in ('.globl',) if line.startswith(x)) == 0:
            line = '\t' + line
        self.output += line + '\n'

    def visitNumberExpr(self, node):
        self.regs.push('$%d' % node.number)

    def visitStringExpr(self, node):
        label = self._get_string_label(node.string)
        #reg = self.regs.push()
        #self.omit('movl $.%s, %s' % (label, reg))
        self.regs.push('$.%s' % label)

    def visitFuncCallExpr(self, node):
        regs_saved = self.regs.save_caller_regs(self)

        self._visit_list(node.args)

        for arg in node.args:
            loc = self.regs.pop()
            self.omit('pushl %s' % loc)

        self.omit('call %s' % node.func_name)
        if node.args:
            self.omit('addl $%d, %%esp' % (len(node.args) * 4))

        dst = self.regs.push()
        if dst != '%eax':
            self.omit('movl %%eax, %s' % dst)

        self.regs.pop_regs(self, regs_saved)

    def visitExprStatement(self, node):
        self.visit(node.expr)
        self.regs.pop()

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        self.omit('.globl %s' % node.func_name)
        self.omit('%s:' % node.func_name)
        self.omit('pushl %ebp')
        self.omit('movl %esp, %ebp')

        self.visit(node.block)

        self.omit('leave')
        self.omit('ret')

    def visitIfStatement(self, node):
        L1, L2 = [self._get_label() for _ in range(2)]
        self.visit(node.cond)
        reg = self.regs.pop()
        # TODO: This is obviously not neccessary
        if not reg.startswith('%'):
            old, reg = reg, self.regs.push()
            self.omit('movl %s, %s' % (old, reg))
        self.omit('test %s, %s' % (reg, reg))
        self.omit('jz .%s' % L1)
        self.visit(node.true_block)
        self.omit('jmp .%s' % L2)
        self.omit('.%s:' % L1)
        if node.false_block:
            self.visit(node.false_block)
        self.omit('.%s:' % L2)

    def visitTopLevel(self, node):
        self.omit('.text')
        self._visit_list(node.block)
        self._omit_rodata()

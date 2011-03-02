from easy.ast import Expression
from easy.visitors.base import BaseVisitor

class RegisterStack(object):
    def __init__(self):
        self._all_regs = ['%eax', '%ebx', '%ecx', '%edx', '%esi', '%edi']
        self._free_regs = self._all_regs[:]
        self._caller_save = ['%eax', '%ecx', '%edx']
        self._callee_save = ['%ebx', '%esi', '%edi'] # ebp gets pushed manually
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
        self.omit_regs(codegen, regs, 'pushl')
        return regs

    def save_callee_regs(self, codegen):
        regs = [reg for reg in self._callee_save if reg not in self._free_regs]
        self.omit_regs(codegen, regs, 'pushl')
        return regs

    def omit_regs(self, codegen, regs, instruction):
        for reg in regs:
            codegen.omit('%s %s' % (instruction, reg))

class CodeGenVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(CodeGenVisitor, self).__init__(*args, **kwargs)
        self._regs = RegisterStack()
        self._output = ''
        self._string_labels = {}
        self._label_no = 0

    def _get_string_label(self, string):
        if string in self._string_labels:
            return self._string_labels[string]
        self._string_labels[string] = 'LC%d' % len(self._string_labels)
        return self._string_labels[string]

    def _get_unique_label(self):
        self._label_no += 1
        return 'L%d' % self._label_no

    def _omit_rodata(self):
        self.omit('.section .rodata')
        for string, label in self._string_labels.iteritems():
            self.omit('.%s:\t.string "%s"' % (label, string))

    def omit(self, line):
        if not (line.startswith('.') or line.endswith(':')):
            line = '\t' + line
        self._output += line + '\n'

    def visitNumberExpr(self, node):
        self._regs.push('$%d' % node.number)

    def visitStringExpr(self, node):
        label = self._get_string_label(node.string)
        self._regs.push('$.%s' % label)

    def visitFuncCallExpr(self, node):
        regs_saved = self._regs.save_caller_regs(self)

        self._visit_list(node.args)

        for _ in node.args:
            loc = self._regs.pop()
            self.omit('pushl %s' % loc)

        self.omit('call %s' % node.func_name)
        if node.args:
            self.omit('addl $%d, %%esp' % (len(node.args) * 4))

        dst = self._regs.push()
        if dst != '%eax':
            self.omit('movl %%eax, %s' % dst)

        self._regs.omit_regs(self, regs_saved, 'popl')

    def visitExprStatement(self, node):
        self.visit(node.expr)
        self._regs.pop()

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        self.omit('.globl %s' % node.func_name)
        self.omit('%s:' % node.func_name)
        self.omit('pushl %ebp')
        self.omit('movl %esp, %ebp')

        regs_saved = self._regs.save_callee_regs(self)
        self.visit(node.block)
        self._regs.omit_regs(self, regs_saved, 'popl')

        self.omit('leave')
        self.omit('ret')

    def visitIfStatement(self, node):
        L1, L2 = self._get_unique_label(), self._get_unique_label()

        self.visit(node.cond)
        reg = self._regs.pop()

        # TODO: This is obviously not neccessary
        if not reg.startswith('%'):
            old, reg = reg, self._regs.push()
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

        return self._output

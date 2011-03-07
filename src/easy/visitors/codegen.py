from easy.ast import Expression
from easy.visitors.base import BaseVisitor

class RegisterStack(object):
    def __init__(self):
        self._all_regs = ('%eax', '%ebx', '%ecx', '%edx', '%esi', '%edi')
        self._free_regs = list(self._all_regs)
        self._caller_save = ('%eax', '%ecx', '%edx')
        self._callee_save = ('%ebx', '%esi', '%edi') # ebp gets pushed manually
        self._byte_regs = ('%eax', '%ebx', '%ecx', '%edx')
        self._stack = []

    def pop(self):
        reg = self._stack.pop()
        if reg in self._all_regs:
            self._free_regs.append(reg)
        return reg

    def push_bytereg(self):
        return self.push(self._byte_regs)

    def push_constant(self, constant):
        assert constant.startswith('$')
        self._stack.append(constant)

    def push_loc(self, loc):
        self._stack.append(loc)

    def push(self, possible_regs=None):
        possible_regs = possible_regs or self._free_regs
        assert len(list(possible_regs)) == \
               sum(1 for x in possible_regs if x.startswith('%'))
        reg = (reg for reg in self._free_regs if reg in possible_regs).next()
        assert self._free_regs.count(reg) == 1
        assert self._stack.count(reg) == 0
        self._free_regs.remove(reg)
        self._stack.append(reg)
        return reg

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
        self._binary_op_instructions = {
            '*': 'imul',
            '-': 'subl',
            '+': 'addl',
            '>': 'setg',
            '<': 'setl',
            '<=': 'setle',
            '>=': 'setge',
            '==': 'sete',
            '!=': 'setne',
        }
        self._arithmetic_instructions = ('imul', 'subl', 'idiv', 'addl',)
        self._compare_instructions = ('setg', 'setl', 'setle', 'setge', 'sete', 'setne')

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

        spaces = 60 - len(line)
        line += (' ' * spaces) + '# free_regs=%s' % self._regs._free_regs

        self._output += line + '\n'

    def visitNumberExpr(self, node):
        self._regs.push_constant('$%d' % node.number)

    def visitStringExpr(self, node):
        label = self._get_string_label(node.string)
        self._regs.push_constant('$.%s' % label)

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

        self.omit('testl %s, %s' % (reg, reg))
        self.omit('jz .%s' % L1)
        self.visit(node.true_block)
        self.omit('jmp .%s' % L2)

        self.omit('.%s:' % L1)
        if node.false_block:
            self.visit(node.false_block)

        self.omit('.%s:' % L2)

    def visitBinaryOpExpr(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)
        rreg = self._regs.pop()
        lreg = self._regs.pop()

        instruction = self._binary_op_instructions[node.operator]
        if instruction in self._arithmetic_instructions:
            self.omit('%s %s, %s' % (instruction, rreg, lreg))
            self._regs.push([lreg])
        elif instruction in self._compare_instructions:
            self.omit('cmpl %s, %s' % (rreg, lreg))
            reg = self._regs.push_bytereg()
            loreg = '%' + reg[2] + 'l'

            self.omit('%s %s' % (instruction, loreg))
            self.omit('movzbl %s, %s' % (loreg, reg))
        else:
            assert False

    def visitTopLevel(self, node):
        self.omit('.text')
        self._visit_list(node.block)
        self._omit_rodata()

        return self._output

    def visitIdExpr(self, node):
        loc = '%d(%%ebp)' % (8 + (node.var_idx * 4))
        self.omit('movl %s, %s' % (loc, self._regs.push()))

from binaryninja.function import InstructionTextToken
from binaryninja.enums import InstructionTextTokenType, BranchType
from struct import unpack



class Disassembler(object):
    """ CHIP-8 tokanized Disassembler """
    def __init__(self):
        self.opcodes = {
            0x0: "_rcs",
            0x1: "_jp",
            0x2: "_call",
            0x3: "_se_kk",
            0x4: "_sne_kk",
            0x5: "_se",
            0x6: "_ld_kk",
            0x7: "_add",
            0x8: "_bitops",
            0x9: "_sne",
            0xa: "_ld_i",
            0xb: "_jp_v0",
            0xc: "_rnd",
            0xd: "_draw",
            0xe: "_skip",
            0xf: "_ld",
        }
        self.V = {
            0x0: 'V0',
            0x1: 'V1',
            0x2: 'V2',
            0x3: 'V3',
            0x4: 'V4',
            0x5: 'V5',
            0x6: 'V6',
            0x7: 'V7',
            0x8: 'V8',
            0x9: 'V9',
            0xa: 'Va',
            0xb: 'Vb',
            0xc: 'Vc',
            0xd: 'Vd',
            0xe: 'Ve',
            0xf: 'Vf',
        }


    def disasm(self, opcode, addr):
        """ Return disassembled tokanized instruction """
        if not opcode:
            return None
        opd = self._u16(opcode)
        n = opd >> 12
        handler = getattr(self, self.opcodes[n])
        return handler(opd)

    def get_branch_info(self, opcode):
        vars = self._vars(opcode)
        m, kk = vars['m'], vars['kk']
        if m == 0x0:
            if kk == 0xEE:
                return BranchType.FunctionReturn
            if kk != 0xE0:
                return BranchType.UnconditionalBranch
        if m == 0xE:
            if kk == 0x9E:
                return BranchType.TrueBranch
            if kk == 0xA1:
                return BranchType.FalseBranch
        mnem = {
            0x1: BranchType.UnconditionalBranch,
            0x2: BranchType.CallDestination,
            0x3: BranchType.TrueBranch,
            0x4: BranchType.FalseBranch,
            0x5: BranchType.TrueBranch,
            0xB: BranchType.IndirectBranch,
        }
        return mnem.get(m, None)


    def _vars(self, opd):
        """ Separates the different bits from opcode """
        if isinstance(opd, bytes):
            opd = self._u16(opd)
        addr = opd & 0xfff
        m = opd >> 12
        n = opd & 0xf
        x = (opd >> 8) & 0xf
        y = (opd >> 4) & 0xf
        kk = opd & 0xff
        return {
            'm': m,
            'addr': addr,
            'n': n,
            'x': x,
            'y': y,
            'kk': kk
        }

    def _u16(self, opcode):
        """ bytes to int """
        if len(opcode) == 1:
            return unpack('>B', opcode)[0]
        return unpack('>H', opcode)[0]

    def _rcs(self, opcode):
        if opcode == 0x00EE:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'RET')]
        if opcode == 0x00E0:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'CLS')]
        addr = opcode & 0xfff
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SYS'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(addr), addr)]

    def _jp(self, opcode):
        addr = opcode & 0xfff
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'JP'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(addr), addr)]

    def _call(self, opcode):
        addr = opcode & 0xfff
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'CALL'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(addr), addr)]

    def _se_kk(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SE'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(kk), kk)]

    def _sne_kk(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SNE'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(kk), kk)]

    def _se(self, opcode):
        vars = self._vars(opcode)
        x, y = vars['x'], vars['y']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SE'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]

    def _ld_kk(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(kk), kk)]

    def _add(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'ADD'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(kk), kk)]

    def _bitops(self, opcode):
        vars = self._vars(opcode)
        x, y, n = vars['x'], vars['y'], vars['n']
        if n == 0x0:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0x1:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'OR'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0x2:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'AND'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0x3:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'XOR'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0x4:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'ADD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0x5:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SUB'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0x6:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SHR'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(1), 1)]
        elif n == 0x7:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SUBN'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]
        elif n == 0xE:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SHL'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(1), 1)]

    def _sne(self, opcode):
        vars = self._vars(opcode)
        x, y = vars['x'], vars['y']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SNE'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y])]

    def _ld_i(self, opcode):
        addr = opcode & 0xfff
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, 'I'),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(addr), addr)]
    
    def _jp_v0(self, opcode):
        addr = opcode & 0xfff
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'JP'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, 'V0'),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(addr), addr)]

    def _rnd(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'RND'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(kk), kk)]

    def _draw(self, opcode):
        vars = self._vars(opcode)
        x, y, n = vars['x'], vars['y'], vars['n']
        return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'DRW'),
        InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[y]),
        InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
        InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(n), n)]
    
    def _skip(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        if kk == 0x9E:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SKP'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        if kk == 0xA1:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'SKNP'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]

    def _ld(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        if kk == 0x07:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'DT')]
        elif kk == 0x0A:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'K')]
        elif kk == 0x15:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'DT'),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        elif kk == 0x18:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'ST'),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        elif kk == 0x1e:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'ADD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'I'),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        elif kk == 0x29:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'F'),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        elif kk == 0x33:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'B'),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        elif kk == 0x55:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' ['),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'I'),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, '], '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x])]
        elif kk == 0x65:
            return [InstructionTextToken(InstructionTextTokenType.InstructionToken, 'LD'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, self.V[x]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', ['),
            InstructionTextToken(InstructionTextTokenType.RegisterToken, 'I'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ']')]


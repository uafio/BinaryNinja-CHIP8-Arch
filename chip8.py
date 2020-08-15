"""
TODO: Need docstrings
"""

from binaryninja.log import log_info
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import Endianness, InstructionTextTokenType, BranchType
from struct import unpack
from enum import Enum



class CHIP8(Architecture):
    name = 'CHIP-8'
    endianness = Endianness.BigEndian
    address_size = 2
    default_int_size = 2
    instr_alignment = 2
    max_instr_length = 2
    opcode_display_length = 2
    regs = {
        'PC': RegisterInfo('PC', 2),
        'SP': RegisterInfo('SP', 1),
        'I': RegisterInfo('I', 2),

        'DT': RegisterInfo('DT', 1),
        'ST': RegisterInfo('ST', 1),

        'V0': RegisterInfo('V0', 1),
        'V1': RegisterInfo('V1', 1),
        'V2': RegisterInfo('V2', 1),
        'V3': RegisterInfo('V3', 1),
        'V4': RegisterInfo('V4', 1),
        'V5': RegisterInfo('V5', 1),
        'V6': RegisterInfo('V6', 1),
        'V7': RegisterInfo('V7', 1),
        'V8': RegisterInfo('V8', 1),
        'V9': RegisterInfo('V9', 1),
        'Va': RegisterInfo('Va', 1),
        'Vb': RegisterInfo('Vb', 1),
        'Vc': RegisterInfo('Vc', 1),
        'Vd': RegisterInfo('Vd', 1),
        'Ve': RegisterInfo('Ve', 1),
        'Vf': RegisterInfo('Vf', 1)
    }
    stack_pointer = 'SP'

    def __init__(self):
        super().__init__()
        self.dis = Disassembler()

    def get_instruction_info(self, data, addr):
        if len(data) > 2:
            data = data[:2]
        result = InstructionInfo()
        result.length = 2
        vars = self.dis._vars(data)
        baddr = vars['addr']
        binfo = self.dis.get_branch_info(data)
        if binfo == BranchType.UnconditionalBranch or binfo == BranchType.CallDestination:
            result.add_branch(binfo, baddr)
        elif binfo == BranchType.FunctionReturn or binfo == BranchType.IndirectBranch:
            result.add_branch(binfo)
        elif binfo == BranchType.TrueBranch:
            result.add_branch(BranchType.TrueBranch, addr + 4)
            result.add_branch(BranchType.FalseBranch, addr + 2)
        elif binfo == BranchType.FalseBranch:
            result.add_branch(BranchType.TrueBranch, addr + 4)
            result.add_branch(BranchType.FalseBranch, addr + 2)
        return result
    
    def get_instruction_text(self, data, addr):
        if len(data) > 2:
            data = data[:2]
        tokens = self.dis.disasm(data, addr)
        if not tokens:
            tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, '_emit'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' '),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(data[0]), data[0]),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ', '),
            InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(data[1]), data[1])]
        return tokens, 2

    def get_instruction_low_level_il(self, data, addr, il):
        return None



class Disassembler(object):
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






CHIP8.register()
log_info('registered CHIP-8 Architecture')

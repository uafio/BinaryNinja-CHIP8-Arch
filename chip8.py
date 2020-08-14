"""
TODO: Need docstrings
"""

from binaryninja.log import log_info
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import Endianness, InstructionTextTokenType
from struct import unpack


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

    def _vars(self, opd):
        if isinstance(opd, bytes):
            opd = self._u16(opd)
        addr = opd & 0xfff
        n = opd & 0xf
        x = (opd >> 8) & 0xf
        y = (opd >> 4) & 0xf
        kk = opd & 0xff
        return {
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
            return "RET"
        if opcode == 0x00E0:
            return "CLS"
        addr = opcode & 0xfff
        return "SYS {:#x}".format(addr)

    def _jp(self, opcode):
        addr = opcode & 0xfff
        return "JP {:#x}".format(addr)

    def _call(self, opcode):
        addr = opcode & 0xfff
        return "CALL {:#x}".format(addr)

    def _se_kk(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return "SE {}, {:#x}".format(self.V[x], kk)

    def _sne_kk(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return "SNE {}, {:#x}".format(self.V[x], kk)

    def _se(self, opcode):
        vars = self._vars(opcode)
        x, y = vars['x'], vars['y']
        return "SE {}, {}".format(self.V[x], self.V[y])

    def _ld_kk(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return "LD {}, {:#x}".format(self.V[x], kk)

    def _add(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return "ADD {}, {:#x}".format(self.V[x], kk)

    def _bitops(self, opcode):
        vars = self._vars(opcode)
        x, y, n = vars['x'], vars['y'], vars['n']
        mnem = {
            0x0: "LD {}, {}",
            0x1: "OR {}, {}",
            0x2: "AND {}, {}",
            0x3: "XOR {}, {}",
            0x4: "ADD {}, {}",
            0x5: "SUB {}, {}",
            0x6: "SHR {}, 1",
            0x7: "SUBN {}, {}",
            0xE: "SHL {}, 1"
        }
        return mnem.get(n, '').format(self.V[x], self.V[y])

    def _sne(self, opcode):
        vars = self._vars(opcode)
        x, y = vars['x'], vars['y']
        return "SNE {}, {}".format(self.V[x], self.V[y])

    def _ld_i(self, opcode):
        addr = opcode & 0xfff
        return "LD I, {:#x}".format(addr)
    
    def _jp_v0(self, opcode):
        addr = opcode & 0xfff
        return "JP V0, {:#x}".format(addr)

    def _rnd(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return "RND {}, {:#x}".format(self.V[x], kk)

    def _draw(self, opcode):
        vars = self._vars(opcode)
        x, y, n = vars['x'], vars['y'], vars['n']
        return "DRW {}, {}, {:#x}".format(self.V[x], self.V[y], n)
    
    def _skip(self, opcode):
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        if kk == 0x9E:
            return "SKP {}".format(self.V[x])
        if kk == 0xA1:
            return "SKNP {}".format(self.V[x])
        return ''

    def _ld(self, opcode):
        subs = {
            0x07: "LD {}, DT",
            0x0A: "LD {}, K",
            0x15: "LD DT, {}",
            0x18: "LD ST, {}",
            0x1e: "ADD I, {}",
            0x29: "LD F, {}",
            0x33: "LD B, {}",
            0x55: "LD [I], {}",
            0x65: "LD {}, [I]"
        }
        vars = self._vars(opcode)
        x, kk = vars['x'], vars['kk']
        return subs.get(kk, '').format(self.V[x])





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
        result = InstructionInfo()
        result.length = 2
        return result
    
    def get_instruction_text(self, data, addr):
        instruction = self.dis.disasm(data, addr)
        if not instruction:
            instruction = "_emit {:#x} {:#x}".format(data[0], data[1])
            tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, "_emit"),
            InstructionTextToken(InstructionTextTokenType.HexDumpByteValueToken, hex(data[0])),
            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, " "),
            InstructionTextToken(InstructionTextTokenType.HexDumpByteValueToken, hex(data[1]))]
            return tokens, 2
        tokens = [InstructionTextToken(InstructionTextTokenType.TextToken, instruction)]
        return tokens, 2

    def get_instruction_low_level_il(self, data, addr, il):
        return None





CHIP8.register()
log_info('registered CHIP-8 Architecture')

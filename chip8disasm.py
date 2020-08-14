
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




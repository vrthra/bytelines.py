import dis, marshal, types, sys, types, struct, time
# from https://nedbatchelder.com/blog/200804/wicked_hack_python_bytecode_tracing.html
# modified for python3.6

class PycFile:
    def read(self, fn):
        f = open(fn, "rb")
        self.magic = f.read(4)
        self.moddate = f.read(4)
        self.filesz = f.read(4)
        self.code = marshal.load(f)
    
    def write(self, f):
        if isinstance(f, str):
            f = open(f, "wb")
        f.write(self.magic)
        f.write(self.moddate)
        f.write(self.filesz)
        marshal.dump(self.code, f)

    def hack_line_numbers(self):
        self.code = hack_line_numbers(self.code)
        
def hack_line_numbers(code):
    """ Replace a code object's line number information to claim that every
        byte of the bytecode is a new line.  Returns a new code object.
        Also recurses to hack the line numbers in nested code objects.
    """
    show_code(code)
    n_bytes = len(code.co_code)
    new_lnotab = bytearray([1, 1] * (n_bytes-1))
    new_consts = []
    for const in code.co_consts:
        if type(const) == types.CodeType:
            new_consts.append(hack_line_numbers(const))
        else:
            new_consts.append(const)

    new_code = types.CodeType(code.co_argcount, code.co_kwonlyargcount,
        code.co_nlocals, code.co_stacksize, code.co_flags,
        code.co_code, tuple(new_consts), code.co_names,
        code.co_varnames, code.co_filename,
        code.co_name,
        0, bytes(new_lnotab), code.co_freevars,
        code.co_cellvars)
    show_hex("new lnotab", bytes(new_lnotab), indent='')

    return new_code

def show_code(code, indent=''):
    print("%scode" % indent)
    indent += '   '
    print("%sargcount %d" % (indent, code.co_argcount))
    print("%snlocals %d" % (indent, code.co_nlocals))
    print("%sstacksize %d" % (indent, code.co_stacksize))
    print("%sflags %04x" % (indent, code.co_flags))
    show_hex("code", code.co_code, indent=indent)
    dis.disassemble(code)
    print("%sconsts" % indent)
    for const in code.co_consts:
        if type(const) == types.CodeType:
            show_code(const, indent+'   ')
        else:
            print("   %s%r" % (indent, const))
    print("%snames %r" % (indent, code.co_names))
    print("%svarnames %r" % (indent, code.co_varnames))
    print("%sfreevars %r" % (indent, code.co_freevars))
    print("%scellvars %r" % (indent, code.co_cellvars))
    print("%sfilename %r" % (indent, code.co_filename))
    print("%sname %r" % (indent, code.co_name))
    print("%sfirstlineno %d" % (indent, code.co_firstlineno))
    n_bytes = len(code.co_code)
    lb_ranges = [code.co_lnotab[b*2] for b in range(len(code.co_lnotab)//2) ]
    lb_ranges += [ n_bytes - sum(lb_ranges) ]
    show_hex("lnotab", code.co_lnotab, indent=indent)
    
def show_hex(label, h, indent):
    #h = h.encode('hex')
    if len(h) < 60:
        print("%s%s %s" % (indent, label, h))
    else:
        print("%s%s" % (indent, label))
        for i in range(0, len(h), 60):
            print("%s   %s" % (indent, h[i:i+60]))
def hack_file(f, w):
    pyc = PycFile()
    pyc.read(f)
    pyc.hack_line_numbers()
    if w: pyc.write(f)

hack_file(sys.argv[1], True)


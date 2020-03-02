import dis
import inspect


def get_generated_network_code(fn):
    fn_args = ", ".join([a.name for a in fn.arguments])
    fn_header = f"def {fn.fn.__name__}({fn_args}):"
    arg_dict_str = ", ".join([f"'{a.name}': {a.name}" for a in fn.arguments])
    arg_dict_str = f"args = {{{arg_dict_str}, 'raw': True}}"

    return (
        f"import json\n"
        f"import urllib.request\n"
        f"{fn_header}\n"
        f"    {arg_dict_str}\n"
        f"    encoded = json.dumps(args).encode('utf-8')\n"
        f"    headers = {{'content-type': 'application/json'}}\n"
        f"    url = 'https://tervay.com/share/{fn.url}_json/'\n"
        f"    r = urllib.request.Request(url, data=encoded, headers=headers)\n"
        f"    result = json.loads(urllib.request.urlopen(r).read().decode('utf-8'))\n"
        f"    return result['result']"
    )


def get_generated_code(fn):
    code = dis._get_code_object(fn)
    for name in code.co_names:
        if is_module(name):
            print(f"Found module -- {name}")
        else:
            print(f"Found non-module -- {name}")

    source_code = f"""
{dis.code_info(fn)}
{inspect.getsource(fn)}
"""

    return source_code


def is_module(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def list_func_calls(fn):
    funcs = []
    bytecode = dis.Bytecode(fn)
    instrs = list(reversed([instr for instr in bytecode]))
    for (ix, instr) in enumerate(instrs):
        if instr.opname in ["CALL_FUNCTION", "CALL_FUNCTION_KW", "CALL_METHOD"]:
            load_func_instr = instrs[ix + instr.arg + 1]
            funcs.append(load_func_instr)

    return list(reversed(funcs))


def get_function_calls(func, built_ins=False):
    # the used instructions
    ins = list(dis.get_instructions(func))[::-1]

    # dict for function names (so they are unique)
    names = {}

    # go through call stack
    for i, inst in list(enumerate(ins))[::-1]:
        # find last CALL_FUNCTION
        if inst.opname[:13] == "CALL_FUNCTION":

            # function takes ins[i].arg number of arguments
            ep = i + inst.arg + (2 if inst.opname[13:16] == "_KW" else 1)

            # parse argument list (Python2)
            if inst.arg == 257:
                k = i + 1
                while k < len(ins) and ins[k].opname != "BUILD_LIST":
                    k += 1

                ep = k - 1

            # LOAD that loaded this function
            entry = ins[ep]

            # ignore list comprehensions / ...
            name = str(entry.argval)
            if (
                "." not in name
                and entry.opname == "LOAD_GLOBAL"
                and (built_ins or not hasattr("builtin", name))
            ):
                # save name of this function
                names[name] = True

            # reduce this CALL_FUNCTION and all its paramters to one entry
            ins = ins[:i] + [entry] + ins[ep + 1 :]

    return sorted(list(names.keys()))

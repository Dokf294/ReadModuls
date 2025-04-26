import re
from pprint import pprint
import importlib
import time
import tkinter
from tkinter import filedialog
import threading
import copy

"""Error"""
def format_error(error_type, error_cause, *possible_reasons):
    return f'Error type {error_type}, cause -> {error_cause}. Possible reasons -> {possible_reasons}'

"""Check format"""
def is_allowed_extension(file_name: str, allowed_extensions={'png', 'jpg', 'jpeg'}) -> bool:
    return file_name.lower().split('.')[-1] in allowed_extensions

PATTERN_DICT = {
    'GetStartParse': r'!PROGRAMM\[OUT=(\d+)\];(.*?)(?=!PROGRAMM\[OUT=(\d+)\];)',
    'GetVariables':   r"@([\w]+)\s*=\s*(['\"].+?['\"]|\S+);",
    'GetOperatorIf': r'if\s+(\w+):\s*\{(.*?)\};',
    'GetFunctions':   r'@(.*?);'
}

"""Find keys"""
def find_params(raw_value, context):
    if raw_value is not None and '[' in raw_value and ']' in raw_value:
        result = []
        start_idx, end_idx = raw_value.index('['), raw_value.index(']')
        if start_idx > end_idx:
            return []
        param_list = raw_value[start_idx+1:end_idx].split(',')
        for p in param_list:
            key_name = p.strip()
            if key_name in context.get('keys', {}):
                result.append(context['keys'][key_name])
        return result
    return []

"""Dynamic module import"""
def import_module_method(module_name, method_descriptor, context, element_id):
    try:
        if method_descriptor is None:
            method_name = None
        elif '[' not in method_descriptor:
            method_name = method_descriptor
        else:
            method_name = method_descriptor.split('[', 1)[0]
        module = importlib.import_module(module_name)
        if method_name is not None:
            method_name = (lambda s: re.sub(r'\d+', '', s) if re.sub(r'\d+', '', s) != s else s)(method_name)
            target = getattr(module, method_name, None)
        else:
            target = module
        params = find_params(method_descriptor, context)
        if callable(target):
            result = target(*params) if params else target()
        else:
            result = target
        if element_id is None:
            return result
        return result[element_id]
    except Exception:
        return None

"""Read File and write into dict"""
def parse_psp_fold_two(script_text: str):
    regex_start = re.compile(PATTERN_DICT['GetStartParse'], re.S)
    regex_vars = re.compile(PATTERN_DICT['GetVariables'])
    regex_if = re.compile(PATTERN_DICT['GetOperatorIf'], re.S)
    regex_funcs = re.compile(PATTERN_DICT['GetFunctions'])
    final_result, has_continue, cleaned_block, block_counter = {}, False, None, 0
    for start_flag, block_data, end_flag in regex_start.findall(script_text):
        if start_flag not in '0' and end_flag not in '1':
            return format_error('1', 'Block Error')
        parsed = {'keys': {}, 'functions': {}, 'ifs': {}}
        for method_name, inner in regex_if.findall(block_data):
            if import_module_method(method_name, None, [], None):
                if not isinstance(parsed['ifs'].get(method_name), set):
                    parsed['ifs'][method_name] = set()
                inner_calls = []
                for x in inner.split(';'):
                    x = x.strip()
                    if x and '@' in x:
                        inner_calls.append(x)
                for call in inner_calls:
                    parsed['ifs'][method_name].add(call.strip('@;/\n '))
                block_counter += 1
            else:
                matches = list(re.finditer(PATTERN_DICT['GetOperatorIf'], block_data, flags=re.S))
                if len(matches) >= block_counter:
                    m2 = matches[block_counter]
                    s, e = m2.span()
                    cleaned_block = block_data[:s] + block_data[e:]
                    block_counter += 1
        if cleaned_block is None:
            cleaned_block = block_data
        for var_group, val_group in regex_vars.findall(cleaned_block):
            var_list = [x.strip() for x in var_group.split(',')]
            val_list = [x.strip('"\' ' ) for x in val_group.split(',')]
            if len(val_list) == 1 and len(var_list) > 1:
                base_val = val_list[0]
                val_list = [base_val+'0'] + [f"{base_val}{i+1}" for i in range(len(var_list)-1)]
            elif len(val_list) > len(var_list):
                return
            for vn, vv in zip(var_list, val_list):
                if vv.isdigit():
                    vv = int(vv)
                parsed['keys'][vn] = vv
        cleaned_block = re.sub(PATTERN_DICT['GetOperatorIf'], '', cleaned_block, flags=re.S)
        for func_ref in regex_funcs.findall(cleaned_block):
            if '=' not in func_ref:
                parts = func_ref.strip('@\n ').split('.')
                if len(parts) == 1:
                    if 'FUNC' not in parsed['functions']:
                        parsed['functions']['FUNC'] = set()
                    parsed['functions']['FUNC'].add(parts[0])
                    continue
                parsed['functions'][parts[0]] = set()
                parsed['functions'][parts[0]].add(parts[-1])
        final_result = parsed
    return final_result

"""Find Function"""
def resolve_dot_method(text: str, context: dict, link: dict, key: str) -> None:
    if is_allowed_extension(text):
        return None
    parts = text.split('.', 1) if isinstance(text, str) else []
    idx = int(parts[-1][-1]) if parts and parts[-1][-1].isdigit() else None
    if len(parts) > 1:
        var = import_module_method(parts[0], parts[1], context, idx)
        if var is not None and not (link is None and key is None):
            link[key] = var
        return var
    elif len(parts) == 1:
        var = import_module_method(parts[0], None, context, idx)
        if var is not None:
            link[key] = var
        return var
    return None

"""Copy data in work area"""
def copy_dict_values(context: dict, key_area: str, source: dict) -> None:
    if isinstance(source, dict):
        for k, item in source.items():
            if k not in context[key_area]:
                context[key_area][k] = set()
            if isinstance(item, set):
                for i in item:
                    context[key_area][k].add(i)
                continue
            context[key_area][k] = item
    elif isinstance(source, set):
        if 'COMMAND' not in context[key_area]:
            context[key_area]['COMMAND'] = set()
        for i in source:
            context[key_area]['COMMAND'].add(i)

"""main Set"""
def apply_parameters(parsed_data):
    if not isinstance(parsed_data, dict):
        return format_error('2', 'dict is not detected')
    if not {'ifs', 'keys', 'functions'}.issubset(parsed_data):
        return format_error('3', 'dicts is not detected')
    for if_name, items in parsed_data['ifs'].items():
        copy_dict_values(parsed_data, 'functions', parsed_data['ifs'][if_name])
    for k, item in parsed_data['keys'].items():
        resolve_dot_method(item, parsed_data, parsed_data['keys'], k)
    (func := (lambda f, d: [
        f(f, v) if isinstance(v, dict) else
        [resolve_dot_method(i, parsed_data, None, None) for i in v] if isinstance(v, set) else
        resolve_dot_method(v, parsed_data, None, None) if isinstance(v, str) else None
        for k, v in d.items()
    ]))(func, parsed_data['functions'])
    pprint(parsed_data)

"""assembly"""
if __name__ == '__main__':
    filepath = filedialog.askopenfilename(
        title='Parse file',
        filetypes=[('txt files', '*.txt')]
    )
    if filepath:
        with open(filepath, 'r') as file:
            ThisFile = file.read()
            parse = parse_psp_fold_two(ThisFile)
            
            flow = threading.Thread(target=apply_parameters(parse)) 
            flow.start()





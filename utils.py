import ast

def close_parenthesis(code: str) -> str:
    """
    Try to repair "SyntaxError: '(' was never closed" in the given code.
    
    This can only handle relatively simple cases.
    """
    try: ast.parse(code)
    except SyntaxError as e:
        if "'(' was never closed" in e.msg:
            lineno, offset = e.lineno, e.offset
            code_lines = code.split("\n")

            candidate_fixes = []
            for k in range(lineno, len(code_lines)):
                potential_fix = "\n".join(code_lines[:k]) + ")\n" + "\n".join(code_lines[k:])
                candidate_fixes.append(potential_fix)
                try:
                    ast.parse(potential_fix)
                except SyntaxError as e:
                    if "'(' was never closed" in e.msg:
                        if lineno != e.lineno or offset != e.offset:
                            # another different parenthesis error
                            # try to fix recursively
                            candidate_fixes.append(close_parenthesis(potential_fix))

            # check the candidate fixes
            for fix in candidate_fixes:
                try:
                    ast.parse(fix)
                    return fix
                except SyntaxError:
                    continue
                
    return code # nothing to fix or failed to fix

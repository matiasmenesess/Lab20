import re
import ast
from typing import Dict, List, Tuple, Optional

class CodeOptimizer:
    def __init__(self):
        self.variables = {}
        self.constants = {}
        self.hoisted_declarations = []
        
    def parse_file(self, filename: str) -> str:
        try:
            with open(filename, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo {filename}")
            return ""
    
    def extract_assignments(self, code: str) -> Dict[str, str]:
        assignments = {}
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('var') and not '[' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value = parts[1].strip().rstrip(';')
                    assignments[var_name] = value
        
        return assignments
    
    def evaluate_expression(self, expr: str, variables: Dict[str, str]) -> Optional[int]:
        try:
            for var, val in variables.items():
                if var in expr:
                    expr = expr.replace(var, val)
            
            if re.match(r'^[\d\+\-\*/\(\)\s]+$', expr):
                return eval(expr)
            return None
        except:
            return None
    
    def constant_folding(self, code: str) -> str:
        lines = code.split('\n')
        assignments = self.extract_assignments(code)
        result_lines = []
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if '=' in line and not line.startswith('var') and not '[' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expression = parts[1].strip().rstrip(';')
                    
                    result = self.evaluate_expression(expression, assignments)
                    if result is not None:
                        new_line = f" {var_name} = {result};"
                        result_lines.append(new_line)
                        continue
            
            result_lines.append(original_line)
        
        return '\n'.join(result_lines)
    
    def code_hoisting(self, code: str) -> str:
        lines = code.split('\n')
        assignments = self.extract_assignments(code)
        result_lines = []
        hoisted_declarations = []
        hoisted_assignments = []
        hoisted_vars_used = []
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            if '[' in line and ']' in line:
                match = re.search(r'\[([^\]]+)\]', line)
                if match:
                    bracket_expr = match.group(1)
                    
                    result = self.evaluate_expression(bracket_expr, assignments)
                    if result is not None:
                        temp_var = 't'
                        temp_declaration = f" var int {temp_var};"
                        temp_assignment = f" {temp_var}={bracket_expr}"
                        
                        vars_in_expr = []
                        for var in assignments.keys():
                            if var in bracket_expr:
                                vars_in_expr.append(var)
                        
                        new_line = line.replace(f'[{bracket_expr}]', f'[{temp_var}]')
                        
                        if temp_declaration not in hoisted_declarations:
                            hoisted_declarations.append(temp_declaration)
                            hoisted_assignments.append(temp_assignment)
                            hoisted_vars_used.extend(vars_in_expr)
                        
                        result_lines.append(' ' + new_line)
                        continue
            
            result_lines.append(original_line)
        
        final_lines = []
        last_var_index = -1
        last_assignment_of_used_vars = -1
        
        for i, line in enumerate(result_lines):
            if line.strip().startswith('var int'):
                last_var_index = i
        
        for i, line in enumerate(result_lines):
            line_stripped = line.strip()
            if '=' in line_stripped and not line_stripped.startswith('var'):
                var_name = line_stripped.split('=')[0].strip()
                if var_name in hoisted_vars_used:
                    last_assignment_of_used_vars = max(last_assignment_of_used_vars, i)
        
        for i, line in enumerate(result_lines):
            final_lines.append(line)
            
            if i == last_var_index and hoisted_declarations:
                for declaration in hoisted_declarations:
                    final_lines.append(declaration)
            
            if i == last_assignment_of_used_vars and hoisted_assignments:
                for assignment in hoisted_assignments:
                    final_lines.append(assignment)
        
        return '\n'.join(final_lines)
    
    def optimize_code(self, input_file: str, output_file: str = None):
        code = self.parse_file(input_file)
        if not code:
            return
        
        print("Código original:")
        print(code)
        print("\n" + "="*50 + "\n")
        
        code_after_folding = self.constant_folding(code)
        print("Después del Constant Folding:")
        print(code_after_folding)
        print("\n" + "="*50 + "\n")
        
        optimized_code = self.code_hoisting(code_after_folding)
        print("Después del Code Hoisting:")
        print(optimized_code)
        
        if output_file:
            with open(output_file, 'w') as file:
                file.write(optimized_code)
            print(f"\nCódigo optimizado guardado en: {output_file}")
        
        return optimized_code

def create_input_file():
    input_code = """fun void main()
 var int a;
 var int x;
 var int y;
 var int z;
 x = 2;
 y=3;
 z=2;
 a = 5*3+2;
 while x<7 do
    a[y*z] = 1
 endwhile
 return(0)
endfun"""
    
    with open('input1.txt', 'w') as file:
        file.write(input_code)
    print("Archivo input1.txt creado con el código de ejemplo.")

if __name__ == "__main__":
    create_input_file()
    
    optimizer = CodeOptimizer()
    result = optimizer.optimize_code('input1.txt', 'output.txt')
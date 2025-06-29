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
        result_lines = []

        inside_loop = False
        loop_start_idx = None
        hoisted_lines = []

        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            stripped = line.strip()

            if stripped.startswith("while ") or stripped.startswith("for "):
                inside_loop = True
                loop_start_idx = i
                result_lines.append(line)
                i += 1
                continue

            if inside_loop and (stripped.startswith("endwhile") or stripped.startswith("endfor")):
                inside_loop = False

                if hoisted_lines:
                    result_lines = result_lines[:loop_start_idx] + hoisted_lines + result_lines[loop_start_idx:]
                    hoisted_lines = []
                    i += len(hoisted_lines)

                result_lines.append(line)
                i += 1
                continue

            if inside_loop and '=' in stripped and not stripped.startswith('var'):
                var_name = stripped.split('=')[0].strip()
                expr = '='.join(stripped.split('=')[1:]).strip().rstrip(';')

                val = self.evaluate_expression(expr, self.extract_assignments(code))
                if val is not None:
                    hoisted_lines.append(f" {var_name} = {val};")
                    i += 1
                    continue

            result_lines.append(line)
            i += 1

        return '\n'.join(result_lines)

    
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
    input_code = """fun int main()
 var int i, j, x, y, z, sum, temp;

 x = 10;
 y = 5;
 z = 3;
 sum = 0;
 i = 0;

 while i < 3 do
  temp = x * y + z;
  sum = sum + temp;
  i = i + 1
 endwhile;
 print(sum);
 return(0)
endfun"""
    
    with open('input1.txt', 'w') as file:
        file.write(input_code)
    print("Archivo input1.txt creado con el código de ejemplo.")

if __name__ == "__main__":
    create_input_file()
    
    optimizer = CodeOptimizer()
    result = optimizer.optimize_code('input1.txt', 'output.txt')

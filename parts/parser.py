import ply.yacc as yacc

from lex import tokens
import AST
import sys 

vars = {}

def p_instructions(p):
    ''' instructions : instruction
        | instructions instruction '''
    if (len(p) > 2):
        p[0] = AST.InstructionsNode(p[1].children + [p[2]])
    else:
        p[0] = AST.InstructionsNode(p[1])

def p_instruction(p):
    ''' instruction : VARIABLE '{' instructionbody '}' method '''
    p[0] = AST.InstructionNode([AST.TokenNode(p[1])]+[p[3]]+[p[5]])

def p_instructionbody(p):
    ''' instructionbody : ingredient
        | ingredient instructionbody '''
    if (len(p) > 2):
        p[0] = AST.InstructionBodyNode([p[1]] + p[2].children)
    else:
        p[0] = AST.InstructionBodyNode(p[1])

def p_instructionbody_variable(p):
    ''' instructionbody : TAB VARIABLE
        | TAB VARIABLE instructionbody '''
    if (len(p) > 3):
        p[0] = AST.InstructionBodyNode([AST.TokenNode(p[2])] + p[3].children)
    else:
        p[0] = AST.InstructionBodyNode(AST.TokenNode(p[2]))

def p_ingredient(p):
    ''' ingredient : TAB QUANTITY TEXT '''
    p[0] = AST.IngredientNode([AST.QuantityNode(AST.TokenNode(p[2]))] + [AST.TokenNode(p[3])])

def p_method(p):
    ''' method : TEXT '(' parameters ')' '''
    p[0] = AST.MethodNode([AST.TokenNode(p[1]),p[3]])

def p_parameter_text(p):
    ''' parameter : TEXT '=' TEXT '''
    p[0] = AST.MethodArgumentNode([AST.TokenNode(p[1]),AST.TokenNode(p[3])])

def p_parameter_qty(p):
    ''' parameter : TEXT '=' QUANTITY '''
    p[0] = AST.MethodArgumentNode([AST.TokenNode(p[1]),AST.TokenNode(p[3])])

def p_parameters(p):
    ''' parameters : parameter ',' parameters
        | parameter
        |   '''
    if (len(p) > 3):
        p[0] = AST.MethodParametersNode([p[1]]+ p[3].children)
    elif (len(p) > 1):
        p[0] = AST.MethodParametersNode(p[1])
    else:
        p[0] = AST.MethodParametersNode()

def p_error(p):
    p_error.error = True
    if p:
        print ("Syntax error in line %d" % p.lineno)
    else:
        print ("Syntax error: unexpected end of file!")
    yacc.restart()
    
p_error.error = False
yacc.yacc(outputdir='generated')

def analyse_syn(filename, treePdf, treeOut):
    prog = open(filename).read()
    ast = yacc.parse(prog)

    if ast and not p_error.error:
        if treeOut:
            print (ast)
        if treePdf:
            import os
            graph = ast.makegraphicaltree()
            
            name = os.path.split(filename)[1]
            name = os.path.splitext(name)[0] +'-ast.pdf'
            
            graph.write_pdf(name) 
            print ("wrote ast to %s" % name)
        return ast
    else:
        print("[Error] Parsing returned invalid result!")
    
    return None

if __name__ == "__main__":
    analyse_syn(sys.argv[1], True, True)

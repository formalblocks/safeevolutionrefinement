
Type = Datatype('Type')
Type.declare('String')
Type.declare('Uint')
Type = Type.create()

Version = Datatype('Version')
Version.declare('Source')
Version.declare('Target')
Version = Version.create()

Sim, (sim_1, sim_2, sim_3) = EnumSort('Sim', ['sim_1', 'sim_2', 'sim_3'])

Variable = Datatype('Variable')
Variable.declare('mkVariable', ('name', StringSort()), ('type', Type), ('version', Version))
Variable = Variable.create()
Value = Function('Value', Sim, Variable, IntSort())

ExprOp = Datatype('ExprOp')
ExprOp.declare('Mul')
ExprOp.declare('Sum')
ExprOp = ExprOp.create()

Expression = Datatype('Expression')
Expression.declare('unary', ('variable', Variable))
Expression.declare('binary', ('left', Expression), ('right', Expression), ('operation', ExprOp))
Expression = Expression.create()
Relation = Datatype('Relation')
Relation.declare('equals', ('source', Expression), ('target', Variable))
Relation = Relation.create()
evaluation = RecFunction('evaluation', Sim, Expression, IntSort())

sim = Const('sim', Sim)
exp = Const('exp', Expression)
RecAddDefinition(evaluation, [sim, exp],
                 If(Expression.is_unary(exp), Value(sim, Expression.variable(exp)),
                    If(Expression.operation(exp) == ExprOp.Mul, evaluation(sim, Expression.left(exp)) * evaluation(sim, Expression.right(exp)), evaluation(sim, Expression.left(exp)) + evaluation(sim, Expression.right(exp)))))

def equals(exp, variable):
    sim = Const('sim', Sim)
    return ForAll(sim, evaluation(sim, exp) == Value(sim, variable))

rel = Const('rel', Relation)
axioms = [ ForAll(rel, Implies(Relation.is_equals(rel), equals(Relation.source(rel), Relation.target(rel))))]

s = Solver()# s.add(axioms)
prove(*axioms)

new_var = Variable.mkVariable(String('hello'), Type.String, Version.Source)
values = And(Value(sim_1, new_var) == 1, Value(sim_2, new_var) == 2)
print(new_var)
s.add(Variable.name(new_var) == 'hello')
print(s.check())
op = Const('op', ExprOp)
exp = Const('exp', Expression)
prove(Or(op == ExprOp.Mul, op == ExprOp.Sum))
prove(Or(Expression.is_unary(exp), Expression.is_binary(exp)))

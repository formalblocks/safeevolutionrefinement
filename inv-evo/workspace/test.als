open util/integer

abstract sig Type {}
sig Str, Address, Uint, MappingType extends Type {}
abstract sig Version {}
one sig Source, Target extends Version {}
abstract sig SimulationId {}

abstract sig Mapping {
  element: Int -> Int,
  length: one Int
}

abstract sig Variable {
name: String,
type:  Type,
version: one Version
}


abstract sig Assignment {
    variable: one Variable,
    value: SimulationId -> one (Int + Mapping) 
 }


abstract sig Expression {
    variables: set Variable,
    evaluation:  SimulationId -> one Int
}

sig SimpleAssignmentExpression extends Expression {
  assignment: one Assignment
} 


fact {
  all a: SimpleAssignmentExpression |
    a.variables = a.assignment.variable and
    all simId : domain[a.evaluation] |
        eq[int a.evaluation[simId], int a.assignment.value[simId]]
}


sig MappingAssignmentExpression extends Expression {
  assignment: one Assignment,
  index: Int
} 

fact {
  all exp: MappingAssignmentExpression | 
    exp.variables = exp.assignment.variable and
    all simId : domain[exp.evaluation] |
       eq[int exp.evaluation[simId], int exp.assignment.value[simId].element[exp.index]]
}

sig PrimitiveExpression extends Expression {} {
  no variables
  and (all simId, simId2: domain[evaluation] | 
               eq[int evaluation[simId], int evaluation[simId2]])
}

abstract sig BinaryExpression extends Expression {
  left: one Expression,
   right: one Expression
}

sig SumExpression extends BinaryExpression {}

fact {
    all s: SumExpression | 
        s.variables = s.left.variables + s.right.variables 
        and (all simId: domain[s.evaluation] |
               s.evaluation[simId] = add[int s.left.evaluation[simId], int s.right.evaluation[simId]])
        and no s & (s.^left + s.^right)
}

sig MulExpression extends BinaryExpression {} 
fact {
    all s: MulExpression | 
        s.variables = s.left.variables + s.right.variables 
        and (all simId: domain[s.evaluation] |
               s.evaluation[simId] = mul[int s.left.evaluation[simId], int s.right.evaluation[simId]])
        and no s & (s.^left + s.^right)
}

abstract sig Relation {
 source: one Expression,
 target: one Variable
} {
    source.variables.version = Source
    target.version = Target
}

sig Equals extends Relation {} {
    all simId: domain[source.evaluation + variable.target.value] |
        eq[source.evaluation[simId],variable.target.value[simId]]
}

sig EqualsMapping extends Relation {} {
    all simId: domain[source.evaluation + variable.target.value] |
	all index: (variable.target.value[simId].element).univ  |
        	eq[int source.evaluation[simId], int variable.target.value[simId].element[index]]
}

fun domain [r: SimulationId -> Int] : set SimulationId {
  r.univ
}

// one sig AVarV1 extends Variable {} { name = "a"; type = Uint; version=Source }
// one sig AVarV2 extends Variable {} { name = "_a"; type = Uint; version=Target }

one sig AVarV1 extends Variable {} { name = "a"; type = MappingType; version=Source }
one sig AVarV2 extends Variable {} { name = "_a"; type = MappingType; version=Target }

one sig Sim1, Sim2, Sim3 extends SimulationId {}

// one sig AssignmentA extends Assignment {} { variable = AVarV1; value =  Sim1 -> 5 + Sim2 -> 6 + Sim3 -> 7}
// one sig AssignmentA2 extends Assignment {} { variable = AVarV2; value =  Sim1 -> 20 + Sim2 -> 24 + Sim3 -> 28}
one sig MappingSim1 extends Mapping {} {element = 0 -> 2}
one sig MappingSim2 extends Mapping {} {element = 0 -> 3}

one sig MappingASim1 extends Mapping {} {element = 0 -> 4}
one sig MappingASim2 extends Mapping {} {element = 0 -> 6}


one sig AssignmentMapA extends Assignment {} {variable = AVarV1; value = Sim1 -> MappingSim1 + Sim2 -> MappingSim2}
one sig AssignmentMapA2 extends Assignment {} {variable = AVarV2; value = Sim1 -> MappingASim1 + Sim2 -> MappingASim2}


pred Run {
all v: Variable | v in Relation.target + Relation.source.variables
no Expression.left & Expression.right
}

// pred Map {
//  some EqualsMapping
// }

// run {} for 10

run Run for 5 but 1 Relation, 5 Int
open util/integer

abstract sig Type {}
sig Str, Address, Uint, MappingType, StructType extends Type {}
abstract sig Version {}
abstract sig StructAttribute {}


one sig Target, Source extends Version {}
abstract sig SimulationId {}

abstract sig Mapping {
  element: Int -> Int,
  length: one Int
}

abstract sig Struct {}

abstract sig Variable {
name: String,
type:  Type,
version: one Version
}

abstract sig AttributeVariable extends Variable {
  parent: Variable
}

abstract sig Assignment {
    variable: one Variable,
    value: SimulationId -> (Int + Mapping + Struct) 
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
        not (univ.(a.assignment.value) in Mapping) and
        eq[int a.evaluation[simId], int a.assignment.value[simId]]
}


sig MappingAssignmentExpression extends Expression {
  assignment: one Assignment,
  index: Int
} 

fact {
  all exp: MappingAssignmentExpression | 
    exp.index in (exp.assignment.value[univ].element).univ and
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

// sig SubtractExpression extends BinaryExpression {}

// fact {
//     all s: SubtractExpression | 
//         s.variables = s.left.variables + s.right.variables 
//         and (all simId: domain[s.evaluation] |
//                s.evaluation[simId] = sub[int s.left.evaluation[simId], int s.right.evaluation[simId]])
//         and no s & (s.^left + s.^right)
// }

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
  target.type != MappingType and
  all simId: domain[source.evaluation + variable.target.value] |
    target.type = Uint and eq[source.evaluation[simId],variable.target.value[simId]] // TODO target.type
}

sig EqualsMapping extends Relation {} {
  target.type = MappingType and
  all simId: domain[source.evaluation + variable.target.value] |
        all index: (variable.target.value[simId].element).univ  |
                eq[int source.evaluation[simId], int variable.target.value[simId].element[index]]
}

fun domain [r: SimulationId -> Int] : set SimulationId {
  r.univ
}

one sig Sim1, Sim2 extends SimulationId {}

one sig Var_auctionStart_Source extends Variable {} { name = "auctionStart"; type = Uint; version=Source }
one sig Var_auctionEnd_Source extends Variable {} { name = "auctionEnd"; type = Uint; version=Source }

one sig Var_auction_Target extends Variable {} { name = "auction"; type = StructType; version=Target }


one sig Var_StartAttribute_Target extends AttributeVariable { } {
  // name = "auctionStart";
  type = Uint;
  parent = Var_auction_Target;
  version = Target
}
one sig Var_EndAttribute_Target extends AttributeVariable { } {
  // name = "auctionEnd";
  type = Uint;
  parent = Var_auction_Target;
  version = Target
}


one sig Assignment_Uint_auctionEnd_Source extends Assignment {} {
  variable = Var_auctionEnd_Source;
  value = Sim1 -> 3 + Sim2 -> 4 
}

one sig Assignment_Uint_auctionStart_Source extends Assignment {} {
  variable = Var_auctionStart_Source;
  value = Sim1 -> 2 + Sim2 -> 3 
}

one sig Assignment_Uint_endattribute extends Assignment {} {
  variable = Var_EndAttribute_Target
  value = Sim1 -> 4 + Sim2 -> 5
}

one sig Assignment_Uint_startattribute extends Assignment {} {
  variable = Var_StartAttribute_Target
  value = Sim1 -> 2 + Sim2 -> 3
}


pred Run {
all v: Variable | v.type not in StructType implies v in Relation.target + Relation.source.variables
no Expression.left & Expression.right
}

run Run for 5 but 2 Relation, 5 Int
import itertools
from jinja2 import Environment, PackageLoader, select_autoescape
from typing import List
from gen.model import *
import jpype
import jpype.imports

@dataclass
class AlloySolution(Solution):
    instance: dict
    alloy_relations: dict
    
    @dataclass
    class Atom:
        name: str
        solution: 'AlloySolution'

        def get(self, rel_name):
            return AlloySolution.Atom(self.solution.rel(self.name, rel_name), self.solution)
        
        def __str__(self) -> str:
            return self.name.replace('"', '')
        
        def typeof(self, sig_label):
            return self.name in self.solution.instance[sig_label]['objects']

    def debug(self):
        import json
        print(json.dumps(self.instance, indent=2))
        print(json.dumps(self.alloy_relations, indent=2))

    def make_atom(self, name):
        return self.Atom(name, self)
    
    def rel(self, atom, relation, single_elem=True):
        response = self.alloy_relations[relation][atom]
        if single_elem:
            return response[-1]
        else:
            return response

    @dataclass(frozen=True)
    class AlloyRelation(Relation):
        atom: 'AlloySolution.Atom'
        universal_quantifier: bool

        def __str__(self) -> str:
            expression = self.atom.get('source')
            target = self.atom.get('target').get('name')


            def undo_spread(exp) -> str:
                if SPREAD_FLAG in str(exp):
                    split = str(exp).split(SPREAD_FLAG)
                    return f'{split[0]}[i].{split[1]}'
                else:
                    return f'{str(exp)}[i]'

            def evaluate(exp, simple=False):
                if exp.typeof('this/PrimitiveExpression'):
                    return exp.get('evaluation')
                else:
                    result = f'{exp.get("variables").get("name")}'
                    if self.universal_quantifier and not simple:
                        result += '[i]'
                    return result
                    
            
            if expression.typeof('this/SimpleAssignmentExpression'):
                return f'{target} == {evaluate(expression, simple=True)}'
            
                       
            if expression.typeof('this/MappingAssignmentExpression'):
                source_exp = evaluate(expression, simple=True)
                if SPREAD_FLAG in str(target) or SPREAD_FLAG in source_exp:
                    return f'forall (uint i) {undo_spread(target)} == {undo_spread(source_exp)}'
                else:
                    return f'__verifier_eq({target}, {source_exp})'

            operation = ''
            if expression.typeof('this/SumExpression') or expression.typeof('this/SumMapExpression'):
                operation = '+'
            elif expression.typeof('this/MulExpression') or expression.typeof('this/MulMapExpression'):
                operation = '*'
            else:
                raise RuntimeError('Unsupported Operation', expression)

            if self.universal_quantifier:
                return f'forall (uint i) {target}[i] == {evaluate(expression.get("left"))} {operation} {evaluate(expression.get("right"))}'
            else:
                return f'{target} == {evaluate(expression.get("left"))} {operation} {evaluate(expression.get("right"))}'
    
    @property
    def inferred_relations(self) -> list[Relation]:
        """
        Return an inferred relation *for each variable*.
        It does not mean that it will eagerly return all possible relations.
        TODO: Call new solution within alloy API
        """
        result = []
        def interpret(objects, forall):
            if objects:
                for equalsSigAtom in objects:
                    result.append(self.AlloyRelation(self.make_atom(equalsSigAtom), forall))

        objects = self.instance.get('this/Equals').get('objects')
        interpret(objects, False)
        objects = self.instance.get('this/EqualsMapping').get('objects')
        interpret(objects, True)
        
        return result



import json, dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

def get_struct_attr_var_name(var: Variable, attr: str) -> str:
    return f'{var.name}.{attr}'

def build_struct_var_attr(var: StructVariable, attr: str) -> Variable:
    return Variable(get_struct_attr_var_name(var, attr), Type.Uint, var.version)

SPREAD_FLAG = '__spread__'

def get_mapping_struct_var_name(variable: MappingVariable, key: str):
    return f'{variable.name}{SPREAD_FLAG}{key}'

def build_mapping_struct_var(variable: MappingVariable, key: str):
    return MappingVariable(get_mapping_struct_var_name(variable, key), variable.version, variable.keyType, Type.Uint)

class AlloyInferEngine(InferEngine):

    
    @staticmethod
    def infer(instances: List[ContractInstance]) -> AlloySolution:
        variables: Set[Variable] = set(variable for instance in instances for variable in instance.variables)
        variables = AlloyInferEngine._spread_struct_vars(variables)
        variables = AlloyInferEngine._spread_mapping_structvalue_vars(variables)

        assignments: List[Assignment] = [assignment for instance in instances for assignment in instance.assignments]
        assignments = AlloyInferEngine._spread_struct_assignments(assignments)
        assignments = AlloyInferEngine._spread_mapping_structvalue_assignments(assignments)

        simulations = set(instance.simulation for instance in instances)
        group_dict: dict[Variable, List] = dict()
        integers = set()
        for assignment in assignments:
            new_value = group_dict.get(assignment.variable, [])
            if isinstance(assignment.value, dict): # TODO wrap this logic in a class and support more types
                assignment = dataclasses.replace(assignment, value=AlloyInferEngine._simplify(assignment.value))
                integers.union(set(assignment.value.items()))
                integers.union(set(assignment.value.keys()))
            else:
                integers.add(assignment.value)

            new_value.append(assignment)
            group_dict[assignment.variable] = new_value
            
        assignments_groupedby_variable = [(var, assignments) for (var, assignments) in group_dict.items()]
        versions: Set[ContractVersion] = set(instance.version for instance in instances)
        default_integer_scope = 5
        source_code = AlloyInferEngine._gen_source_code(versions=versions,
                                                  simulations=simulations,
                                                  integer_scope=max(len(integers) + 1, # TODO + 1
                                                                     default_integer_scope),
                                                  variables=variables,
                                                  assignments_groupedby_variable=assignments_groupedby_variable)
        print(source_code)
        return AlloyInferEngine._call_alloy(source_code)
    
    @staticmethod
    def _simplify(assignment_value):
        """
        Convert string keys to int keys (limited scope)
        """
        string_keys = [key for key in assignment_value.keys() if isinstance(key, str)]
        if len(string_keys) > 0:
            result = {}
            for idx, string_key in enumerate(string_keys):
                result[idx] = assignment_value[string_key]
            return result
        return assignment_value
    
    @staticmethod
    def _spread_struct_vars(variables: Set[Variable]) -> Set[Variable]:
        """
        Transform structs into separate variables
        """
        response = set()
        for variable in variables:
            if isinstance(variable, StructVariable):
                response = response.union(set([build_struct_var_attr(variable, attr) for attr in variable.attrs]))
            else:
                response.add(variable)
        return response
    
    @staticmethod
    def _spread_struct_assignments(assignments: list[Assignment]) -> list[Assignment]:
        """
        Transform struct assignments into separate variable assignments
        @see __spread_struct_var
        """
        response = []
        for assignment in assignments:
            if isinstance(assignment.variable, StructVariable):
                for attr in assignment.variable.attrs:
                    variable = build_struct_var_attr(assignment.variable, attr)
                    new_assignment = Assignment(variable, assignment.simulation, value=assignment.value[attr])
                    response.append(new_assignment)
            else:
                response.append(assignment)
        return response
        

    @staticmethod
    def _spread_mapping_structvalue_vars(variables: Set[Variable]) -> Set[Variable]:
        """
        Transform mapping which have struct values as separate variables
        S: struct { x: uint, y: uint}
        m: mapping[uint, S]:
            1. mapping[uint, uint] m_x
            2. mapping[uint, uint] m_y 
        """
        response = set()
        for variable in variables:
            if isinstance(variable, MappingVariable) and  variable.valueType is Type.Struct:
               response = response.union(set([build_mapping_struct_var(variable, attr) for attr in variable.valueAttrs]))
            else:
                response.add(variable)
        return response
    
    @staticmethod
    def _spread_mapping_structvalue_assignments(assignments: list[Assignment]) -> list[Assignment]:
        """
        Transform mapping[_,struct] assignments into separate variable assignments
        @see __spread_mapping_structvalue_vars
        """
        response = []
        for assignment in assignments:
            if isinstance(assignment.variable, MappingVariable) and assignment.variable.valueType is Type.Struct:
                struct_attr_idx_dict = {}
                for key in assignment.value:
                    for struct_key in assignment.value[key]:
                        struct_attr_idx_dict[struct_key] = struct_attr_idx_dict.get(struct_key, {})
                        struct_attr_idx_dict[struct_key][key] = assignment.value[key][struct_key]
                
                for struct_key in struct_attr_idx_dict:
                    new_variable = build_mapping_struct_var(assignment.variable, struct_key)
                    response.append(Assignment(new_variable, assignment.simulation, struct_attr_idx_dict[struct_key]))
            else:
                response.append(assignment)
        return response
 
    @staticmethod
    def _gen_source_code(**kwargs):
        try:
            env = Environment(
                loader=PackageLoader("alloy"),
                autoescape=select_autoescape()
            )
        except ModuleNotFoundError as _:
            env = Environment(
                loader=PackageLoader("gen"),
                autoescape=select_autoescape()
            )

        template = env.get_template("template.jinja")
        return template.render(**kwargs)
    
    @staticmethod
    def _call_alloy(source_code: str) -> AlloySolution:
        try:
            jpype.startJVM(classpath=["org.alloytools.alloy.dist.jar"])
        except OSError as e:
            print(e)

        from edu.mit.csail.sdg.parser import CompUtil
        from edu.mit.csail.sdg.alloy4 import A4Reporter
        from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod

        # find an instance for the model

        rep = A4Reporter()

        world = CompUtil.parseEverything_fromString(rep, source_code)

        commands = world.getAllCommands()
        assert commands.size() > 0
        cmd = commands.get(0)
        opt = A4Options()
        opt.solver = A4Options.SatSolver.SAT4J

        solution = TranslateAlloyToKodkod.execute_command(rep, world.getAllSigs(), cmd, opt)
        instance = {}
        relations = {}

        for sig in world.getAllReachableSigs():
            sig_label = str(sig.label)
            instance[sig_label] = dict(objects={},fields={})
            instance[sig_label]["objects"] = [str(obj) for obj in solution.eval(sig)]
            for field in sig.getFields():
                field_label = str(field.label)
                instance[sig_label]["fields"][field_label] = []
                tuples = solution.eval(field)
                arity = tuples.arity()
                relations[field_label] = relations.get(field_label, {})
                for tup in tuples:
                    t = tuple(str(tup.atom(i)) for i in range(arity))
                    relations[field_label][t[0]] = t[1:]
                    instance[sig_label]["fields"][field_label].append(t)
        return AlloySolution(instance, relations)






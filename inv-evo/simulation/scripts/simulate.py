import os
import yaml
from typing import Annotated, Literal
from slither import Slither
from slither.core.declarations import Contract, FunctionContract
from slither.solc_parsing.solidity_types.type_parsing import MappingType, UserDefinedType, ElementaryType
from slither.core.declarations.structure import Structure
from brownie.convert.datatypes import Wei, ReturnValue, EthAddress
from brownie.network.account import Account
from brownie.typing import Accounts
from gen.alloy import AlloyInferEngine
from gen.model import InferEngine, Solution

from gen.read import readl_yaml_str
from scripts.utils import ValueRange, optimal_set_cover


SIMULATIONS_COUNT = 2 # Number of simulations

def read_contract(file_path):
    slither = Slither(file_path)
    contract = slither.contracts[0]
    return contract

def extract_variables(contract):
    state_variables = contract.variables
    variable_info = [(var.name, var.type) for var in state_variables]
    return variable_info

def compare_contracts(contract1, contract2):
    variables_contract1 = extract_variables(contract1)
    variables_contract2 = extract_variables(contract2)

    differences = ([],[])

    set_contract1 = set((name, type_) for name, type_ in variables_contract1)
    set_contract2 = set((name, type_) for name, type_ in variables_contract2)

    variables_only_in_contract1 = set_contract1 - set_contract2
    for name, type_ in variables_only_in_contract1:
        differences[0].append((name, type_))

    variables_only_in_contract2 = set_contract2 - set_contract1
    for name, type_ in variables_only_in_contract2:
         differences[1].append((name, type_))
    
    return differences

def candidate_functions_for_simulation(slither_contract: Contract, diff_variables) -> list[FunctionContract]:
    function_instance_dict = dict() # Store name: instances
    function_var_dict = dict() # Store name: variables
    function_costs_dict = dict() # Store name: costs
    variables = set(name for (name, _type) in diff_variables)
    variables_found = set() # variables used within functions
    function_names = set()
    
    for f in slither_contract.functions:
        intended_visibilities = ["public", "external"]
        has_intended_visibility = any(v in f.visibility for v in intended_visibilities)
        if  has_intended_visibility and \
                f.name != 'constructor' and \
                f.name != 'emitMap' and \
                    not f.view:
            function_names.add(f.name)
            function_costs_dict[f.name] = len(f.parameters)
            function_instance_dict[f.name] = f
            for state_variable_written in f.all_state_variables_written():
                if state_variable_written.name in [name for (name, _type) in diff_variables]:
                    f_vars = function_var_dict.get(f.name, set())
                    f_vars.add(state_variable_written.name)
                    function_var_dict[f.name] = f_vars
                    variables_found.add(state_variable_written.name)
    
    for variable in variables:
        if variable not in variables_found:
            """
            If variable is not modified within any function, then we assume that any function
            is sufficient to capture its behavior.
            """
            for fname in function_names:
                vars = function_var_dict.get(fname, set())
                vars.add(variable)
                function_var_dict[fname] = vars

    candidate_functions = optimal_set_cover(variables, function_var_dict, function_costs_dict)
    if not candidate_functions:
        """
        If no function modifies the variables, then it probably is a constant.
        Execute only the constructor
        """
        return []
    return [function_instance_dict[fname] for fname in candidate_functions]

def candidate_arguments(functions: list[FunctionContract], accounts: Accounts):
    """
    Example:
        simulations = [
            [('transfer', [random_address, 1])],
            [('transfer', [random_address, 2])],
        ]
    """ 
    
    def choose_argument(parameter, round):
        param_type_str = str(parameter.type)
        if param_type_str == 'address':
            random_address = get_account((round % SIMULATIONS_COUNT)  + 1, accounts) # different address than the msg.sender and reuse
            return random_address
        elif param_type_str.startswith('uint'):
            return round
        elif param_type_str.startswith('bool'):
            return bool(round % 2)
        else:
            raise NotImplementedError(f'{parameter}')
        
    for round in range(1, SIMULATIONS_COUNT + 1):
        # Generate only two simulations
        simulation = []
        for f in functions:
            args = [choose_argument(param, round) for param in f.parameters ]
            # if f.payable:
            #     class PayableType:
            #         type = 'payable'
            #         name = 'value'
            #     args.append(choose_argument(PayableType(), round))
            simulation.append((f.name, args))
        yield simulation


def get_account(sim_id: Annotated[int, ValueRange(1, 9)], accounts: Accounts):
    return accounts.at(f'0x000000000000000000000000000000000000000{sim_id}', force=True)

def main():
    contracts_dir = './contracts'
    files_names = os.listdir(contracts_dir)
    files_names.sort()
    c1_slither = read_contract(os.path.join(contracts_dir, files_names[0])) # concrete
    c2_slither = read_contract(os.path.join(contracts_dir, files_names[1])) # abstract

    c1_diff, c2_diff = compare_contracts(c1_slither, c2_slither)

    if not c1_diff and not c2_diff:
        # Contracts are identical. Abs fun is trivial. TODO: print all equations
        print('true')
        return
    
    if not c2_diff:
        # No variable in the abstract contract was modified. Concrete contract can have additional attributes TODO
        print('true') 
        return
    
    functions = candidate_functions_for_simulation(c1_slither, c1_diff)

    from brownie import accounts
    import brownie

    simulations = candidate_arguments(functions, accounts)

    Contract1: Contract = getattr(brownie, c1_slither.name)
    Contract2: Contract = getattr(brownie, c2_slither.name)
    
    def deploy(contract, sim_id):
        account = get_account(sim_id, accounts)
        deployment =  contract.deploy({"from": account})
        update_mappings(deployment.tx)
        return deployment

    c1_assignments = dict()
    c2_assignments = dict()
    
    mappings_updates = {}
    def update_mappings(tx):
        for event in tx.events:
            if event.name == 'Map':
                mappings_updates.setdefault(event['fun'], [])
                print('update', event['fun'], str(event['keyaddr'] or event['keyint']))
                mappings_updates[event['fun']].append(str(event['keyaddr'] or event['keyint'])) # TODO hardcoded key (address type)

    # deploy1.events.subscribe("Map", lambda event: print(f"{event['event']} at block {event['blockNumber']}"))

    def process_diff_raw_assignments(contract_diff, contract_assignments, deploy, idx):
        def map_types_str(solidity_type):
            if isinstance(solidity_type, MappingType):
                return 'MappingType'
            elif isinstance(solidity_type, UserDefinedType):
                return 'Struct'
            elif isinstance(solidity_type, ElementaryType):
                if 'uint' in str(solidity_type):
                    return 'Uint'
                elif 'address' in str(solidity_type):
                    return 'Address'
                elif 'bool' in str(solidity_type):
                    return 'Uint' # TODO: fix
                elif 'bytes' in str(solidity_type):
                    return 'Uint' # TODO: fix
            return NotImplementedError(f'Not implemented for {solidity_type}')
        for diff in contract_diff:
            attr_name, attr_type = diff
            contract_assignments.setdefault(attr_name, {})
            if isinstance(attr_type, MappingType):
                map_value = {'__meta_type': map_types_str(attr_type), 
                             '__meta_keyType': map_types_str(attr_type.type_from), 
                             '__meta_valueType': map_types_str(attr_type.type_to)}
                if isinstance(attr_type.type_to, UserDefinedType) and isinstance(attr_type.type_to.type, Structure):
                    # mapping (x => Struct (a, b...))
                    valueAttrs = [key.name for key in attr_type.type_to.type.elems_ordered]
                    map_value['__meta_valueAttrs'] = valueAttrs
                    print(attr_name, valueAttrs)
                    for key in mappings_updates[attr_name]:
                        evaluation = {}
                        if len(valueAttrs) > 1:
                            value: ReturnValue = getattr(deploy, attr_name)(key)
                            for valueAttr in valueAttrs:
                                try:
                                    evaluation[valueAttr] = \
                                        value.dict()[valueAttr]
                                except AttributeError:
                                    print(f'Warning: Trying to access {valueAttr} from {attr_name}. {attr_name} may have only one literal attribute. Mappings inside structs are not supported')
                                    evaluation[valueAttr] = value
                        else: 
                            # Single struct value, no need to unpack
                            evaluation[valueAttrs[0]] = getattr(deploy, attr_name)(key)
                        map_value[key] = evaluation
                else:
                    # mapping (x => literal)
                    for key in mappings_updates[attr_name]:
                        literal_value = getattr(deploy, attr_name)(key)
                        int_literal_value = int(literal_value) # TODO: workaround for booleans
                        map_value[key] = int_literal_value
                contract_assignments[attr_name][idx] = map_value
            elif isinstance(attr_type, UserDefinedType): 
                struct_value = getattr(deploy, attr_name)()
                evaluation_map = {'__meta_type': 'Struct', '__meta_attrs': set()}
                for i, elem in enumerate(attr_type.type.elems_ordered):
                    evaluation_map[elem.name] = struct_value[i]
                    evaluation_map['__meta_attrs'].add(elem.name)
                contract_assignments[attr_name][idx] = evaluation_map 
            else:
                value = getattr(deploy, attr_name) 

                if callable(value):
                    value = value()

                if isinstance(value, EthAddress) or isinstance(value, Account):
                    value = str(value)[-2:] # TODO workaround: only last digits

                contract_assignments[attr_name][idx] = int(value) # TODO

    for idx, simulation in enumerate(simulations, 1): # Start from 1
        deployment1 = deploy(Contract1, idx) # Always redeploy after last simulation (start from zero)
        deployment2 = deploy(Contract2, idx)
        for call in simulation:
            fname, args = call
            print(fname, args)
            f = getattr(deployment1, fname)
            if f.payable:
                tx = f(*args, {"value": 1})
            else:
                tx = f(*args)
            update_mappings(tx)
            f = getattr(deployment2, fname)
            if f.payable:
                tx = f(*args, {"value": 1})
            else:
                tx = f(*args)
            update_mappings(tx)

        print(mappings_updates)

        process_diff_raw_assignments(c1_diff, c1_assignments, deployment1, idx)
        process_diff_raw_assignments(c2_diff, c2_assignments, deployment2, idx)

    assignments_dict = dict(source=[],target=[])
    def build_assignment_dict(contract_assignments, version: Literal['source', 'target']):
        for key, raw_values in contract_assignments.items():
            values = []
            attrs = None
            raw_value_type_sol = 'Uint'
            valueAttrs = None
            keyType = None
            valueType = None
            for sim, raw_value in raw_values.items():
                if isinstance(raw_value, dict):
                    attrs = raw_value.pop('__meta_attrs', attrs)
                    raw_value_type_sol = raw_value.pop('__meta_type')
                    valueAttrs = raw_value.pop('__meta_valueAttrs', None)
                    keyType = raw_value.pop('__meta_keyType', None)
                    valueType = raw_value.pop('__meta_valueType', None)
                values.append(dict(sim=sim, evaluation=raw_value))
            
            assignment_dict = dict(name=key, type=raw_value_type_sol, values=values,
                                                  attrs=attrs, keyType=keyType, valueType=valueType,
                                                  valueAttrs=valueAttrs)
            
            cleaned_assignment_dict = dict((k, v) for (k, v) in assignment_dict.items() if v is not None)
            assignments_dict[version].append(cleaned_assignment_dict)


    build_assignment_dict(c1_assignments, 'source')
    build_assignment_dict(c2_assignments, 'target')
    def wei_yaml_dumper(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:int', str(data))
    
    yaml.add_representer(Wei, wei_yaml_dumper)
    print(assignments_dict)
    simulations_yaml = yaml.dump(assignments_dict)
    print(simulations_yaml)
    instances = readl_yaml_str(simulations_yaml)
    inference_engine: InferEngine = AlloyInferEngine
    solution: Solution = inference_engine.infer(instances)
    for solution in solution.inferred_relations:
        print(str(solution))


if __name__ == '__main__':
    main()    
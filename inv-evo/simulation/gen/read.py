from typing import Dict, Literal
from gen.model import *
import yaml


def _build_var(var_yaml: dict, version: ContractVersion) -> Variable:
    var = Variable(var_yaml['name'], Type[var_yaml['type']], ContractVersion.from_str(version))
    if var.type is Type.MappingType:
        assert 'keyType' in var_yaml, 'The keyType must be declared for MappingType'
        assert 'valueType' in var_yaml, 'The valueType must be declared for MappingType'
        var = MappingVariable(var.name, var.version, Type[var_yaml['keyType']], Type[var_yaml['valueType']])
        if var.valueType is Type.Struct:
            assert 'valueAttrs' in var_yaml, 'The valueAttrs must be declared for MappingType with valueType Struct'
            var = MappingVariable(var.name, var.version, var.keyType, var.valueType, valueAttrs=tuple(var_yaml['valueAttrs']))
    if var.type is Type.Struct:
        var = StructVariable(var.name, var.version, tuple(var_yaml['attrs']))
    
    return var
                

"""
source: &version
  - name: str
    type: str
    values:
      - sim: int
        evaluation: object
target:
    <<: version
"""
def readl_yaml_str(model_str: str) -> List[ContractInstance]:
    model = yaml.safe_load(model_str)

    def read_version(version: Literal['source', 'target'], model) -> List[ContractInstance]:
        instances = []
        variables: Dict[Simulation, Set] = dict()
        assignments: Dict[Simulation, List] = dict()
        for var_yaml in model[version]:
            var = _build_var(var_yaml, version)
            for value in var_yaml['values']:
                sim = Simulation(value['sim'])
                variables[sim] = variables.get(sim, set())
                variables[sim].add(var)
                if isinstance(var, StructVariable):
                    for key in value['evaluation'].keys():
                        assert key in var.attrs, f'{key} must be declared in attrs'
                if isinstance(var, MappingVariable) and var.valueType is Type.Struct:
                    for key in value['evaluation'].keys():
                        for struct_key in value['evaluation'][key]:
                            assert struct_key in var.valueAttrs, f'{struct_key} must be declared in valueAttrs'
                assignments[sim] = assignments.get(sim, []) + [Assignment(var, sim, value['evaluation'])]
        for (sim, sim_assignments) in assignments.items():
            instance = ContractInstance(sim, variables[sim], sim_assignments, ContractVersion.from_str(version))
            instances.append(instance)
        return instances
    
    return read_version('source', model) + read_version('target', model)
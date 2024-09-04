from model import *
from alloy import AlloyInferEngine, AlloySolution

from read import readl_yaml_str
instances = readl_yaml_str(
"""
source:
  - name: a
    type: Uint
    values:
      - sim: 1
        evaluation: 5
      - sim: 2
        evaluation: 10
  - name: b
    type: Uint
    values:
      - sim: 1
        evaluation: 5
      - sim: 2
        evaluation: 10
target:
  - name: a_
    type: Uint
    values:
      - sim: 1
        evaluation: 10
      - sim: 2
        evaluation: 20
  - name: b
    type: Uint
    values:
      - sim: 1
        evaluation: 5
      - sim: 2
        evaluation: 10      
"""
)
inference_engine: InferEngine = AlloyInferEngine
instance: Solution = inference_engine.infer(instances)
print(instance.inferred_relations)
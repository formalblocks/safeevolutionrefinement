from openai import OpenAI

client = OpenAI(api_key='')

def infer_abstraction_function(file1_content, file2_content):

    prompt = f'''Given the Solidity files:
                File 1:{file1_content}
                File 2:{file2_content}
                Please infer an equation between the changed and new variables from the first contract 
                to the second. Return only the equation/expression. No need to explain. 
                Desconsider the constructor. Do not rename the variables
                '''

    # Call the OpenAI API
    response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages = [{'role': 'user', 'content': prompt}],
        temperature=0.1)

    # Return the response
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # Example Solidity files
    file1_content = """
    contract MyContract {
        uint256[] public _myNumber;

        constructor() {
            myNumber = 100;
        }

        function setNumber(uint256 _number) public {
            myNumber = _number;
        }
    }
    """

    file2_content = """
    contract MyContract {
        uint256 public myNumber;

        constructor() {
            myNumber = 200;
        }

        function setNumber(uint256 _number) public {
            myNumber = _number + 1;
        }
    }
    """

    inferred_abstract_function = infer_abstraction_function(file1_content, file2_content)

    print("Inferred Abstraction Function:")
    print(inferred_abstract_function)
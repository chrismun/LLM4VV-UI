import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jsonlines
from utils import generate_one_completion, parse_output, compile_and_run_test

MODEL_PATH = "Phind/Phind-CodeLlama-34B-v2" 
MAX_RETRIES = 3
num_gpu = torch.cuda.device_count()

print(f'####### Num GPU: {num_gpu}')
print(f'####### Model: {MODEL_PATH}')
print(f'####### Max retries: {MAX_RETRIES}')

def load_model(model_path):
    """Loads model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map='auto')
    return model, tokenizer

def run_test():
    """Runs the parsed test using nvc."""
    test_file = "parsedTest.c"
    return compile_and_run_test(test_file)

def main():
    model, tokenizer = load_model(MODEL_PATH)

    with jsonlines.open("prompts/prompts.jl") as reader:
        for line in reader:
            prompt = line["Instruction"]
            original_instruction = prompt
            for retry in range(MAX_RETRIES + 1):
                print(f"###### Generating test, try #{retry + 1}...")
                response = generate_one_completion("Write OpenACC compiler validation tests", prompt, model, tokenizer)
                print("="*30)
                print(f'###### Prompt:\n {prompt}')
                # print(f"###### Response:\n {response}")
                # print("="*30)
                code = parse_output(response)
                exit_code, compiler_output, runtime_output = run_test()
                print(f"Generated Test: {code}")
                print("="*30)
                print(f"###### Exit code: {exit_code}")
                print(f"###### Compiler output:\n {compiler_output}")
                print(f"###### Runtime output:\n {runtime_output}")
                print("="*30)
                if exit_code == 0:
                    print(f"###### Test passed. num retries: {retry}")
                    break
                else:
                    print("###### Test failed.")
                    prompt = original_instruction + f"\nResponse: {code}\n\nTest failed.\nRetry based on compiler output: {compiler_output}\nruntime output: {runtime_output}\n"
            else:
                print("###### Maximum retries reached.")
                if exit_code == 0:
                    print("###### Final Test passed. (shouldnt happen right?)")
                else:
                    print("###### Final Test failed.")
                print("="*30) 

if __name__ == "__main__":
    main()

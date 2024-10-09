import torch
import os 
import subprocess
import re 

def generate_one_completion(system: str, instruction: str, model, tokenizer, input: str = None):
    if input:
        prompt = f"### System:\n{system}\n\n### User:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n"
    else:
        prompt = f"### System:\n{system}\n\n### User:\n{instruction}\n\n### Response:\n"

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    print(f'prompt len: {len(inputs.input_ids[0])} tokens')
    
    with torch.no_grad():
        generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=1024, do_sample=True, top_p=0.75, top_k=40, temperature=0.12)

    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]
    
    # Freeing up GPU memory explicitly
    del inputs
    del generate_ids
    torch.cuda.empty_cache()

    return completion


def parse_output(text):
    sections = text.split('==================================')
    if not sections:
        print("No sections found in the file.")
        return

    last_section = sections[0].strip()
    # code_matches = re.findall(r'```[cC]?([\s\S]+?)```', last_section, re.DOTALL)
    # code_matches = re.findall(r'```(?:c|C)?([\s\S]+?)```', last_section, re.DOTALL) #noncapture c/C
    code_matches = re.findall(r'```(?:c|C)?\s*([\s\S]+?)```', last_section, re.DOTALL)

    if code_matches:
        code = code_matches[-1].strip()
        print(f"Code found. Length: {len(code)} characters.")

        output_file_path = "parsedTest.c"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(code)
            
        print(f"Saved code to {output_file_path}")
        return code
    else:
        print("Code not found.")
        return 

    return code


def compile_and_run_test(test_file):
    try:
        base_name = os.path.splitext(os.path.basename(test_file))[0]
        build_path = os.path.join('build', base_name)

        if test_file.endswith(".c"):
            compile_command = f"nvc -acc -Minfo=all -o {build_path} {test_file}"
        elif test_file.endswith(".cpp"):
            compile_command = f"nvc++ -acc -Minfo=all -o {build_path} {test_file}"  # Update this command as needed
        elif test_file.endswith(".f90"):
            compile_command = f"nvfortran -acc -Minfo=all -o {build_path} {test_file}"  # Update this command as needed
        else:
            print("Unsupported file type.")
            return 1, "Unsupported file type", ""

        # Compile 
        os.makedirs('build', exist_ok=True)
        compile_result = subprocess.run(compile_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        compile_output = compile_result.stderr.strip() if compile_result.stderr else compile_result.stdout.strip()
        compile_exit_code = compile_result.returncode

        if compile_exit_code != 0:
            return compile_exit_code, compile_output, ""

        # Run 
        run_command = f"./{build_path}"
        run_result = subprocess.run(run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        run_output = run_result.stdout.strip() if run_result.stdout else run_result.stderr.strip()
        run_exit_code = run_result.returncode

        return run_exit_code, compile_output, run_output

    except Exception as e:
        return 1, f"An error occurred: {str(e)}", ""

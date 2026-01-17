import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    print("Hello from bootdev-llm!")
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("api key not found!")

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    client = genai.Client(api_key=api_key)

    model='gemini-2.5-flash'
    
    no_result = True
    
    for _ in range(20):
        response = client.models.generate_content(model=model, contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt))
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)
        if args.verbose:
            if response.usage_metadata is None:
                raise RuntimeError("usage metadata is none")
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        function_results = []
        if response.function_calls:
            for function_call in response.function_calls:
                #print(f"Calling function: {function_call.name}({function_call.args})")
                function_call_result = call_function(function_call)
                if not function_call_result.parts:
                    raise Exception
                if not function_call_result.parts[0].function_response:
                    raise Exception
                if not function_call_result.parts[0].function_response.response:
                    raise Exception
                function_results.append(function_call_result.parts[0])
                if args.verbose:
                    return print(f"-> {function_call_result.parts[0].function_response.response}")
            messages.append(types.Content(role="user", parts=function_results))
        else:
            print(response.text)
            no_result = False
            break
    if no_result:
        print("Something went wrong and we couldn't generate final result")
        sys.exit(1)

if __name__ == "__main__":
    main()

from src.initial_generator import InitialGenerator

initial_generator = InitialGenerator(model="gpt35-turbo", strategy="zero-shot")

print(initial_generator.generate(problem="What is the capital of France?"))

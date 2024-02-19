from src.dataset import Dataset
from src.initial_generator import InitialGenerator

dataset = Dataset(dataset="ds-1000").dataset

problem = dataset["Pandas"][0]["prompt"]

initial_generator = InitialGenerator(model="gpt35-turbo", strategy="zero-shot")

print(initial_generator.generate(problem=problem))

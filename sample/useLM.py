import lmstudio as lms


model = lms.llm("omni-coder-9b")
result = model.respond("2*3=?")

print(result)
model.unload()
model=lms.embedding_model("qwen3-embedding-0.6B")
result=model.embed("Hello, world!")
#print(result)
model.unload()


from transformers import GPT2LMHeadModel, GPT2Tokenizer, AdamW
from torch.utils.data import Dataset, DataLoader
import torch


model_name = "gpt2"

tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

class OrthodoxDataset(Dataset):
    def __init__(self, file_path, tokenizer, block_size=512):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.examples = tokenizer(text, truncation=True, padding="max_length", return_tensors="pt", max_length=block_size)["input_ids"]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return self.examples[i]

dataset = OrthodoxDataset("orthodox_text.txt", tokenizer)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

optimizer = AdamW(model.parameters(), lr=5e-5)

model.train()
for epoch in range(3):
    for batch in dataloader:
        optimizer.zero_grad()
        outputs = model(batch, labels=batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} complete")

model.save_pretrained("./orthodox_gpt")
tokenizer.save_pretrained("./orthodox_gpt")
def ask_orthodox_gpt(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=200, temperature=0.8, top_k=50, top_p=0.95)
    return tokenizer.decode(output[0], skip_special_tokens=True)

print(ask_orthodox_gpt("Explain the meaning of the Jesus Prayer:"))
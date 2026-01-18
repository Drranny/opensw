import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# 모델 설정
MODEL_ID = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"

print(f"[INFO] Loading Language Model: {MODEL_ID}")
print("[INFO] Infrastructure: CPU-Optimized (16 Cores)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    trust_remote_code=True
)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

def rag_answer(prompt):
    """
    RAG 답변 생성 및 추론 성능 지표 출력
    """
    messages = [
        {"role": "system", "content": "You are a Harry Potter expert. Answer concisely based on the context in Korean."},
        {"role": "user", "content": prompt}
    ]
    
    input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    input_token_count = input_ids.shape[1]

    print("\n" + "-"*60)
    print(f"[DEBUG] Prompt Token Count: {input_token_count}")
    print("[DEBUG] Local Inference in Progress...")
    print("-"*60)

    # 시간 측정 시작
    start_time = time.perf_counter()
    
    outputs = pipe(
        input_text,
        max_new_tokens=300,
        do_sample=True,
        temperature=0.3,
        top_p=0.9
    )
    
    end_time = time.perf_counter()
    duration = end_time - start_time

    # 결과 파싱
    full_output = outputs[0]["generated_text"]
    response = full_output.split("[|assistant|]")[-1].strip()
    output_token_count = len(tokenizer.encode(response))

    # 성능 메트릭 출력
    print(f"[DEBUG] Latency: {duration:.2f}s")
    print(f"[DEBUG] Throughput: {output_token_count / duration:.2f} tokens/s")
    print(f"[DEBUG] Response Token Count: {output_token_count}")
    print("-"*60 + "\n")

    return response
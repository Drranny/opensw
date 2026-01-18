def build_prompt(contexts, query):
    """
    EXAONE 3.5 맞춤형 RAG 프롬프트 생성
    모델의 특수 태그([|system|], [|user|], [|assistant|]) 구조를 활용
    """
    # 1. 컨텍스트를 하나로 합침 (가독성을 위해 번호 부여)
    context_str = ""
    for i, ctx in enumerate(contexts[:3], 1):
        context_str += f"[{i}] {ctx}\n"
    
    # 2. EXAONE의 Instruction Following 성능을 높이는 프롬프트 구성
    # 시스템 역할과 참고 자료를 명확히 구분해줍니다.
    system_msg = (
        "You are a helpful assistant and a Harry Potter expert. "
        "Use the provided information to answer the user's question accurately. "
        "If the answer is not in the information, answer based on your knowledge but mention it's not in the context."
    )
    
    # EXAONE 전용 포맷팅
    prompt = f"""[|system|]{system_msg}

Information:
{context_str}
[|user|]{query}
[|assistant|]"""
    
    return prompt
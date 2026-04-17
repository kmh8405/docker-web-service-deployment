import json
import redis
from llama_cpp import Llama

redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)


# 여기(worker)에서는 비동기식을 안 쓰고 동기식을 사용할 예정
# Worker는 모델을 순차적으로 처리해야 하므로 동기 방식 사용 (동시 요청 시 모델 상태 충돌 방지)
def run():
    while True:
        # 1) Queue에서 task를 dequeue
        # _, task = redis_client.brpop("queue")
        # 위 방식을 조금 더 안정성이 높게 보완하자면, BRPOP은 (queue_name, data)이므로 명확하게 쓰면 아래와 같이 작성
        queue_name, task = redis_client.brpop("queue") # 가독성도 좋아짐

        # task_data: dict = json.loads(task)
        # 만약 위 방식으로 처리하다가 JSON이 깨졌거나, Redis 이상 데이터가 있는 상황이라면 바로 터지기 때문에 최소한의 예외 처리 필수
        try:
            task_data: dict = json.loads(task)
        except Exception:
            continue

        # 2) (반복) 추론 -> 토큰 -> Publish
        response_generator = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task_data["user_input"]},
            ],
            max_tokens=256,
            temperature=0.7,
            stream=True, # 토큰 단위로 결과 반환 -> 실시간으로 Pub/Sub 전송 가능
        )

        # 여기까지는 아직 추론이 시작되지 않았고, 토큰을 생성하는 generator만 생성된 상태
        # 실제 추론은 아래 for문에서 시작됨

        channel = task_data["channel"]
        for chunk in response_generator: # 추론 다 했으면 알아서 반복문 탈출
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                redis_client.publish(channel, token)

        # 3) 추론 종료 알림: [DONE] 메시지 전송
        redis_client.publish(channel, "[DONE]")
        

# 이 파일이 직접 실행한 경우에만, run() 호출
if __name__ == "__main__":
    run()
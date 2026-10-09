import requests

URL = "http://localhost:8000/chat"


def send(user_id, query):
    r = requests.post(URL, json={"query": query, "user_id": user_id}, timeout=90)
    answer = r.json().get("answer") if r.status_code == 200 else f"ERROR {r.status_code}"
    print(f"[{user_id}] YOU: {query}")
    print(f"[{user_id}] BOT: {answer}")
    print("-" * 60)


A = "ilv_ali"
S = "ilv_sara"

send(A, "I want a chatbot for my clinic, please contact me.")
send(S, "I need a voice agent for my salon. Can someone contact me?")
send(A, "Ali Khan")
send(S, "Sara Noor")
send(A, "ali.khan@test.com")
send(S, "sara.noor@test.com")
send(A, "0501111111")
send(S, "0502222222")
send(A, "skip")
send(S, "Around 2000 AED")
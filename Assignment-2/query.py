import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from swarm import Swarm, Agent
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Setup
BASE_URL = os.getenv("PROXY_BASE_URL")
MODEL = "openai/gpt-4.1-mini"
client = Swarm(client=OpenAI(base_url=BASE_URL, api_key="unused"))

# Load vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)


def retrieve_context(query: str, k: int = 5) -> str:
    docs = vectorstore.similarity_search(query, k=k)
    parts = []
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        parts.append(f"[{src}, p.{page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def make_agent(name: str, role: str) -> Agent:
    return Agent(
        name=name,
        model=MODEL,
        instructions=(
            f"You are {name}. {role}\n\n"
            "Use ONLY the provided context to answer. "
            "Cite the document filename and page number for every claim."
        ),
    )


methods_agent = make_agent(
    "Methods Analyst",
    "You answer questions about methods, experimental setup, datasets, and evaluation metrics.",
)
results_agent = make_agent(
    "Results Extractor",
    "You answer questions about results, numbers, ablation studies, and comparisons between approaches.",
)
skeptical_agent = make_agent(
    "Skeptical Reviewer",
    "You answer questions about limitations, threats to validity, weaknesses, and critique.",
)
general_agent = make_agent(
    "General Synthesizer",
    "You answer general questions, summarize findings, and synthesize information across papers.",
)


def transfer_to_methods():
    """Transfer to the Methods Analyst for questions about methods, setup, datasets, or metrics."""
    return methods_agent


def transfer_to_results():
    """Transfer to the Results Extractor for questions about results, numbers, ablations, or comparisons."""
    return results_agent


def transfer_to_skeptical():
    """Transfer to the Skeptical Reviewer for questions about limitations, threats, or critique."""
    return skeptical_agent


def transfer_to_general():
    """Transfer to the General Synthesizer for general or broad questions."""
    return general_agent


router_agent = Agent(
    name="Router",
    model=MODEL,
    instructions=(
        "You are a router agent. Based on the user's question, hand off to the best specialist:\n"
        "- Methods Analyst: methods, setup, datasets, metrics\n"
        "- Results Extractor: results, numbers, ablations, comparisons\n"
        "- Skeptical Reviewer: limitations, threats, weaknesses, critique\n"
        "- General Synthesizer: anything else\n\n"
        "Call the appropriate transfer function immediately. Do not answer yourself."
    ),
    functions=[transfer_to_methods, transfer_to_results, transfer_to_skeptical, transfer_to_general],
)


def main():
    print("RAG Literature Assistant (type 'quit' to exit)\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break

        context = retrieve_context(question)
        augmented = f"Context:\n{context}\n\nQuestion: {question}"

        response = client.run(agent=router_agent, messages=[{"role": "user", "content": augmented}])

        print(f"\n[{response.agent.name}]")
        print(response.messages[-1]["content"])
        print()


if __name__ == "__main__":
    main()

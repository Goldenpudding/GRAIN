import json
import os
import random
import re
import string
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
import numpy as np
import openai
import pandas
import joblib
from dotenv import load_dotenv
from openai import OpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from prompts import task_decomposition_prompt, task_revision_prompt, task_solution_prompt, answer_match_prompt
from fewshots import TASK_DECOMPOSITION_EXAMPLES, TASK_REVISION_EXAMPLES, TASK_SOLUTION_EXAMPLES
from llm import AnyOpenAILLM


load_dotenv()
url = os.getenv("base_url")
api = os.getenv("api_key")
llm_model = os.getenv("model")


def llm(query, system="You are a knowledgeable personal assistant, please answer the following questions as a personal assistant (do not use Markdown format)", num_choices=1, temperature=0., port=8003):
    if isinstance(port, int):
        base_url = url
        api_key = api
        messages = [
            {
                "role": "system",
                "content": f"""{system}"""
            },
            {
                "role": "user",
                "content": f"""{query}"""
            }
        ]
        try:
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
            completion = client.chat.completions.create(
                model=llm_model,
                messages=messages,
                extra_body={"stop_token_ids": [151643, 151645]},
                n=num_choices,
                temperature=temperature,
                max_tokens=6000,
             )
            if num_choices > 1:
                return [completion.choices[i].message.content for i in range(num_choices)]
            else:
                return completion.choices[0].message.content
        except Exception as e:
            print(e)


def evaluator(query, system="You are a knowledgeable personal assistant, please answer the following questions as a personal assistant (do not use Markdown format)", num_choices=1, temperature=0., port=8004):
    if isinstance(port, int):
        base_url = f"http://localhost:8004/v1"
        api_key = "sk-bff10ae47d9sand2b1bf7f9dcf0c98a"
        messages = [
            {
                "role": "system",
                "content": f"""{system}"""
            },
            {
                "role": "user",
                "content": f"""{query}"""
            }
        ]
        try:
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
            completion = client.chat.completions.create(
                model='Qwen-72B',
                messages=messages,
                extra_body={"stop_token_ids": [151643, 151645]},
                n=num_choices,
                temperature=temperature,
                max_tokens=6000,
             )
            if num_choices > 1:
                return [completion.choices[i].message.content for i in range(num_choices)]
            else:
                return completion.choices[0].message.content
        except Exception as e:
            print(e)


def extract_plan(text):
    t = text if text is not None else ""
    pattern = r"(Plan:\s*(?:Step\s*\d+:\s*.+(?:\n|$))*)"
    match = re.search(pattern, t, re.DOTALL)
    if match:
        return match.group(0).strip()
    return t


def extract_revised_plan(text):
    t = text if text is not None else ""
    pattern = r"(Revised Plan:\s*(?:Step\s*\d+:\s*.+(?:\n|$))*)"
    match = re.search(pattern, t, re.DOTALL)
    if match:
        return match.group(0).strip()
    return t


def extract_answer(text):
    t = text if text is not None else ""
    pattern = r"Finish\[(.*?)\]"
    matches = re.findall(pattern, t, re.DOTALL)
    return matches[-1] if matches else t


def normalize_answer(s):
    s = "" if s is None else str(s)

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def test(question, related_context, answer):
    task_decomposition_text = task_decomposition_prompt.format(
        examples=TASK_DECOMPOSITION_EXAMPLES,
        question=question,
    )
    plan_result = llm(task_decomposition_text)
    plan = extract_plan(plan_result)

    task_revision_text = task_revision_prompt.format(
        examples=TASK_REVISION_EXAMPLES,
        question=question,
        plan=plan,
        knowledge=related_context,
    )
    revision_plan_result = llm(task_revision_text)
    revised_plan = extract_revised_plan(revision_plan_result)

    task_solution_text = task_solution_prompt.format(
        examples=TASK_SOLUTION_EXAMPLES,
        question=question,
        revised_plan=revised_plan,
        knowledge=related_context,
    )
    result_answer = llm(task_solution_text)
    llm_answer = extract_answer(result_answer)

    answer_match_text = answer_match_prompt.format(
        question=question,
        standard_answer=normalize_answer(answer),
        experimental_answer=normalize_answer(llm_answer),
    )
    b = evaluator(answer_match_text)
    b = extract_answer(b)
    return b == "True"


def parse_entity_list(text):
    if text is None:
        return []

    text = text.strip()

    code_block_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if code_block_match:
        text = code_block_match.group(1).strip()

    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return [str(x).strip() for x in obj if str(x).strip()]
    except Exception:
        pass

    bracket_match = re.search(r"\[(.*?)\]", text, re.DOTALL)
    if bracket_match:
        inner = bracket_match.group(1)
        parts = [x.strip().strip("'\"") for x in inner.split(",")]
        return [x for x in parts if x]

    lines = [line.strip("-• \n\r\t") for line in text.splitlines()]
    lines = [line for line in lines if line]
    if len(lines) > 1:
        return lines

    parts = [x.strip() for x in text.split(",")]
    return [x for x in parts if x]


def extract_entities_from_question(question):
    prompt = f"""
You are an information extraction assistant.

Your task is to identify the important named entities in the following question.
Only extract entities that are useful for graph retrieval, such as:
- person names
- place names
- organization names
- event names
- work titles
- specific objects/concepts if they are central to the question

Do not extract generic question words.
Do not explain.
Return ONLY a JSON list of strings.

Question:
{question}
"""
    entity_text = llm(prompt)
    entity_list = parse_entity_list(entity_text)

    seen = set()
    result = []
    for ent in entity_list:
        ent_norm = ent.strip()
        if ent_norm and ent_norm.lower() not in seen:
            seen.add(ent_norm.lower())
            result.append(ent_norm)
    return result


def normalize_text_for_match(text):
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def build_graph_index(triples):
    adjacency = defaultdict(list)

    for triple in triples:
        head = triple.get("head", "")
        relation = triple.get("relation", "")
        tail = triple.get("tail", "")

        if not head or not tail:
            continue

        adjacency[normalize_text_for_match(head)].append(triple)
        adjacency[normalize_text_for_match(tail)].append(triple)

    return adjacency


def find_seed_entities(entity, adjacency):
    entity_norm = normalize_text_for_match(entity)
    seeds = []

    if entity_norm in adjacency:
        seeds.append(entity_norm)

    for node in adjacency.keys():
        if entity_norm in node or node in entity_norm:
            if node not in seeds:
                seeds.append(node)

    return seeds


def graph_retrieval_by_entities(entity_list, triples, depth=2, max_knowledge=30):
    adjacency = build_graph_index(triples)

    visited_nodes = set()
    visited_triples = set()
    collected_triples = []
    queue = deque()

    for entity in entity_list:
        seeds = find_seed_entities(entity, adjacency)
        for seed in seeds:
            if seed not in visited_nodes:
                queue.append((seed, 0))
                visited_nodes.add(seed)

    while queue and len(collected_triples) < max_knowledge:
        current_node, current_depth = queue.popleft()

        if current_depth >= depth:
            continue

        for triple in adjacency.get(current_node, []):
            head = triple.get("head", "")
            relation = triple.get("relation", "")
            tail = triple.get("tail", "")

            triple_key = (
                normalize_text_for_match(head),
                normalize_text_for_match(relation),
                normalize_text_for_match(tail),
            )

            if triple_key not in visited_triples:
                visited_triples.add(triple_key)
                collected_triples.append(triple)

            head_norm = normalize_text_for_match(head)
            tail_norm = normalize_text_for_match(tail)

            for next_node in [head_norm, tail_norm]:
                if next_node not in visited_nodes:
                    visited_nodes.add(next_node)
                    queue.append((next_node, current_depth + 1))

            if len(collected_triples) >= max_knowledge:
                break

    return collected_triples


def triples_to_text(triples, source_name=None):
    lines = []
    for triple in triples:
        head = triple.get("head", "")
        relation = triple.get("relation", "")
        tail = triple.get("tail", "")
        if source_name:
            lines.append(f"[{source_name}] ({head}, {relation}, {tail})")
        else:
            lines.append(f"({head}, {relation}, {tail})")
    return "\n".join(lines)


def retrieve_related_context(question, crg, dkg, depth=2, max_knowledge_per_graph=30):
    entity_list = extract_entities_from_question(question)

    if not entity_list:
        entity_list = [question]

    crg_triples = graph_retrieval_by_entities(
        entity_list=entity_list,
        triples=crg,
        depth=depth,
        max_knowledge=max_knowledge_per_graph,
    )

    dkg_triples = graph_retrieval_by_entities(
        entity_list=entity_list,
        triples=dkg,
        depth=depth,
        max_knowledge=max_knowledge_per_graph,
    )

    crg_text = triples_to_text(crg_triples, source_name="CRG")
    dkg_text = triples_to_text(dkg_triples, source_name="DKG")

    related_context = (
        f"Question Entities: {entity_list}\n\n"
        f"Knowledge from CRG:\n{crg_text}\n\n"
        f"Knowledge from DKG:\n{dkg_text}"
    )
    return related_context

def process_sample(row, data, crg, dkg, depth=3):
    try:
        question = data[row]["question"]
        related_context = retrieve_related_context(question, crg, dkg, depth=depth)
        answer = data[row]["answer"]
        result = test(question, related_context, answer)
        return result
    except Exception as e:
        print(f"Error processing row {row}: {e}")
        return False


def parallel_test(data, test_list, crg, dkg, max_workers=4, depth=3):
    count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_row = {
            executor.submit(process_sample, row, data, crg, dkg, depth): row
            for row in test_list
        }
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            try:
                result = future.result()
                if result:
                    count += 1
            except Exception as e:
                print(f"Row {row} generated an exception: {e}")
    return count


data_name_list = ["2wiki", "hotpotqa", "musique"]
data_path_list = [
    "dataset/2wikimultihopqa.json",
    "dataset/hotpotqa.json",
    "dataset/musique.json",
]
CRG_path_list = [
    "CRG/2wiki.json",
    "CRG/hotpotqa.json",
    "CRG/musique.json",
]
DKG_path_list = [
    "DKG/2wiki.json",
    "DKG/hotpotqa.json",
    "DKG/musique.json",
]


for data_choose in range(3):
    data_name = data_name_list[data_choose]
    data_path = data_path_list[data_choose]
    CRG_path = CRG_path_list[data_choose]
    DKG_path = DKG_path_list[data_choose]

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(CRG_path, "r", encoding="utf-8") as f:
        crg = json.load(f)

    with open(DKG_path, "r", encoding="utf-8") as f:
        dkg = json.load(f)

    data_num = len(data)
    random.seed(2025)

    test_num = data_num
    test_list = random.sample(range(data_num), test_num)

    count = parallel_test(data, test_list, crg, dkg, max_workers=20, depth=2)
    ACC = count / test_num if test_num > 0 else 0
    print(ACC)
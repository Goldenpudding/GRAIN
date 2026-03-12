from langchain.prompts import PromptTemplate

## 任务分解prompt
TASK_DECOMPOSITION_TEMPLATE = """Let's begin by understanding the task, extracting the relevant variables along with their corresponding numerals, and following the format provided in the subsequent examples to break down this task into a complete plan(Please respond in plain text only, without any markdown formatting or symbols like #, *, or backticks).
Here are some examples:
{examples}
(END OF EXAMPLES)

Question: {question}"""


## 任务修正prompt
TASK_REVISION_TEMPLATE = """You will be given a previous plan which was developed to solve the following problem. Please draw on your knowledge and the provided knowledge base to analyze whether there are any errors in this plan. If there are errors or areas for improvement, analyze the possible reasons for its shortcomings and propose a new, concise, and high-level plan aimed at avoiding the same mistakes. Your revised plan should be more efficient or accurate, addressing any flaws or missing steps from the original(Please respond in plain text only, without any markdown formatting or symbols like #, *, or backticks). 
Here are some examples:
{examples}
(END OF EXAMPLES)

Question: {question}
Previous Plan: {plan}
Knowledge: {knowledge}
"""


## 任务解答prompt
TASK_SOLUTION_TEMPLATE = """You are an advanced agent.revised plan and you will be given the previous revised plan. Then, let's carry out the plan, calculate intermediate variables (pay attention to correct numerical calculation and commonsense), solve the problem step by step. Finish[answer] returns the answer and finishes the task. You will be given context that you should use to help you answer the question(Please respond in plain text only, without any markdown formatting or symbols like #, *, or backticks).
Here are some examples:
{examples}
(END OF EXAMPLES)

Question: {question}
Reivised Plan: {revised_plan}
Relevant Context: {knowledge}
"""


## 答案匹配prompt
ANSWER_MATCH_TEMPLATE = """You are an advanced Agent. I will provide you with a question, along with a standard answer and an experimental answer. Your task is to perform a fuzzy match between the two answers. If the experimental answer is within an acceptable range and effectively equivalent to the standard answer, return Finish[True]. If the experimental answer is not within an acceptable range or does not effectively match the standard answer, return Finish[False].

Question: {question}
Standard Answer: {standard_answer}
Experimental Answer: {experimental_answer}
"""


task_decomposition_prompt = PromptTemplate(
    input_variables=["examples", "question"],
    template=TASK_DECOMPOSITION_TEMPLATE,
)


task_revision_prompt = PromptTemplate(
    input_variables=["examples", "question", "plan", "knowledge"],
    template=TASK_REVISION_TEMPLATE,
)


task_solution_prompt = PromptTemplate(
    input_variables=["examples", "question", "revised_plan", "knowledge"],
    template=TASK_SOLUTION_TEMPLATE,
)


answer_match_prompt = PromptTemplate(
    input_variables=['question', 'standard_answer', 'experimental_answer'],
    template=ANSWER_MATCH_TEMPLATE,
)
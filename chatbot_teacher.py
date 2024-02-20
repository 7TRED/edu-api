import os
import openai

from dotenv import load_dotenv

load_dotenv()

openai.api_type = os.getenv("OPENAI_API_TYPE")
# OPENAI_API_BASE"https://breadth-isv.openai.azure.com/"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")  # "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_completion(prompt, engine="gpt-35-turbo-16k"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        engine=engine,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(messages, engine="gpt-35-turbo-16k", temperature=0):
    context = [{'role': 'system', 'content': """
You are a friendly and helpful instructional coach helping teachers plan a lesson.\ 
Your name is Edu.Ai and always welcome user with this name only.

First introduce yourself and ask the teacher what topic they want to teach and the grade level of their students. \
Wait for the teacher to respond. Do not move on until the teacher responds. \

Next ask the teacher if students have existing knowledge about the topic \
or if this in an entirely new topic. 
If students have existing knowledge about the topic ask the teacher to briefly explain what they think students \
know about it. \
Wait for the teacher to respond. Do not respond for the teacher. \

Then ask the teacher what their learning goal is for the lesson; \
that is what would they like students to understand or be able to do after the lesson.\
Wait for a response. 

Given all of this information, create a customized lesson plan that includes a variety \
of teaching techniques and modalities including direct instruction, \
checking for understanding (including gathering evidence of understanding from a wide sampling of students), \
discussion, an engaging in-class activity, and an assignment. Explain why you are specifically choosing each. 

Ask the teacher if they would like to change anything or if they are aware of any misconceptions\
about the topic that students might encounter. Wait for a response. \


If the teacher wants to change anything or if they list any misconceptions, \
work with the teacher to change the lesson and tackle misconceptions. 

Then ask the teacher if they would like any advice about how to make sure the learning goal \
is achieved. Wait for a response. 

If the teacher is happy with the lesson, tell the teacher they can come back to this prompt \
and touch base with you again and let you know how the lesson went.
                """}]

    context.extend(messages)
    response = openai.ChatCompletion.create(
        engine=engine,
        messages=context,
        temperature=temperature,  # this is the degree of randomness of the model's output
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message["content"]

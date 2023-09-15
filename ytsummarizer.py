

import os
import openai
import json
import re
from time import time, sleep
from urllib.parse import urlparse, parse_qs
import textwrap
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from dotenv import load_dotenv

load_dotenv()

# OPENAI_API_BASE"https://breadth-isv.openai.azure.com/"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")  # "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = os.getenv("OPENAI_API_TYPE")


def get_transcript(url):
    url_data = urlparse(url)
    video_id = parse_qs(url_data.query)["v"][0]
    if not video_id:
        print('Video ID not found.')
        return None

    try:
        formatter = TextFormatter()

        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en'])
        text = formatter.format_transcript(transcript)
        text = re.sub('\s+', ' ', text).replace('--', '')
        # print(text)
        return video_id, text

    except Exception as e:
        print('Error downloading transcript:', e)
        return None


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, model='text-davinci-003', engine="text-davinci-003", temp=0.5, top_p=1.0, tokens=500, freq_pen=0.25, pres_pen=0.0, stop=['\n']):
    max_retry = 3
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                model=model,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            # print(text)
            if not text:
                retry += 1
                continue
            return text

        except Exception as e:
            retry += 1
            if retry >= max_retry:
                return "Oops, something went wrong"
            print('Error communicating with OpenAI:', e)
            sleep(1)


def ask_gpt(text, prompt_file, output_file, job='SUMMARY'):
    # Summarize chunks
    chunks = textwrap.wrap(text, width=10000)
    results = list()
    for i, chunk in enumerate(chunks):
        prompt = open_file(prompt_file).replace('<<CONTENT>>', chunk)
        prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
        output = ''
        if job == 'SUMMARY':
            output = gpt3_completion(prompt, tokens=500)
        elif job == 'REWRITE':
            output = gpt3_completion(prompt, tokens=2048)
        results.append(output)
        print(f'{i+1} of {len(chunks)}\n{output}\n\n\n')

    return results


def generate_summary(url):
    try:
        # Download transcript
        video_id, text = get_transcript(url)
        summary = ""
        # Summarize the transcript (chunk by chunk if needed)
        if text:
            # Summarize transcript
            output_file = f'summary_{video_id}_{time()}.txt'
            results = ask_gpt(text, 'prompt_summary.txt', 'SUMMARY')
            summary = '\n\n'.join(results)
            # save_file(summary, output_file)

            # Summarize the summary
            if len(results) > 1:
                summary = "".join(
                    ask_gpt(summary, 'prompt_rewrite.txt', 'REWRITE'))
                # save_file('\n\n'.join(new_summary),
                #           output_file.replace('.txt', '_2.txt'))

            print('----- YT Summary Done -----')
            return summary

    except Exception as e:
        return f"Could not retrieve a transcript for the video {url}"


if __name__ == "__main__":
    print(generate_summary("https://www.youtube.com/watch?v=4Stzj2_Rlo4"))

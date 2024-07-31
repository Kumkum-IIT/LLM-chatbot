from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
from django.views.decorators.csrf import csrf_exempt
import json
# from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
# from openai import Completion
from openai import OpenAI
from django.http import StreamingHttpResponse
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get("OPENAI_API_KEY")

@csrf_exempt
def chatbot_view(request):
    return render(request, 'chatbot.html')

# webkitSpeechRecognition

@csrf_exempt  # Disable CSRF for this view, adjust as needed for production
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('chat_input')
            skill = data.get('skill')
            # preferred_genre = data.get('genre')
            # ott_platform = data.get('ottPlatform')
            # language = data.get('language')
            # print(ott_platform)

            prompt = f"""
            1. Your name is Luna and you're an AI assistant for helping users to respond with sports queries.
            2. If user asks anything related to any sports,respond with that sports question only.
            3. Give name of the players related to the sports.
            4. Don't respond anything outside sports domain. If users asks something which is not related sports, reply with I don't have information.
            """

        except KeyError:
            return JsonResponse({'error': 'Invalid input format'}, status=400)

        try:
            # from openai import OpenAI
            def event_stream():
                client = OpenAI(api_key=API_KEY)
                stream = client.chat.completions.create(model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "sports detailed description: "+user_input+"specific sports skill: "+skill}
                ],
                temperature=1,
                max_tokens=2048,
                stream=True,)
                # content = response.choices[0].message.content

                # return JsonResponse({'content': content})

                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

            return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)


    return JsonResponse({'error': 'Method not allowed'}, status=405)


#     response = Completion.create(
#         model="text-davinci-003",
#         prompt=messages,
#         temperature=1,
#         max_tokens=256,
#         top_p=1,
#         frequency_penalty=0,
#         presence_penalty=0
#     )

# response = requests.post(
#                 url="https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": "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",
#                 },
#                 json={
#                     "model": "mistralai/mistral-7b-instruct:free",
#                     "messages": [{'role': 'user', 'content': prompt},
#                                 {'role': 'user', 'content': user_input}],
#                     "temperature": 0.1
#                 }
#             )

# test=[]
            # def generate_response():
            #     full_response = " "
            #     for chunk in response:
            #         chunk_message = chunk.choices[0].delta.content
            #         content = chunk_message
            #         if chunk_message is None:
            #             test.append(chunk_message)
            #             break
            #         full_response +=content
            #         yield chunk_message

            # # use Django's StreamingHttpResponse to send the response messages as a stream to the frontend
            # return StreamingHttpResponse(generate_response(), headers={'X-Accel-Buffering': 'no'})
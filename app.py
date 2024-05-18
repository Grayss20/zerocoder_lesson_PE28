from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests

app = FastAPI()

openai.api_key = os.environ["OPENAI_API_KEY"]

class Topic(BaseModel):
    topic: str

def get_recent_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey=YOUR_NEWS_API_KEY"
    response = requests.get(url)
    articles = response.json()["articles"]
    recent_news = [article["title"] for article in articles[:3]]
    return "\n".join(recent_news)

def generate_post(topic):
    recent_news = get_recent_news(topic)

    prompt_title = f"Придумайте привлекательный заголовок для поста на тему: {topic}"
    response_title = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_title}],
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    title = response_title.choices[0].message.content.strip()

    prompt_meta = f"Напишите краткое, но информативное мета-описание для поста с заголовком: {title}"
    response_meta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_meta}],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    meta_description = response_meta.choices[0].message.content.strip()

    prompt_post = f"Напишите подробный и увлекательный пост для блога на тему: {topic}, учитывая следующие последние новости:\n{recent_news}\n\nИспользуйте короткие абзацы, подзаголовки, примеры и ключевые слова для лучшего восприятия и SEO-оптимизации."
    response_post = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_post}],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    post_content = response_post.choices[0].message.content.strip()

    return {
        "title": title,
        "meta_description": meta_description,
        "post_content": post_content
    }

@app.post("/generate-post")
async def generate_post_api(topic: Topic):
    generated_post = generate_post(topic.topic)
    return generated_post

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

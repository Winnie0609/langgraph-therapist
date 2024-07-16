from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
# openai_api_key = os.environ["OPENAI_API_KEY"]


def get_open_ai_model(temperature=0, model="gpt-3.5-turbo"):
    """
    Retrieves an OpenAI model with the specified temperature and model type.

    Args:
        temperature (float): The temperature setting for the model, from 0-2.
        model (str): The model type (e.g., "gpt-3.5-turbo", "gpt-4o").

    Returns:
        ChatOpenAI: An instance of the ChatOpenAI class configured with the specified parameters.
    """

    llm = ChatOpenAI(
        model=model, temperature=temperature, openai_api_key=openai_api_key
    )
    return llm


def get_open_ai_json(temperature=0, model="gpt-3.5-turbo"):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        model_kwargs={"response_format": {"type": "json_object"}},
        openai_api_key=openai_api_key,
    )
    return llm

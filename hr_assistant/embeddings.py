from langchain_community.embeddings import JinaEmbeddings

from hr_assistant import config


def get_embeddings_model():
    """Return a Jina embeddings model. Reads JINA_API_KEY from the environment."""
    return JinaEmbeddings(
        jina_api_key=config.JINA_API_KEY,
        model_name=config.EMBEDDING_MODEL_NAME,
    )
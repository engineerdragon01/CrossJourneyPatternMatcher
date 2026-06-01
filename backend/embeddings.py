import os

import numpy as np
import voyageai


def embed(texts: list[str]) -> np.ndarray:
    """Embed a list of strings → float32 numpy array (N, D).

    Swap implementation: replace this function body with the OpenAI block below
    and set OPENAI_API_KEY instead of VOYAGE_API_KEY.

    # OpenAI alternative:
    # from openai import OpenAI
    # client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    # return np.array([d.embedding for d in resp.data], dtype=np.float32)
    """
    client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
    result = client.embed(texts, model="voyage-3", input_type="document")
    return np.array(result.embeddings, dtype=np.float32)
